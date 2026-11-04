#!/usr/bin/env python3
"""Render actual Rive effects, then check pixels. Requires a Metal-capable session."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('theme',nargs='?',choices=['OrbitCrystal','CrystalNES'],default='OrbitCrystal')
theme=parser.parse_args().theme
with tempfile.TemporaryDirectory(prefix='delta-crystal-render-') as temporary:
    target=Path(temporary)
    def render(name,*arguments):
        subprocess.run(['rive',str(ROOT/theme),*arguments,
                        '--screenshot='+str(target/(name+'.png'))],check=True,capture_output=True,text=True)
    render('idle','--advance=1')
    if theme=='OrbitCrystal':
        render('moved','--data=stickX=1','--data=stickY=1','--advance=10')
    render('tapTravel','--data=aPressed=true','--advance=6','--data=aPressed=false','--advance=22')
    render('tapSettled','--data=aPressed=true','--advance=6','--data=aPressed=false','--advance=100')
    render('reducedEarly','--data=aPressed=true','--data=reduceMotion=true','--advance=10')
    render('reducedLate','--data=aPressed=true','--data=reduceMotion=true','--advance=35')
    render('landscape','--artboard=Landscape','--data=aPressed=true','--advance=20')
    subprocess.run(['swift','-module-cache-path',str(ROOT/'build/ModuleCache'),
                    str(ROOT/'Tests/CrystalRenderTests.swift'),str(target),str(ROOT/theme/'info.json')],check=True)
