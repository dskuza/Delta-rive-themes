#!/usr/bin/env python3
"""Prepare the sibling Delta rive checkout and its forked dependencies."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__,epilog='Additional options are forwarded to Delta’s setup command, including --xcode and --offline.')
parser.add_argument('--delta',type=Path,default=Path(os.environ.get('DELTA_DIR',ROOT.parent/'Delta')))
args,remaining=parser.parse_known_args()
delta=args.delta.expanduser().resolve()
if not delta.exists():
    if '--offline' in remaining:
        parser.error('Delta is missing; clone dskuza/Delta on rive first.')
    subprocess.run(['git','clone','--branch','rive','git@github.com:dskuza/Delta.git',str(delta)],check=True)
command=delta/'Scripts/setup-rive.py'
if not command.is_file():
    parser.error(f'{delta} needs Delta’s rive branch with Scripts/setup-rive.py.')
subprocess.run([sys.executable,str(command),*remaining,'--themes',str(ROOT)],check=True)
