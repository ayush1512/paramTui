#!/usr/bin/env python3
"""ParamTUI - SSH Manager & HPC Console.

A modern terminal user interface for managing HPC clusters.
"""

import sys
from manager import main_menu

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Goodbye!")
        sys.exit(0)