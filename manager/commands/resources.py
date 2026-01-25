"""Resource monitoring commands."""

import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def resource_cpu_usage(ssh_conn):
    """Get CPU usage information."""
    output = ssh_conn.execute_command("top -bn1 | head -20")
    if output:
        console.print(Panel(output, title="🖥 CPU Usage", border_style="cyan"))
        return True
    return False


def resource_memory_usage(ssh_conn):
    """Get memory usage information."""
    output = ssh_conn.execute_command("free -h")
    if output:
        console.print(Panel(output, title="🧠 Memory Usage", border_style="green"))
        return True
    return False


def resource_gpu_usage(ssh_conn):
    """Get GPU utilization using nvidia-smi."""
    output = ssh_conn.execute_command("nvidia-smi || echo 'No GPU available or nvidia-smi not found'")
    if output:
        console.print(Panel(output, title="🎮 GPU Utilization", border_style="yellow"))
        return True
    return False


def resource_node_availability(ssh_conn):
    """Get node availability from SLURM."""
    output = ssh_conn.execute_command("sinfo -o '%20P %5a %10l %6D %8t %N'")
    if output is None:
        
        
        return False


def get_remote_system_info(ssh_conn):
    """Get system information from remote server."""
    output = ssh_conn.execute_command("uname -a && df -h && free -h")
    if output:
        console.print("[bold green]Remote System Information:[/bold green]")
        console.print(output)


def quota_disk_usage(ssh_conn):
    """Get disk quota usage."""
    output = ssh_conn.execute_command("lfs quota -h ~ || df -h ~")
    if output:
        console.print(Panel(output, title="💾 Disk Quota", border_style="yellow"))
        return True
    return False

    

