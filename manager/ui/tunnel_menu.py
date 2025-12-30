"""SSH Tunnel menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import tunnel


def tunnel_menu(ssh_conn):
    """SSH Tunnel management."""
    console.clear()
    print_header(ssh_conn)
    
    console.print("[bold cyan]🔗 SSH Tunnel Setup[/bold cyan]\n")
    
    tunnel_type = questionary.select(
        "Tunnel type:",
        choices=[
            "🔗 Local Port Forward (access remote service locally)",
            "🔙 Remote Port Forward (expose local service to remote)",
            "← Cancel"
        ],
        style=custom_style
    ).ask()
    
    if tunnel_type == "← Cancel":
        return
    
    remote_port = questionary.text("Remote port:", default="8888", style=custom_style).ask()
    local_port = questionary.text("Local port:", default=remote_port, style=custom_style).ask()
    
    if remote_port:
        tunnel.create_tunnel(ssh_conn, remote_port, local_port if local_port else None)
