"""Help menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import help as help_cmds


def help_menu(ssh_conn):
    """Help submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "📚 Help & Documentation:",
            choices=[
                "📋 SLURM Cheat Sheet",
                "🔧 Common Errors & Fixes",
                "📖 About PARAM TUI",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📋 SLURM Cheat Sheet":
            help_cmds.help_slurm_cheatsheet()
        elif choice == "🔧 Common Errors & Fixes":
            help_cmds.help_common_errors()
        elif choice == "📖 About PARAM TUI":
            help_cmds.help_about()
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
