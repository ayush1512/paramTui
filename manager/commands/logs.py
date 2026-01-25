"""Log management commands."""

from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel

from manager.commands.files import file_download

console = Console()


def logs_get_session_history(ssh_conn, lines=50):
    """Get SSH session history."""
    output = ssh_conn.execute_command(f"last -n {lines} $USER || last -n {lines}")
    if output:
        console.print(Panel(output, title="📋 Session History", border_style="cyan"))
        return True
    return False


def logs_get_job_submission_history(ssh_conn, days=7):
    """Get job submission history."""
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    output = ssh_conn.execute_command(f"sacct -u $USER -S {start_date} -o JobID,JobName,Submit,Start,End,State | head -50")
    if output:
        console.print(Panel(output, title=f"📝 Job Submission History (Last {days} days)", border_style="green"))
        return True
    return False


def logs_get_error_logs(ssh_conn, pattern="*.err"):
    """Find and list recent error logs."""
    output = ssh_conn.execute_command(f"find ~ -name '{pattern}' -mtime -7 -type f  | head -20")
    if output:
        console.print("[bold cyan]📋 Recent Error Logs:[/bold cyan]")
        for log in output.strip().split('\n'):
            if log:
                console.print(f"  📄 {log}")
        return output.strip().split('\n')
    console.print("[yellow]No recent error logs found.[/yellow]")
    return []

