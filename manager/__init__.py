"""ParamTUI - SSH Manager & HPC Console.

A modular terminal user interface for managing HPC clusters.
"""

from manager.connection import SSHConnection
from manager.ui.menus import main_menu, connection_menu

__all__ = ['SSHConnection', 'main_menu', 'connection_menu']
__version__ = '1.0.0'