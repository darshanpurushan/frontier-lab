"""Run the complete research study for stocks and sector ETFs."""
from pathlib import Path
import os
from frontier_lab.cli import main

if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    main(['--config','config.json','--study','--etf-study'])
