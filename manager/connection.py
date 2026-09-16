"""SSH Connection management module using Paramiko."""

import getpass
import os
import posixpath
import shutil
import socket
import stat
import sys
import threading
import time
import paramiko
import questionary
from rich.console import Console

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

AUTH_STYLE = questionary.Style([
    ("qmark", "fg:#673ab7 bold"),
    ("question", "bold"),
    ("answer", "fg:#f44336 bold"),
    ("pointer", "fg:#673ab7 bold"),
    ("highlighted", "fg:#673ab7 bold"),
    ("selected", "fg:#cc5454"),
    ("instruction", "fg:#808080"),
])

console = Console()


class SSHConnection:
    """Manages SSH connection to remote server using Paramiko with multi-step auth."""

    def __init__(self):
        self.host = None
        self.user = None
        self.port = None
        self.connected = False
        self.client = None
        self.transport = None
        self._sftp = None
        self.control_path = None

    def connect(self, host, user, port):
        """Establish SSH connection supporting puzzle, OTP, and password authentication."""
        try:
            self.host = host
            self.user = user
            self.port = int(port) if port else 22

            console.print(f"[bold yellow]Connecting to {self.user}@{self.host}:{self.port}...[/bold yellow]")
            console.print("[dim]Establishing connection...[/dim]\n")

            # Initialize Paramiko SSHClient
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Create direct socket connection
            try:
                sock = socket.create_connection((self.host, self.port), timeout=20)
            except (socket.timeout, socket.error) as e:
                console.print(f"[bold red]✗ Network connection failed:[/bold red] {str(e)}")
                self.connected = False
                return False

            self.transport = paramiko.Transport(sock)
            self.transport.start_client(timeout=20)

            # Check supported authentication methods
            allowed_types = []
            try:
                self.transport.auth_none(self.user)
            except paramiko.BadAuthenticationType as e:
                allowed_types = e.allowed_types or []
            except Exception:
                allowed_types = []

            # Check if auth_none unexpectedly succeeded
            if self.transport.is_authenticated():
                self._finish_connection()
                return True

            console.print("[bold cyan]Please complete authentication:[/bold cyan]")

            authenticated = False

            # Try publickey auth if offered and standard key files exist
            if "publickey" in allowed_types:
                key_paths = [
                    os.path.expanduser("~/.ssh/id_rsa"),
                    os.path.expanduser("~/.ssh/id_ed25519"),
                    os.path.expanduser("~/.ssh/id_ecdsa"),
                ]
                for kp in key_paths:
                    if os.path.exists(kp):
                        try:
                            pkey = None
                            for key_cls in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey):
                                try:
                                    pkey = key_cls.from_private_key_file(kp)
                                    break
                                except Exception:
                                    continue
                            if pkey:
                                self.transport.auth_publickey(self.user, pkey)
                                if self.transport.is_authenticated():
                                    authenticated = True
                                    break
                        except Exception:
                            pass

            # Primary MFA / challenge-response: keyboard-interactive (CDAC puzzle, OTP, password)
            if not authenticated and ("keyboard-interactive" in allowed_types or not allowed_types):
                try:
                    self.transport.auth_interactive(self.user, self._interactive_auth_handler)
                    if self.transport.is_authenticated():
                        authenticated = True
                except paramiko.BadAuthenticationType:
                    pass
                except paramiko.AuthenticationException as e:
                    console.print(f"[bold red]✗ Authentication failed:[/bold red] {str(e)}")
                    self.disconnect()
                    return False

            # Fallback to standard password auth if keyboard-interactive wasn't used/accepted
            if not authenticated and "password" in allowed_types:
                try:
                    pwd = self._safe_prompt("Enter Password:", echo=False)
                    if pwd:
                        self.transport.auth_password(self.user, pwd)
                        if self.transport.is_authenticated():
                            authenticated = True
                except paramiko.AuthenticationException as e:
                    console.print(f"[bold red]✗ Password authentication failed:[/bold red] {str(e)}")
                    self.disconnect()
                    return False

            if authenticated and self.transport.is_authenticated():
                self._finish_connection()
                return True
            else:
                console.print("[bold red]✗ Connection failed: Authentication was not completed[/bold red]")
                self.disconnect()
                return False

        except Exception as e:
            console.print(f"[bold red]✗ Connection failed:[/bold red] {str(e)}")
            self.disconnect()
            return False

    def _finish_connection(self):
        """Finalize authenticated connection and wire SSHClient."""
        self.transport.set_keepalive(30)
        self.client._transport = self.transport
        self.connected = True
        console.print(f"\n[bold green]✓ Successfully connected to {self.user}@{self.host}[/bold green]")
        console.print("[dim]Persistent Paramiko session established[/dim]")

    def _interactive_auth_handler(self, title, instructions, prompt_list):
        """Callback for keyboard-interactive authentication (supports puzzle, OTP, password)."""
        if title and title.strip():
            console.print(f"\n[bold cyan]{title.strip()}[/bold cyan]")
        if instructions and instructions.strip():
            console.print(f"[dim]{instructions.strip()}[/dim]")

        answers = []
        for prompt, echo in prompt_list:
            prompt_text = prompt.strip()
            # If the prompt ends without a colon or question mark, add a colon
            if prompt_text and not prompt_text.endswith((':', '?')):
                display_prompt = f"{prompt_text}:"
            else:
                display_prompt = prompt_text

            ans = self._safe_prompt(display_prompt, echo=echo)
            answers.append(ans)

        return answers

    def _safe_prompt(self, prompt_text, echo=True):
        """Prompt user with questionary or fallback to stdlib."""
        try:
            if echo:
                val = questionary.text(prompt_text, style=AUTH_STYLE).ask()
            else:
                val = questionary.password(prompt_text, style=AUTH_STYLE).ask()
            if val is not None:
                return val
        except Exception:
            pass

        # Fallback to standard input / getpass
        try:
            if echo:
                return input(f"{prompt_text} ")
            else:
                return getpass.getpass(f"{prompt_text} ")
        except Exception:
            return ""

    def execute_command(self, command, timeout=30):
        """Execute a command on the remote server using the persistent connection."""
        if not self.connected or not self.transport or not self.transport.is_active():
            console.print("[bold red]Not connected to any server![/bold red]")
            return None

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            exit_status = stdout.channel.recv_exit_status()
            out_str = stdout.read().decode("utf-8", errors="replace")
            err_str = stderr.read().decode("utf-8", errors="replace")

            if err_str and exit_status != 0:
                console.print(f"[bold red]Error:[/bold red] {err_str.strip()}")

            return out_str

        except (socket.timeout, TimeoutError):
            console.print("[bold red]Command timed out[/bold red]")
            return None
        except Exception as e:
            console.print(f"[bold red]Command execution failed: {str(e)}[/bold red]")
            return None

    def get_sftp(self):
        """Get or initialize active SFTP client."""
        if not self.connected or not self.transport or not self.transport.is_active():
            return None
        try:
            if self._sftp is None or self._sftp.get_channel() is None or self._sftp.get_channel().is_closed():
                self._sftp = self.client.open_sftp()
            return self._sftp
        except Exception as e:
            console.print(f"[bold red]Failed to open SFTP session: {str(e)}[/bold red]")
            return None

    def upload_file(self, local_path, remote_path):
        """Upload a local file to remote destination via SFTP."""
        sftp = self.get_sftp()
        if not sftp:
            console.print("[bold red]SFTP session not available[/bold red]")
            return False

        try:
            # Handle directory destination
            target_path = remote_path
            try:
                rstat = sftp.stat(remote_path)
                if stat.S_ISDIR(rstat.st_mode):
                    target_path = posixpath.join(remote_path, os.path.basename(local_path))
            except IOError:
                pass

            sftp.put(local_path, target_path)
            return True
        except Exception as e:
            console.print(f"[bold red]✗ Upload failed: {str(e)}[/bold red]")
            return False

    def download_file(self, remote_path, local_path):
        """Download a remote file to local destination via SFTP."""
        sftp = self.get_sftp()
        if not sftp:
            console.print("[bold red]SFTP session not available[/bold red]")
            return False

        try:
            target_path = local_path
            if os.path.isdir(local_path):
                target_path = os.path.join(local_path, posixpath.basename(remote_path))

            sftp.get(remote_path, target_path)
            return True
        except Exception as e:
            console.print(f"[bold red]✗ Download failed: {str(e)}[/bold red]")
            return False

    def interactive_shell(self):
        """Launch an interactive shell session using the persistent connection."""
        if not self.connected or not self.transport or not self.transport.is_active():
            console.print("[bold red]Not connected to any server![/bold red]")
            return

        console.print(f"[bold yellow]Starting interactive shell on {self.user}@{self.host}...[/bold yellow]")
        console.print("[dim]Type 'exit' to return to Console Manager[/dim]\n")

        try:
            chan = self.transport.open_session()
            size = shutil.get_terminal_size((80, 24))
            chan.get_pty(term="xterm-256color", width=size.columns, height=size.lines)
            chan.invoke_shell()
            self._bridge_terminal_io(chan)
        except Exception as e:
            console.print(f"[bold red]Shell session error: {str(e)}[/bold red]")

    def run_interactive_command(self, command):
        """Run an interactive command with PTY (e.g. nano, srun --pty)."""
        if not self.connected or not self.transport or not self.transport.is_active():
            console.print("[bold red]Not connected to any server![/bold red]")
            return

        try:
            chan = self.transport.open_session()
            size = shutil.get_terminal_size((80, 24))
            chan.get_pty(term="xterm-256color", width=size.columns, height=size.lines)
            chan.exec_command(command)
            self._bridge_terminal_io(chan)
        except Exception as e:
            console.print(f"[bold red]Interactive session error: {str(e)}[/bold red]")

    def _bridge_terminal_io(self, chan):
        """Bridge local terminal I/O with remote SSH channel across Windows and Unix."""
        if sys.platform == "win32":
            import msvcrt

            stop_event = threading.Event()
            special_keys = {
                b"H": b"\x1b[A",  # Up
                b"P": b"\x1b[B",  # Down
                b"M": b"\x1b[C",  # Right
                b"K": b"\x1b[D",  # Left
                b"G": b"\x1b[H",  # Home
                b"O": b"\x1b[F",  # End
                b"S": b"\x1b[3~",  # Delete
                b"R": b"\x1b[2~",  # Insert
                b"I": b"\x1b[5~",  # Page Up
                b"Q": b"\x1b[6~",  # Page Down
            }

            def input_loop():
                while not stop_event.is_set() and not chan.closed:
                    try:
                        if msvcrt.kbhit():
                            ch = msvcrt.getch()
                            if ch in (b"\x00", b"\xe0"):
                                ch2 = msvcrt.getch()
                                seq = special_keys.get(ch2, b"")
                                if seq:
                                    chan.send(seq)
                            else:
                                chan.send(ch)
                        else:
                            time.sleep(0.01)
                    except Exception:
                        break

            t = threading.Thread(target=input_loop, daemon=True)
            t.start()

            try:
                while not chan.closed:
                    if chan.recv_ready():
                        data = chan.recv(4096)
                        if not data:
                            break
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    elif chan.exit_status_ready():
                        while chan.recv_ready():
                            data = chan.recv(4096)
                            if data:
                                sys.stdout.buffer.write(data)
                                sys.stdout.buffer.flush()
                        break
                    else:
                        time.sleep(0.01)
            finally:
                stop_event.set()
                chan.close()
        else:
            import select
            import termios
            import tty

            old_tty = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
                chan.settimeout(0.0)

                while not chan.closed:
                    r, _, _ = select.select([chan, sys.stdin], [], [])
                    if chan in r:
                        try:
                            data = chan.recv(4096)
                            if not data:
                                break
                            sys.stdout.buffer.write(data)
                            sys.stdout.flush()
                        except socket.timeout:
                            pass
                    if sys.stdin in r:
                        data = sys.stdin.read(1)
                        if not data:
                            break
                        chan.send(data)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
                chan.close()

    def disconnect(self):
        """Close SSH connection and cleanup resources."""
        if self._sftp:
            try:
                self._sftp.close()
            except Exception:
                pass
            self._sftp = None

        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None

        if self.transport:
            try:
                self.transport.close()
            except Exception:
                pass
            self.transport = None

        self.connected = False
        console.print("[bold yellow]Disconnected from server.[/bold yellow]")
