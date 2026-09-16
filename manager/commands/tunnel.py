"""SSH tunnel management commands using Paramiko port forwarding."""

import select
import socketserver
import threading
import time
from rich.console import Console

console = Console()


class _ForwardServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class _ForwardHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.server.ssh_transport.open_channel(
                "direct-tcpip",
                (self.server.chain_host, self.server.chain_port),
                self.request.getpeername(),
            )
        except Exception:
            return

        if chan is None:
            return

        try:
            while True:
                r, _, _ = select.select([self.request, chan], [], [])
                if self.request in r:
                    data = self.request.recv(4096)
                    if not data:
                        break
                    chan.send(data)
                if chan in r:
                    data = chan.recv(4096)
                    if not data:
                        break
                    self.request.send(data)
        except Exception:
            pass
        finally:
            chan.close()
            self.request.close()


def create_tunnel(ssh_conn, remote_port, local_port=None):
    """Create an SSH tunnel (port forwarding) using the persistent Paramiko connection."""
    if not ssh_conn.connected or not ssh_conn.transport or not ssh_conn.transport.is_active():
        console.print("[bold red]Not connected to any server![/bold red]")
        return

    if local_port is None:
        local_port = remote_port

    try:
        remote_port = int(remote_port)
        local_port = int(local_port)
    except ValueError:
        console.print("[bold red]Invalid port number specified.[/bold red]")
        return

    console.print(f"[bold yellow]Creating tunnel: localhost:{local_port} -> {ssh_conn.host}:{remote_port}[/bold yellow]")
    console.print("[dim]Press Ctrl+C to close the tunnel[/dim]\n")

    try:
        server = _ForwardServer(("127.0.0.1", local_port), _ForwardHandler)
        server.ssh_transport = ssh_conn.transport
        server.chain_host = "localhost"
        server.chain_port = remote_port

        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        console.print(f"[bold green]✓ Tunnel active: localhost:{local_port} forwarding to remote port {remote_port}[/bold green]")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Closing tunnel...[/bold yellow]")
            server.shutdown()
            server.server_close()
            console.print("[bold yellow]Tunnel closed.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Tunnel error: {str(e)}[/bold red]")
