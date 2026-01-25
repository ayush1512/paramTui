"""User Settings menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import settings


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
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "View Profile":
            settings.settings_get_profile(ssh_conn)
        elif choice == "SSH Keys":
            settings.settings_list_ssh_keys(ssh_conn)
        elif choice == "🐚 Shell Configuration":
            settings.settings_get_default_shell(ssh_conn)
        elif choice == "🐍 Conda Configuration":
            settings.settings_get_conda_config(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
