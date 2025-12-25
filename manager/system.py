import subprocess
import platform
from rich.console import Console
from rich.table import Table
import os
import tempfile

console = Console()

class SSHConnection:
    """Manages SSH connection to remote server with multi-step auth."""
    
    def __init__(self):
        self.host = None
        self.user = None
        self.port = None
        self.connected = False
        self.control_path = None
    
    def connect(self, host, user, port):
        """Establish SSH connection with puzzle, OTP, and password authentication."""
        try:
            console.print(f"[bold yellow]Connecting to {user}@{host}:{port}...[/bold yellow]")
            
            # Store connection details
            self.host = host
            self.user = user
            self.port = port
            
            # Create a unique control path for this connection
            self.control_path = os.path.join(tempfile.gettempdir(), f"ssh-{user}-{host}-{port}")
            
            # Start SSH connection with ControlMaster
            # Remove -f flag to allow interactive authentication
            ssh_command = f"ssh -M -S {self.control_path} -o ControlPersist=yes -N -p {port} {user}@{host} &"
            console.print(f"[dim]Establishing persistent connection...[/dim]\n")
            
            # For the initial connection, let user handle it interactively
            console.print("[bold cyan]Please complete authentication:[/bold cyan]")
            # console.print("  1. Answer the puzzle (type the string from the ASCII art)")
            # console.print("  2. Enter OTP/Verification code")
            # console.print("  3. Enter password\n")
            
            # First, establish connection interactively without background flag
            initial_command = f"ssh -M -S {self.control_path} -o ControlPersist=10m -p {port} {user}@{host} 'echo CONNECTION_SUCCESS'"
            
            result = subprocess.run(initial_command, shell=True, text=True, capture_output=True)
            
            if result.returncode == 0 and "CONNECTION_SUCCESS" in result.stdout:
                # Verify the control socket was created
                import time
                time.sleep(1)  # Give it a moment to establish
                
                # Test if the persistent connection is working
                test_command = f"ssh -S {self.control_path} -O check {user}@{host} 2>&1"
                test_result = subprocess.run(
                    test_command, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                if "Master running" in test_result.stdout or test_result.returncode == 0:
                    self.connected = True
                    console.print(f"\n[bold green]✓ Successfully connected to {user}@{host}[/bold green]")
                    console.print(f"[dim]Persistent connection established via ControlMaster[/dim]")
                    return True
                else:
                    console.print("[bold red]✗ Control socket not established[/bold red]")
                    self.connected = False
                    return False
            else:
                console.print(f"[bold red]✗ Connection failed[/bold red]")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")
                self.connected = False
                return False
                
        except Exception as e:
            console.print(f"[bold red]✗ Connection failed: {str(e)}[/bold red]")
            self.connected = False
            return False
    
    def execute_command(self, command):
        """Execute a command on the remote server using the persistent connection."""
        if not self.connected:
            console.print("[bold red]Not connected to any server![/bold red]")
            return None
        
        try:
            # Use the existing ControlMaster connection (no re-authentication needed)
            ssh_command = f"ssh -S {self.control_path} -p {self.port} {self.user}@{self.host} '{command}'"
            result = subprocess.run(
                ssh_command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.stderr and result.returncode != 0:
                console.print(f"[bold red]Error:[/bold red] {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            console.print("[bold red]Command timed out[/bold red]")
            return None
        except Exception as e:
            console.print(f"[bold red]Command execution failed: {str(e)}[/bold red]")
            return None
    
    def disconnect(self):
        """Close SSH connection and cleanup ControlMaster socket."""
        if self.connected and self.control_path:
            try:
                # Exit the ControlMaster connection
                subprocess.run(
                    f"ssh -S {self.control_path} -O exit {self.user}@{self.host}",
                    shell=True,
                    capture_output=True
                )
            except:
                pass
            
            # Remove socket file if it exists
            if os.path.exists(self.control_path):
                try:
                    os.remove(self.control_path)
                except:
                    pass
        
        self.connected = False
        console.print("[bold yellow]Disconnected from server.[/bold yellow]")
    
    def interactive_shell(self):
        """Launch an interactive shell session using the persistent connection."""
        if not self.connected:
            console.print("[bold red]Not connected to any server![/bold red]")
            return
        
        console.print(f"[bold yellow]Starting interactive shell on {self.user}@{self.host}...[/bold yellow]")
        console.print("[dim]Type 'exit' to return to Console Manager[/dim]\n")
        
        try:
            subprocess.run(
                f"ssh -S {self.control_path} -p {self.port} {self.user}@{self.host}",
                shell=True
            )
        except Exception as e:
            console.print(f"[bold red]Shell session error: {str(e)}[/bold red]")


# SLURM Management Functions
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
    output = ssh_conn.execute_command(f"sinfo")
    if output:
        console.print(output)

# Conda Management Functions
def conda_list_envs(ssh_conn):
    """List all conda environments."""
    output = ssh_conn.execute_command("conda env list")
    if output:
        console.print("[bold green]Conda Environments:[/bold green]")
        console.print(output)

def conda_activate_env(ssh_conn, env_name):
    """Activate a conda environment."""
    console.print(f"[bold yellow]Activating environment '{env_name}'...[/bold yellow]")
    output = ssh_conn.execute_command(f"conda activate {env_name}")
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


# Tunneling Functions
def create_tunnel(ssh_conn, remote_port, local_port=None):
    """Create an SSH tunnel (port forwarding) using the persistent connection."""
    if local_port is None:
        local_port = remote_port
    
    console.print(f"[bold yellow]Creating tunnel: localhost:{local_port} -> {ssh_conn.host}:{remote_port}[/bold yellow]")
    console.print(f"[dim]Press Ctrl+C to close the tunnel[/dim]\n")
    
    try:
        subprocess.run(
            f"ssh -S {ssh_conn.control_path} -L {local_port}:localhost:{remote_port} -N -p {ssh_conn.port} {ssh_conn.user}@{ssh_conn.host}",
            shell=True
        )
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Tunnel closed.[/bold yellow]")


# System Info Functions
def get_remote_system_info(ssh_conn):
    """Get system information from remote server."""
    output = ssh_conn.execute_command("uname -a && df -h && free -h")
    if output:
        console.print("[bold green]Remote System Information:[/bold green]")
        console.print(output)

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
    # macOS usually uses ifconfig
    output = run_command("ifconfig")
    if output:
        console.print("[bold green]Network Interfaces:[/bold green]")
        console.print(output)

