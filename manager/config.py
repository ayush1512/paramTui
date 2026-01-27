# manager/config.py
"""Configuration file management for storing SSH connection details."""

import json
import os
from pathlib import Path
from rich.console import Console

console = Console()

CONFIG_FILE = "paramtui_config.json"

def get_config_path():
    """Get the path to the config file in the parent folder."""
    current_dir = Path(__file__).parent.parent
    return current_dir / CONFIG_FILE

def load_config():
    """Load configuration from file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
        return {}

def save_config(host, user, port):
    """Save connection details to config file."""
    config_path = get_config_path()
    
    config = {
        "host": host,
        "user": user,
        "port": port
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        console.print(f"[green]✓ Configuration saved to {config_path.name}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Failed to save config: {e}[/red]")
        return False

def delete_config():
    """Delete the config file."""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            config_path.unlink()
            console.print("[green]✓ Configuration deleted[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to delete config: {e}[/red]")
            return False
    return True