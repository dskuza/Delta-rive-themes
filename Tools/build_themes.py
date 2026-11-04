#!/usr/bin/env python3
"""Build .riv files, native fallback PDFs and importable .deltaskin archives.

Requires macOS, Xcode command-line tools and Rive CLI 1.8.0 or newer.
No login is needed: these scenes contain no scripts.
"""
from pathlib import Path
import subprocess
import shutil
import zipfile
import argparse
ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([str(a) for a in args],cwd=ROOT,check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('themes', nargs='*', choices=['Template','NeonCircuit','Orbit','OrbitCrystal'])
    requested = parser.parse_args().themes
    themes = requested or ['Template','NeonCircuit','Orbit','OrbitCrystal']
    projects = themes.copy()
    if not requested and (ROOT/'AnalogStickLab'/'scene.rml').exists():
        projects.append('AnalogStickLab')
    for name in projects:
        run('rive',ROOT/name,'--verify')
        run('rive',ROOT/name,'--once')
    (ROOT/'build').mkdir(exist_ok=True)
    run('swift','-module-cache-path',ROOT/'build'/'ModuleCache',ROOT/'Tools'/'FallbackArtwork.swift',ROOT)
    (ROOT/'Dist').mkdir(exist_ok=True)
    if 'AnalogStickLab' in projects:
        shutil.copy2(ROOT/'AnalogStickLab'/'build'/'AnalogStickLab.riv',ROOT/'Dist'/'AnalogStickLab.riv')
    for name in themes:
        project=ROOT/name
        members={'info.json':project/'info.json','rive.json':project/'rive.json',name+'.riv':project/'build'/f'{name}.riv'}
        for asset in ['portrait.pdf','landscape.pdf']:
            members[asset]=project/'build'/asset
        if name in ['Orbit','OrbitCrystal']:
            members['stick.pdf'] = project/'build'/'stick.pdf'
        shutil.copy2(project/'build'/f'{name}.riv',ROOT/'Dist'/f'{name}.riv')
        target=ROOT/'Dist'/f'{name}.deltaskin'
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for filename,path in sorted(members.items()):
                info=zipfile.ZipInfo(filename,date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(info,path.read_bytes())
        print(f'Packaged {target} ({target.stat().st_size} bytes)')
if __name__=='__main__':main()
