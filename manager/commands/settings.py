"""User settings commands."""

from rich.console import Console
from rich.panel import Panel

console = Console()


def settings_get_profile(ssh_conn):
    """Get user profile information."""
    output = ssh_conn.execute_command("""
        echo "Username: $USER"
        echo "Home: $HOME"
        echo "Shell: $SHELL"
        echo "Groups: $(groups)"
        echo "UID: $(id -u)"
        echo "GID: $(id -g)"
    """)
    if output:
        console.print(Panel(output, title="👤 User Profile", border_style="cyan"))
        return True
    return False


def settings_list_ssh_keys(ssh_conn):
    """List SSH keys."""
    output = ssh_conn.execute_command("ls -la ~/.ssh/")
    if output:
        console.print(Panel(output, title="🔐 SSH Keys", border_style="green"))
        return True
    console.print("[yellow]No SSH keys found.[/yellow]")
    return False


def settings_get_default_shell(ssh_conn):
    """Get default shell."""
    output = ssh_conn.execute_command("echo $SHELL && cat /etc/shells")
    if output:
        console.print(Panel(output, title="🐚 Shell Configuration", border_style="cyan"))
        return True
    return False


def settings_get_conda_config(ssh_conn):
    """Get Conda configuration."""
    output = ssh_conn.execute_command("conda config --show | head -30")
    if output:
        console.print(Panel(output, title="🐍 Conda Configuration", border_style="green"))
        return True
    return False
