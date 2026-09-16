"""ParamTUI - SSH Manager & HPC Console.

A modular terminal user interface for managing HPC clusters.
"""

import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from manager.connection import SSHConnection
from manager.ui.menus import main_menu, connection_menu

__all__ = ['SSHConnection', 'main_menu', 'connection_menu']
__version__ = '1.0.0'