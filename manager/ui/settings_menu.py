"""User Settings menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import settings
from manager.config import load_config, delete_config


def settings_menu(ssh_conn):
    """User Settings submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "User Settings:",
            choices=[
                "View Profile",
                "SSH Keys",
                questionary.Separator(),
                "View Saved Connection",
                "Delete Saved Connection",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "View Profile":
            settings.settings_get_profile(ssh_conn)
        elif choice == "SSH Keys":
            settings.settings_list_ssh_keys(ssh_conn)
        elif choice == "View Saved Connection":
            config = load_config()
            if config:
                console.print(f"\n[cyan]Host:[/cyan] {config.get('host')}")
                console.print(f"[cyan]User:[/cyan] {config.get('user')}")
                console.print(f"[cyan]Port:[/cyan] {config.get('port')}\n")
            else:
                console.print("[yellow]No saved connection found.[/yellow]")
        elif choice == "Delete Saved Connection":
            confirm = questionary.confirm(
                "Are you sure you want to delete the saved connection?",
                default=False,
                style=custom_style
            ).ask()
            if confirm:
                delete_config()
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
