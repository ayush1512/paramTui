"""SSH Connection management module."""

import subprocess
import os
import tempfile
import time
from rich.console import Console

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
            
            self.host = host
            self.user = user
            self.port = port
            
            self.control_path = os.path.join(tempfile.gettempdir(), f"ssh-{user}-{host}-{port}")
            
            console.print(f"[dim]Establishing persistent connection...[/dim]\n")
            console.print("[bold cyan]Please complete authentication:[/bold cyan]")
            
            initial_command = f"ssh -M -S {self.control_path} -o ControlPersist=10m -p {port} {user}@{host} 'echo CONNECTION_SUCCESS'"
            
            result = subprocess.run(initial_command, shell=True, text=True, capture_output=True)
            
            if result.returncode == 0 and "CONNECTION_SUCCESS" in result.stdout:
                time.sleep(1)
                
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
                subprocess.run(
                    f"ssh -S {self.control_path} -O exit {self.user}@{self.host}",
                    shell=True,
                    capture_output=True
                )
            except:
                pass
            
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
