#!/usr/bin/env python3
"""Run the offline suite by default; forward explicit pytest arguments."""
from pathlib import Path
import subprocess
import sys

if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", *sys.argv[1:]], cwd=Path(__file__).parent))
