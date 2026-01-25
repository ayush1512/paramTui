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
    # if output:
    #     table = Table(title="🖧 Node Availability", box=box.ROUNDED)
    #     table.add_column("Partition", style="cyan")
    #     table.add_column("Avail", style="green")
    #     table.add_column("Time Limit", style="yellow")
    #     table.add_column("Nodes", justify="right")
    #     table.add_column("State", style="magenta")
    #     table.add_column("Node List", style="dim")
        
    #     lines = output.strip().split('\n')[1:]
    #     for line in lines:
    #         parts = line.split()
    #         if len(parts) >= 6:
    #             table.add_row(*parts[:6])
        
    #     console.print(table)
    #     return True
        return False


# def resource_load_average(ssh_conn):
#     """Get system load average."""
#     output = ssh_conn.execute_command("uptime && cat /proc/loadavg")
#     if output:
#         console.print(Panel(output, title="📈 Load Average", border_style="cyan"))
#         return True
#     return False


# def resource_network_usage(ssh_conn):
#     """Get network usage statistics."""
#     output = ssh_conn.execute_command("netstat -i 2>/dev/null || ip -s link")
#     if output:
#         console.print(Panel(output, title="🌐 Network Usage", border_style="blue"))
#         return True
#     return False


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


# def quota_compute_usage(ssh_conn):
#     """Get compute (CPU/GPU hours) usage."""
#     output = ssh_conn.execute_command("""
#         sacct -u $USER --start=$(date -d '30 days ago' +%Y-%m-%d) -o JobID,JobName,Elapsed,CPUTime,AllocCPUS -n 2>/dev/null | head -30
#     """)
#     if output:
#         console.print("[bold cyan]📊 Compute Usage (Last 30 days):[/bold cyan]")
#         console.print(output)
        
#         summary = ssh_conn.execute_command("sreport user topusage start=$(date -d '30 days ago' +%Y-%m-%d) 2>/dev/null | head -20")
#         if summary:
#             console.print("\n[bold cyan]Usage Summary:[/bold cyan]")
#             console.print(summary)
#         return True
#     return False


# def quota_check_warnings(ssh_conn):
#     """Check for quota warnings."""
#     disk_output = ssh_conn.execute_command("quota -s 2>/dev/null | grep -E '[0-9]+%'")
#     warnings = []
    
#     if disk_output:
#         try:
#             for word in disk_output.split():
#                 if '%' in word:
#                     pct = int(word.replace('%', ''))
#                     if pct > 80:
#                         warnings.append("⚠️ Disk usage above 80%!")
#                         break
#         except:
#             pass
    
#     if warnings:
#         for w in warnings:
#             console.print(f"[bold yellow]{w}[/bold yellow]")
#     else:
#         console.print("[bold green]✓ No quota warnings[/bold green]")
    
#     return warnings

