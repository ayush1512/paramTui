"""Comprehensive unit tests for Paramiko-based SSHConnection and commands."""

import os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import socket
import paramiko

from manager.connection import SSHConnection
from manager.commands.files import file_upload, file_download, file_edit
from manager.commands.job_templates import interactive_gpu_session, interactive_cpu_session
from manager.commands.tunnel import create_tunnel


class TestSSHConnectionInit(unittest.TestCase):
    """Test SSHConnection initialization and default state."""

    def test_init_defaults(self):
        conn = SSHConnection()
        self.assertIsNone(conn.host)
        self.assertIsNone(conn.user)
        self.assertIsNone(conn.port)
        self.assertFalse(conn.connected)
        self.assertIsNone(conn.client)
        self.assertIsNone(conn.transport)
        self.assertIsNone(conn._sftp)
        self.assertIsNone(conn.control_path)


class TestInteractiveAuthHandler(unittest.TestCase):
    """Test keyboard-interactive authentication handler callback."""

    def setUp(self):
        self.conn = SSHConnection()

    @patch.object(SSHConnection, "_safe_prompt")
    def test_interactive_auth_handler(self, mock_prompt):
        # Simulate CDAC prompts: puzzle (echo=True), OTP (echo=True), password (echo=False)
        mock_prompt.side_effect = ["42", "123456", "mysecretpassword"]

        prompts = [
            ("Challenge: What is 40 + 2?", True),
            ("Enter OTP", True),
            ("Password", False),
        ]

        answers = self.conn._interactive_auth_handler(
            title="CDAC HPC Authentication",
            instructions="Please solve challenge and provide credentials",
            prompt_list=prompts,
        )

        self.assertEqual(answers, ["42", "123456", "mysecretpassword"])
        self.assertEqual(mock_prompt.call_count, 3)

        # Verify colon addition for prompt without punctuation
        mock_prompt.assert_any_call("Challenge: What is 40 + 2?", echo=True)
        mock_prompt.assert_any_call("Enter OTP:", echo=True)
        mock_prompt.assert_any_call("Password:", echo=False)


class TestSSHConnectionConnect(unittest.TestCase):
    """Test connect workflow and authentication pathways."""

    def setUp(self):
        self.conn = SSHConnection()

    @patch("socket.create_connection")
    def test_network_failure(self, mock_sock):
        mock_sock.side_effect = socket.error("Connection refused")
        result = self.conn.connect("example.com", "user", 22)
        self.assertFalse(result)
        self.assertFalse(self.conn.connected)

    @patch("manager.connection.paramiko.Transport")
    @patch("socket.create_connection")
    def test_connect_keyboard_interactive_success(self, mock_sock, mock_transport_cls):
        mock_transport = MagicMock()
        mock_transport_cls.return_value = mock_transport

        # auth_none raises BadAuthenticationType with keyboard-interactive
        bad_auth = paramiko.BadAuthenticationType("Allowed types", ["keyboard-interactive"])
        mock_transport.auth_none.side_effect = bad_auth
        # Not authenticated initially, authenticated after auth_interactive
        mock_transport.is_authenticated.side_effect = [False, True, True]

        result = self.conn.connect("paramrudra.cdacdelhi.in", "testuser", "4422")

        self.assertTrue(result)
        self.assertTrue(self.conn.connected)
        self.assertEqual(self.conn.port, 4422)
        mock_transport.auth_interactive.assert_called_once()
        mock_transport.set_keepalive.assert_called_with(30)

    @patch("manager.connection.paramiko.Transport")
    @patch("socket.create_connection")
    def test_connect_password_fallback_success(self, mock_sock, mock_transport_cls):
        mock_transport = MagicMock()
        mock_transport_cls.return_value = mock_transport

        bad_auth = paramiko.BadAuthenticationType("Allowed types", ["password"])
        mock_transport.auth_none.side_effect = bad_auth
        mock_transport.is_authenticated.side_effect = [False, True, True]

        with patch.object(self.conn, "_safe_prompt", return_value="mypassword"):
            result = self.conn.connect("paramrudra.cdacdelhi.in", "testuser", 22)

        self.assertTrue(result)
        self.assertTrue(self.conn.connected)
        mock_transport.auth_password.assert_called_once_with("testuser", "mypassword")

    @patch("manager.connection.paramiko.Transport")
    @patch("socket.create_connection")
    def test_connect_auth_failure(self, mock_sock, mock_transport_cls):
        mock_transport = MagicMock()
        mock_transport_cls.return_value = mock_transport

        bad_auth = paramiko.BadAuthenticationType("Allowed types", ["keyboard-interactive"])
        mock_transport.auth_none.side_effect = bad_auth
        mock_transport.is_authenticated.return_value = False
        mock_transport.auth_interactive.side_effect = paramiko.AuthenticationException("Auth failed")

        result = self.conn.connect("paramrudra.cdacdelhi.in", "testuser", 22)

        self.assertFalse(result)
        self.assertFalse(self.conn.connected)


