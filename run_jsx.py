#!/usr/bin/env python3
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from JSX.cli import main

if __name__ == "__main__":
    sys.exit(main())
