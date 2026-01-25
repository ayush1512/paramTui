"""Conda environment management commands."""

from rich.console import Console

console = Console()


def conda_list_envs(ssh_conn):
    """List all conda environments."""
    output = ssh_conn.execute_command(" conda env list")
    if output:
        console.print("[bold green]Conda Environments:[/bold green]")
        console.print(output)


def conda_activate_env(ssh_conn, env_name):
    """Activate a conda environment."""
    console.print(f"[bold yellow]Activating environment '{env_name}'...[/bold yellow]")
    output = ssh_conn.execute_command(f"source conda activate {env_name}")
    if output and ("error" in output.lower() or "not found" in output.lower()):
        console.print(f"[bold red]Failed to activate environment:[/bold red] {output}")
    else:
        console.print("[bold green]Environment activated![/bold green]")


def conda_create_env(ssh_conn, env_name, python_version=None):
    """Create a new conda environment."""
    if python_version:
        cmd = f"conda create -n {env_name} python={python_version} -y"
    else:
        cmd = f"conda create -n {env_name} -y"
    
    console.print(f"[bold yellow]Creating environment '{env_name}'...[/bold yellow]")
    output = ssh_conn.execute_command(cmd)
    if output:
        console.print("[bold green]Environment created successfully![/bold green]")


def conda_remove_env(ssh_conn, env_name):
    """Remove a conda environment."""
    console.print(f"[bold yellow]Removing environment '{env_name}'...[/bold yellow]")
    output = ssh_conn.execute_command(f"conda env remove -n {env_name} -y")
    console.print("[bold green]Environment removed![/bold green]")


def conda_install_package(ssh_conn, env_name, package):
    """Install a package in a conda environment."""
    console.print(f"[bold yellow]Installing {package} in '{env_name}'...[/bold yellow]")
    output = ssh_conn.execute_command(f"conda install -n {env_name} {package} -y")
    if output:
        console.print("[bold green]Package installed![/bold green]")
        
def conda_list_package(ssh_conn, env_name):
    """Install a package in a conda environment."""
    console.print(f"[bold yellow]Packages installed in '{env_name}'...[/bold yellow]")
    if env_name == 'base':
        output = ssh_conn.execute_command(f"source ~/.bashrc && conda list -n base")
    else:
        output = ssh_conn.execute_command(f"source ~/.bashrc && conda list -n {env_name}")
    if output:
        console.print({output})
