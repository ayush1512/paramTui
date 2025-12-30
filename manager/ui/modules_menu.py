"""Software Modules menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import modules


def modules_menu(ssh_conn):
    """Software Modules submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "🧩 Software Modules:",
            choices=[
                "📋 List Available Modules",
                "✅ Show Loaded Modules",
                "➕ Load Module",
                "➖ Unload Module",
                "🔍 Search Modules",
                "📚 Recommended Module Sets",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📋 List Available Modules":
            pattern = questionary.text("Filter pattern (leave empty for all):", default="", style=custom_style).ask()
            modules.module_list_available(ssh_conn, pattern if pattern else None)
        elif choice == "✅ Show Loaded Modules":
            modules.module_list_loaded(ssh_conn)
        elif choice == "➕ Load Module":
            module_name = questionary.text("Module name:", style=custom_style).ask()
            if module_name:
                modules.module_load(ssh_conn, module_name)
        elif choice == "➖ Unload Module":
            module_name = questionary.text("Module name:", style=custom_style).ask()
            if module_name:
                modules.module_unload(ssh_conn, module_name)
        elif choice == "🔍 Search Modules":
            keyword = questionary.text("Search keyword (e.g., cuda, python, mpi):", style=custom_style).ask()
            if keyword:
                modules.module_search(ssh_conn, keyword)
        elif choice == "📚 Recommended Module Sets":
            modules.module_get_recommended_sets()
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
