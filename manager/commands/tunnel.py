"""SSH tunnel management commands."""

import subprocess
from rich.console import Console

console = Console()


def create_tunnel(ssh_conn, remote_port, local_port=None):
    """Create an SSH tunnel (port forwarding) using the persistent connection."""
    if local_port is None:
        local_port = remote_port
    
    console.print(f"[bold yellow]Creating tunnel: localhost:{local_port} -> {ssh_conn.host}:{remote_port}[/bold yellow]")
    console.print(f"[dim]Press Ctrl+C to close the tunnel[/dim]\n")
    
    try:
        subprocess.run(
            f"ssh -S {ssh_conn.control_path} -L {local_port}:localhost:{remote_port} -N -p {ssh_conn.port} {ssh_conn.user}@{ssh_conn.host}",
            shell=True
        )
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Tunnel closed.[/bold yellow]")
