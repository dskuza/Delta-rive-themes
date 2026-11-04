#!/usr/bin/env python3
"""Import built themes through the sibling Delta simulator workflow."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(add_help=False)
parser.add_argument('--delta',type=Path,default=Path(os.environ.get('DELTA_DIR',ROOT.parent/'Delta')))
args,remaining=parser.parse_known_args()
command=args.delta.expanduser().resolve()/'Scripts/import-rive-themes.py'
if not command.is_file():
    raise SystemExit('Delta’s import command was not found. Run Tools/setup.py or pass --delta PATH.')
subprocess.run([sys.executable,str(command),*remaining,'--themes',str(ROOT)],check=True)
