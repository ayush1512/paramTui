"""UI styles and common elements."""

import questionary
from questionary import Style
from rich.console import Console

console = Console()

# Custom questionary style for better appearance
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#808080'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


def print_header(ssh_conn=None):
    """Print the application header."""
    header = """
╔═══════════════════════════════════════════════════════════════╗
║            🚀 PARAM - SSH Manager & HPC Console 🚀            ║
╚═══════════════════════════════════════════════════════════════╝"""
    console.print(header, style="bold blue")
    if ssh_conn and ssh_conn.connected:
        console.print(f"  [bold green]✓ Connected:[/bold green] {ssh_conn.user}@{ssh_conn.host}:{ssh_conn.port}", justify="center")
    console.print()
