"""Conda Package Manager menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import conda


def conda_menu(ssh_conn):
    """Conda package manager submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "🐍 Conda Package Manager:",
            choices=[
                "📋 List Environments",
                "✅ Activate Environment",
                "➕ Create Environment",
                "➖ Remove Environment",
                "📦 Install Package",
                "📦 List Package",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📋 List Environments":
            conda.conda_list_envs(ssh_conn)
        elif choice == "✅ Activate Environment":
            env_name = questionary.text("Environment name:", style=custom_style).ask()
            if env_name:
                conda.conda_activate_env(ssh_conn, env_name)
        elif choice == "➕ Create Environment":
            env_name = questionary.text("Environment name:", style=custom_style).ask()
            python_ver = questionary.text("Python version (leave empty for default):", default="", style=custom_style).ask()
            if env_name:
                conda.conda_create_env(ssh_conn, env_name, python_ver if python_ver else None)
        elif choice == "➖ Remove Environment":
            env_name = questionary.text("Environment name to remove:", style=custom_style).ask()
            if env_name:
                if questionary.confirm(f"Remove environment '{env_name}'?", default=False, style=custom_style).ask():
                    conda.conda_remove_env(ssh_conn, env_name)
        elif choice == "📦 Install Package":
            env_name = questionary.text("Environment name:", style=custom_style).ask()
            package = questionary.text("Package name:", style=custom_style).ask()
            if env_name and package:
                conda.conda_install_package(ssh_conn, env_name, package)
        elif choice == "📦 List Package":
            env_name = questionary.text("Environment name:", style=custom_style).ask()
            if env_name:
                conda.conda_list_package(ssh_conn, env_name)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
