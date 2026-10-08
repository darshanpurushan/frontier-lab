"""Open this file in Spyder and press F5, or run it from Terminal."""
from pathlib import Path
import os

from frontier_lab.cli import main

if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    main(['--config', 'config.json'])
