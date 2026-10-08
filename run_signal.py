"""Research the supplied WorldQuant-style price/volume formula on real prices."""
from pathlib import Path
import os
from frontier_lab.signal_cli import main

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    main(['--config','config.json'])
