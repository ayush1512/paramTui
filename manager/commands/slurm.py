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
    output = ssh_conn.execute_command("squeue -u $USER -t RUNNING")
    console.print(output)
    if output is None:
        return False


def job_get_pending(ssh_conn):
    """Get pending jobs with reason."""
    output = ssh_conn.execute_command("squeue -u $USER -t PENDING")
    console.print(output)
    if output is None:
        return False
