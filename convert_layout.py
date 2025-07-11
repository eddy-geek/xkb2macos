#!/usr/bin/env python3
"""Command-line script for XKB to macOS layout conversion.

This script serves as the main entry point for the XKB to macOS layout converter.
"""
import sys
from xkb_to_macos.cli import main

if __name__ == '__main__':
    sys.exit(main())
