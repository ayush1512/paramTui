"""File Manager menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import files


def file_manager_menu(ssh_conn):
    """File Manager submenu."""
    current_path = files.file_get_home_path(ssh_conn)
    
    while True:
        console.clear()
        print_header(ssh_conn)
        console.print(f"[bold cyan]📁 Current Directory: {current_path}[/bold cyan]\n")
        
        choice = questionary.select(
            "📁 File Manager:",
            choices=[
                "📂 Browse Current Directory",
                "🏠 Go to Home Directory",
                # "💾 Go to Scratch Directory",
                "📁 Change Directory",
                questionary.Separator("─── File Operations ───"),
                "⬆️  Upload File",
                "⬇️  Download File",
                "📄 Edit File",
                "📄 Create File/Directory",
                "✏️  Rename File/Directory",
                "🗑️  Delete File/Directory",
                questionary.Separator("─── View & Search ───"),
                "👁️  View File Content",
                "🔍 Search Files",
                "📊 View Disk Usage",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📂 Browse Current Directory":
            files.file_browse_directory(ssh_conn, current_path)
        elif choice == "🏠 Go to Home Directory":
            current_path = files.file_get_home_path(ssh_conn)
            files.file_browse_directory(ssh_conn, current_path)
        elif choice == "💾 Go to Scratch Directory":
            current_path = files.file_get_scratch_path(ssh_conn)
            files.file_browse_directory(ssh_conn, current_path)
        elif choice == "📁 Change Directory":
            new_path = questionary.text(
                "Enter path:",
                default=current_path,
                style=custom_style
            ).ask()
            if new_path:
                current_path = new_path
                files.file_browse_directory(ssh_conn, current_path)
        elif choice == "⬆️  Upload File":
            local = questionary.path("Select local file to upload:", style=custom_style).ask()
            remote = questionary.text("Remote destination:", default=current_path + "/", style=custom_style).ask()
            if local and remote:
                files.file_upload(ssh_conn, local, remote)
        elif choice == "⬇️  Download File":
            remote = questionary.text("Remote file path:", style=custom_style).ask()
            local = questionary.text("Local destination:", default="./", style=custom_style).ask()
            if remote and local:
                files.file_download(ssh_conn, remote, local)
        elif choice == "📄 Edit File":
            file_name = questionary.text("File Name:", style=custom_style).ask()
            if file_name:
                path = f"{current_path}"
                files.file_edit(ssh_conn, path, file_name)
        elif choice == "📄 Create File/Directory":
            file_type = questionary.select(
                "Create:",
                choices=["📁 Directory", "📄 Empty File"],
                style=custom_style
            ).ask()
            name = questionary.text("Name:", style=custom_style).ask()
            if name:
                path = f"{current_path}/{name}"
                if "Directory" in file_type:
                    files.file_create_directory(ssh_conn, path)
                else:
                    ssh_conn.execute_command(f"touch {path}")
                    console.print(f"[bold green]✓ File created: {path}[/bold green]")
        elif choice == "✏️  Rename File/Directory":
            old_name = questionary.text("Current name/path:", style=custom_style).ask()
            new_name = questionary.text("New name/path:", style=custom_style).ask()
            if old_name and new_name:
                files.file_rename(ssh_conn, old_name, new_name)
        elif choice == "🗑️  Delete File/Directory":
            path = questionary.text("Path to delete:", style=custom_style).ask()
            if path:
                is_dir = questionary.confirm("Is this a directory?", default=False, style=custom_style).ask()
                if questionary.confirm(f"Are you sure you want to delete '{path}'?", default=False, style=custom_style).ask():
                    files.file_delete(ssh_conn, path, is_dir)
        elif choice == "👁️  View File Content":
            path = questionary.text("File path:", style=custom_style).ask()
            if path:
                files.file_view_content(ssh_conn, path)
        elif choice == "🔍 Search Files":
            pattern = questionary.text("Search pattern:", style=custom_style).ask()
            if pattern:
                files.file_search(ssh_conn, current_path, pattern)
        elif choice == "📊 View Disk Usage":
            files.file_disk_quota(ssh_conn, current_path)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
