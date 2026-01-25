"""Backward compatibility module - imports from new modular structure.

DEPRECATED: This module is kept for backward compatibility.
Please import from manager.connection and manager.commands instead.
"""

from manager.connection import SSHConnection
from manager.templates import JOB_TEMPLATES
from manager.commands.slurm import *
from manager.commands.conda import *
from manager.commands.files import *
from manager.commands.modules import *
from manager.commands.resources import *
from manager.commands.job_templates import *
from manager.commands.logs import *
from manager.commands.settings import *
from manager.commands.help import *
from manager.commands.tunnel import *

import subprocess
import platform
from rich.console import Console
from rich.table import Table

console = Console()


def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            text=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error executing command:[/bold red] {e.stderr}")
        return None


def get_system_info():
    """Returns basic system information."""
    uname = platform.uname()
    table = Table(title="System Information")
    table.add_column("Attribute", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("System", uname.system)
    table.add_row("Node Name", uname.node)
    table.add_row("Release", uname.release)
    table.add_row("Version", uname.version)
    table.add_row("Machine", uname.machine)
    
    console.print(table)


def check_disk_usage():
    """Runs df -h to check disk usage."""
    output = run_command("df -h")
    if output:
        console.print("[bold green]Disk Usage:[/bold green]")
        console.print(output)


def list_files():
    """Runs ls -la to list files in current directory."""
    output = run_command("ls -la")
    if output:
        console.print("[bold green]Directory Contents:[/bold green]")
        console.print(output)


def check_network():
    """Runs ifconfig (or ip a) to check network interfaces."""
    output = run_command("ifconfig")
    if output:
        console.print("[bold green]Network Interfaces:[/bold green]")
        console.print(output)
