"""SLURM job management commands."""

from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def slurm_show_jobs(ssh_conn):
    """Show all SLURM jobs."""
    output = ssh_conn.execute_command("squeue -u $USER")
    if output:
        console.print("[bold green]Your SLURM Jobs:[/bold green]")
        console.print(output)


def slurm_submit_job(ssh_conn, script_path):
    """Submit a SLURM job."""
    output = ssh_conn.execute_command(f"sbatch {script_path}")
    if output:
        console.print("[bold green]Job Submitted:[/bold green]")
        console.print(output)


def slurm_cancel_job(ssh_conn, job_id):
    """Cancel a SLURM job."""
    output = ssh_conn.execute_command(f"scancel {job_id}")
    console.print(f"[bold yellow]Cancelled job {job_id}[/bold yellow]")


def slurm_job_info(ssh_conn, job_id):
    """Get detailed info about a SLURM job."""
    output = ssh_conn.execute_command(f"scontrol show job {job_id}")
    if output:
        console.print(f"[bold green]Job {job_id} Details:[/bold green]")
        console.print(output)


def slurm_nodes_info(ssh_conn):
    """Get details of the nodes."""
    output = ssh_conn.execute_command("sinfo")
    if output:
        console.print(output)


def job_get_running(ssh_conn):
    """Get running jobs with details."""
    output = ssh_conn.execute_command("squeue -u $USER -t RUNNING -o '%.18i %.15j %.8T %.10M %.9l %.6D %.4C %.10m %R'")
    if output is None:
    #     table = Table(title="🏃 Running Jobs", box=box.ROUNDED)
    #     table.add_column("Job ID", style="cyan")
    #     table.add_column("Name", style="green")
    #     table.add_column("State", style="yellow")
    #     table.add_column("Time", style="magenta")
    #     table.add_column("Limit", style="blue")
    #     table.add_column("Nodes", justify="right")
    #     table.add_column("CPUs", justify="right")
    #     table.add_column("Memory", style="yellow")
    #     table.add_column("Node List", style="dim")

    #     lines = [line for line in output.strip().split('\n') if line.strip()]
    #     if len(lines) > 1:
    #         for line in lines[1:]: 
    #             parts = line.split(None, 8)
    #             if len(parts) == 9:
    #                 table.add_row(*parts)
    #         console.print(table)
    #         return True
    # console.print("[yellow]No running jobs found.[/yellow]")
        return False


def job_get_pending(ssh_conn):
    """Get pending jobs with reason."""
    output = ssh_conn.execute_command("squeue -u $USER -t PENDING -o '%.18i %.15j %.8T %.10M %.9l %.6D %.4C %R'")
    if output is None:
    #     table = Table(title="⏳ Pending Jobs", box=box.ROUNDED)
    #     table.add_column("Job ID", style="cyan")
    #     table.add_column("Name", style="green")
    #     table.add_column("State", style="yellow")
    #     table.add_column("Time", style="magenta")
    #     table.add_column("Limit", style="blue")
    #     table.add_column("Nodes", justify="right")
    #     table.add_column("CPUs", justify="right")
    #     table.add_column("Reason", style="red")
        
    #     lines = [line for line in output.strip().split('\n') if line.strip()]
    #     if len(lines) > 1:
    #         for line in lines[1:]: 
    #             parts = line.split(None, 8)
    #             if len(parts) == 9:
    #                 table.add_row(*parts)
    #         console.print(table)
    #         return True
    # console.print("[yellow]No pending jobs found.[/yellow]")
        return False


# def job_get_completed(ssh_conn, days=7):
#     """Get completed jobs from history."""
#     start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
#     output = ssh_conn.execute_command(f"sacct -u $USER -S {start_date} --state=COMPLETED -o JobID,JobName,State,Elapsed,MaxRSS,ExitCode -n | head -30")
#     if output:
#         table = Table(title=f"✅ Completed Jobs (Last {days} days)", box=box.ROUNDED)
#         table.add_column("Job ID", style="cyan")
#         table.add_column("Name", style="green")
#         table.add_column("State", style="green")
#         table.add_column("Elapsed", style="magenta")
#         table.add_column("Max Memory", style="yellow")
#         table.add_column("Exit Code", style="blue")
        
#         for line in output.strip().split('\n'):
#             parts = line.split()
#             if len(parts) >= 6 and not parts[0].endswith('.batch'):
#                 table.add_row(*parts[:6])
        
#         console.print(table)
#         return True
#     console.print("[yellow]No completed jobs found in history.[/yellow]")
#     return False


# def job_get_failed(ssh_conn, days=7):
#     """Get failed jobs from history."""
#     start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
#     output = ssh_conn.execute_command(f"sacct -u $USER -S {start_date} --state=FAILED,CANCELLED,TIMEOUT -o JobID,JobName,State,Elapsed,ExitCode -n   | head -30")
#     if output:
#         table = Table(title=f"❌ Failed/Cancelled Jobs (Last {days} days)", box=box.ROUNDED)
#         table.add_column("Job ID", style="cyan")
#         table.add_column("Name", style="green")
#         table.add_column("State", style="red")
#         table.add_column("Elapsed", style="magenta")
#         table.add_column("Exit Code", style="yellow")
        
#         for line in output.strip().split('\n'):
#             parts = line.split()
#             if len(parts) >= 5 and not parts[0].endswith('.batch'):
#                 table.add_row(*parts[:5])
        
#         console.print(table)
#         return True
#     console.print("[yellow]No failed jobs found in history.[/yellow]")
#     return False


# def job_resource_usage(ssh_conn, job_id):
#     """Get resource usage for a specific job."""
#     output = ssh_conn.execute_command(f"sacct -j {job_id} -o JobID,JobIDRaw,JobName,NTasks,AllocCPUS,Elapsed,State,ExitCode,AveCPUFreq,ReqCPUFreqMin,ReqCPUFreqMax,ReqCPUFreqGov,ReqMem,ConsumedEnergy,ReqTRES -n")
#     if output:
#         console.print(Panel(output, title=f"📊 Resource Usage - Job {job_id}", border_style="cyan"))
#         return True
#     return False


# def job_view_log(ssh_conn, job_id, log_type="out"):
#     """View job output or error log."""
#     output = ssh_conn.execute_command(f"find ~ -name '*{job_id}*.{log_type}' -type f | head -1")
#     if output and output.strip():
#         log_path = output.strip()
#         log_content = ssh_conn.execute_command(f"tail -100 {log_path}")
#         if log_content:
#             console.print(Panel(log_content, title=f"📋 Job {job_id} .{log_type} Log", border_style="green"))
#             return True
#     console.print(f"[yellow]Log file for job {job_id} not found.[/yellow]")
#     return False