#!/usr/bin/env python3
"""
JSX - JavaScript Secret Scanner
Entry point for the CLI tool.
"""

import sys
import os

# Add current directory to path so JSX package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from JSX.cli import main

if __name__ == "__main__":
    sys.exit(main())
