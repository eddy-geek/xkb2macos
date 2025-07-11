"""Main entry point for the XKB to macOS layout converter.

This module allows running the package directly with `python -m xkb_to_macos`.
"""
import sys
from xkb_to_macos.cli import main

if __name__ == '__main__':
    sys.exit(main())
