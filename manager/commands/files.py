"""File management commands."""

import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

console = Console()


def file_browse_directory(ssh_conn, path="~"):
    """Browse a directory and show files with details."""
    cmd = f"ls -la {path}"
    output = ssh_conn.execute_command(cmd)
    if output:
        table = Table(title=f"📁 Directory: {path}", box=box.ROUNDED)
        table.add_column("Permissions", style="cyan")
        table.add_column("Owner", style="green")
        table.add_column("Group", style="green")
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Modified", style="magenta")
        table.add_column("Name", style="bold white")
        
        lines = output.strip().split('\n')[1:]
        for line in lines:
            parts = line.split(None, 8)
            if len(parts) >= 9:
                perms = parts[0]
                owner = parts[2]
                group = parts[3]
                size = parts[4]
                date_str = f"{parts[5]} {parts[6]} {parts[7]}"
                name = parts[8]
                icon = "📁" if perms.startswith('d') else "📄"
                table.add_row(perms, owner, group, size, date_str, f"{icon} {name}")
        
        console.print(table)
        return True
    return False


def file_get_home_path(ssh_conn):
    """Get user's home directory."""
    return ssh_conn.execute_command("echo $HOME").strip()


def file_get_scratch_path(ssh_conn):
    """Get user's scratch directory."""
    output = ssh_conn.execute_command("echo ~/scratch")
    return output.strip()


def file_upload(ssh_conn, local_path, remote_path):
    """Upload a file to the remote server."""
    try:
        cmd = f"scp -P {ssh_conn.port} -o ControlPath={ssh_conn.control_path} {local_path} {ssh_conn.user}@{ssh_conn.host}:{remote_path}"
        console.print(f"[bold yellow]Uploading {local_path} to {remote_path}...[/bold yellow]")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[bold green]✓ Upload successful![/bold green]")
            return True
        else:
            console.print(f"[bold red]✗ Upload failed: {result.stderr}[/bold red]")
            return False
    except Exception as e:
        console.print(f"[bold red]✗ Upload error: {str(e)}[/bold red]")
        return False


def file_download(ssh_conn, remote_path, local_path):
    """Download a file from the remote server."""
    try:
        cmd = f"scp -P {ssh_conn.port} -o ControlPath={ssh_conn.control_path} {ssh_conn.user}@{ssh_conn.host}:{remote_path} {local_path}"
        console.print(f"[bold yellow]Downloading {remote_path} to {local_path}...[/bold yellow]")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[bold green]✓ Download successful![/bold green]")
            return True
        else:
            console.print(f"[bold red]✗ Download failed: {result.stderr}[/bold red]")
            return False
    except Exception as e:
        console.print(f"[bold red]✗ Download error: {str(e)}[/bold red]")
        return False

def file_edit(ssh_conn, path, filename):
    """Edit file."""
    console.print(f"[bold yellow]Starting nano editor...[/bold yellow]")
    
    cmd = f"nano {path}/{filename}"
    try:
        subprocess.run(
            f"ssh -S {ssh_conn.control_path} -t -p {ssh_conn.port} {ssh_conn.user}@{ssh_conn.host} '{cmd}'",
            shell=True
        )
    except Exception as e:
        console.print(f"[bold red]Session error: {str(e)}[/bold red]")
    
    
def file_create_directory(ssh_conn, path):
    """Create a new directory."""
    output = ssh_conn.execute_command(f"mkdir -p {path} && echo 'SUCCESS'")
    if output and 'SUCCESS' in output:
        console.print(f"[bold green]✓ Directory created: {path}[/bold green]")
        return True
    console.print(f"[bold red]✗ Failed to create directory[/bold red]")
    return False


def file_delete(ssh_conn, path, is_directory=False):
    """Delete a file or directory."""
    cmd = f"rm -rf {path}" if is_directory else f"rm {path}"
    output = ssh_conn.execute_command(f"{cmd} && echo 'SUCCESS'")
    if output and 'SUCCESS' in output:
        console.print(f"[bold green]✓ Deleted: {path}[/bold green]")
        return True
    console.print(f"[bold red]✗ Failed to delete[/bold red]")
    return False


def file_rename(ssh_conn, old_path, new_path):
    """Rename/move a file or directory."""
    output = ssh_conn.execute_command(f"mv {old_path} {new_path} && echo 'SUCCESS'")
    if output and 'SUCCESS' in output:
        console.print(f"[bold green]✓ Renamed: {old_path} → {new_path}[/bold green]")
        return True
    console.print(f"[bold red]✗ Failed to rename[/bold red]")
    return False


def file_view_content(ssh_conn, path, lines=50):
    """View file content (for text files)."""
    output = ssh_conn.execute_command(f"head -n {lines} {path}")
    if output:
        ext = path.split('.')[-1] if '.' in path else 'txt'
        syntax = Syntax(output, ext, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"📄 {path}", border_style="green"))
        return True
    return False

def file_search(ssh_conn, path, pattern, depth):
    """Search for files by name pattern."""
    console.print(f"[bold cyan]Searching for '{pattern}' in {path}...[/bold cyan]\n")
    cmd1 = f'find {path} -maxdepth 1 -name "*{pattern}*" | head -50'
    output = ssh_conn.execute_command(cmd1)
    
    if output and output.strip() and not depth:
        console.print("[bold green]Files found in depth:[/bold green]")
        console.print(output)
        return True
    else:
        cmd2 = f'find {path} -name "*{pattern}*" | head -50'
        output = ssh_conn.execute_command(cmd2)
        
        if output and output.strip():
            console.print("[bold green]Files found (recursive search):[/bold green]")
            console.print(output)
            return True
        else:
            console.print("[yellow]No files found matching the pattern.[/yellow]")
            return False

def file_disk_quota(ssh_conn, path="~"):
    """Get disk usage for a directory."""
    output = ssh_conn.execute_command(f"du -h {path} | sort -hr | head -20")
    if output:
        table = Table(title=f"💾 Disk Usage: {path}", box=box.ROUNDED)
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Path", style="cyan")
        
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    table.add_row(parts[0], parts[1])
        
        console.print(table)
        
        quota_output = ssh_conn.execute_command("lfs quota -h ~/")
        if quota_output:
            console.print("\n[bold cyan]Quota Information:[/bold cyan]")
            console.print(quota_output)
        return True
    return False