class TestSSHConnectionExecuteCommand(unittest.TestCase):
    """Test remote command execution."""

    def setUp(self):
        self.conn = SSHConnection()
        self.conn.connected = True
        self.conn.transport = MagicMock()
        self.conn.transport.is_active.return_value = True
        self.conn.client = MagicMock()

    def test_execute_when_disconnected(self):
        self.conn.connected = False
        res = self.conn.execute_command("ls")
        self.assertIsNone(res)

    def test_execute_command_success(self):
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()

        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stdout.read.return_value = b"job1.sh\njob2.sh\n"
        mock_stderr.read.return_value = b""

        self.conn.client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        output = self.conn.execute_command("squeue")
        self.assertEqual(output, "job1.sh\njob2.sh\n")
        self.conn.client.exec_command.assert_called_with("squeue", timeout=30)

    def test_execute_command_with_error(self):
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()

        mock_stdout.channel.recv_exit_status.return_value = 1
        mock_stdout.read.return_value = b""
        mock_stderr.read.return_value = b"squeue: command not found"

        self.conn.client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

        output = self.conn.execute_command("squeue")
        self.assertEqual(output, "")

    def test_execute_command_timeout(self):
        self.conn.client.exec_command.side_effect = socket.timeout("timed out")
        output = self.conn.execute_command("sleep 100")
        self.assertIsNone(output)


class TestSSHConnectionSFTP(unittest.TestCase):
    """Test SFTP file upload and download."""

    def setUp(self):
        self.conn = SSHConnection()
        self.conn.connected = True
        self.conn.transport = MagicMock()
        self.conn.transport.is_active.return_value = True
        self.conn.client = MagicMock()
        self.mock_sftp = MagicMock()
        self.conn.client.open_sftp.return_value = self.mock_sftp

    def test_get_sftp(self):
        sftp = self.conn.get_sftp()
        self.assertEqual(sftp, self.mock_sftp)
        self.conn.client.open_sftp.assert_called_once()

    def test_upload_file(self):
        # Destination is not a directory
        self.mock_sftp.stat.side_effect = IOError("Not found")

        success = self.conn.upload_file("local_script.sh", "/remote/path/script.sh")
        self.assertTrue(success)
        self.mock_sftp.put.assert_called_with("local_script.sh", "/remote/path/script.sh")

    def test_download_file(self):
        success = self.conn.download_file("/remote/output.log", "local_output.log")
        self.assertTrue(success)
        self.mock_sftp.get.assert_called_with("/remote/output.log", "local_output.log")


class TestSSHConnectionDisconnect(unittest.TestCase):
    """Test disconnection and resource cleanup."""

    def test_disconnect(self):
        conn = SSHConnection()
        conn.connected = True
        mock_sftp = MagicMock()
        mock_client = MagicMock()
        mock_transport = MagicMock()

        conn._sftp = mock_sftp
        conn.client = mock_client
        conn.transport = mock_transport

        conn.disconnect()

        self.assertFalse(conn.connected)
        mock_sftp.close.assert_called_once()
        mock_client.close.assert_called_once()
        mock_transport.close.assert_called_once()
        self.assertIsNone(conn._sftp)
        self.assertIsNone(conn.client)
        self.assertIsNone(conn.transport)


class TestCommandsIntegration(unittest.TestCase):
    """Test command helpers calling SSHConnection without subprocess/scp."""

    def setUp(self):
        self.conn = MagicMock(spec=SSHConnection)
        self.conn.connected = True

    def test_file_upload_command(self):
        self.conn.upload_file.return_value = True
        res = file_upload(self.conn, "test.py", "~/test.py")
        self.assertTrue(res)
        self.conn.upload_file.assert_called_with("test.py", "~/test.py")

    def test_file_download_command(self):
        self.conn.download_file.return_value = True
        res = file_download(self.conn, "~/test.py", "test.py")
        self.assertTrue(res)
        self.conn.download_file.assert_called_with("~/test.py", "test.py")

    def test_file_edit_command(self):
        file_edit(self.conn, "~", "test.txt")
        self.conn.run_interactive_command.assert_called_with("nano ~/test.txt")

    def test_interactive_gpu_session_command(self):
        interactive_gpu_session(self.conn, num_gpus=2, time="01:00:00", mem="32G")
        self.conn.run_interactive_command.assert_called_with(
            "srun --gres=gpu:2 --time=01:00:00 --mem=32G --pty bash"
        )

    def test_interactive_cpu_session_command(self):
        interactive_cpu_session(self.conn, num_cpus=1, time="01:00:00", core="20")
        self.conn.run_interactive_command.assert_called_with(
            "srun --partition=cpu -N 1 --time=01:00:00 -c 20 --pty bash"
        )

    def test_create_tunnel_not_connected(self):
        self.conn.connected = False
        self.conn.transport = None
        # Should cleanly return without crashing
        create_tunnel(self.conn, 8888, 8888)


if __name__ == "__main__":
    unittest.main()
