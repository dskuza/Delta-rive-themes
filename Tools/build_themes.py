#!/usr/bin/env python3
"""Build the NES/N64 Rive files, native fallback PDFs and importable packages.

Requires macOS with Metal, Xcode command-line tools and Rive CLI 1.8.0 or newer.
No login is needed: these scenes contain no scripts.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
THEMES=['nes','n64']

def run(*args):
    subprocess.run([str(a) for a in args],cwd=ROOT,check=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('themes',nargs='*',choices=THEMES)
    themes=parser.parse_args().themes or THEMES
    for name in themes:
        run('rive',ROOT/name,'--verify')
        run('rive',ROOT/name,'--once')
    (ROOT/'build').mkdir(exist_ok=True)
    run('swift','-module-cache-path',ROOT/'build/ModuleCache',ROOT/'Tools/FallbackArtwork.swift',ROOT,*themes)
    (ROOT/'Dist').mkdir(exist_ok=True)
    for name in themes:
        project=ROOT/name
        members={'info.json':project/'info.json','rive.json':project/'rive.json',name+'.riv':project/'build'/f'{name}.riv'}
        for orientation in ['portrait','landscape']:
            preview=project/'build'/f'{orientation}-preview.png'
            run('rive',project,'--artboard='+orientation.title(),
                '--data=aPressed=true','--data=upPressed=true','--advance=20',
                '--screenshot='+str(preview))
            members[preview.name]=preview
            members[orientation+'.pdf']=project/'build'/(orientation+'.pdf')
        # Cap assets follow native metadata rather than a theme-name convention.
        info=json.loads((project/'info.json').read_text())
        for displays in info['representations'].values():
            for orientations in displays.values():
                for rep in orientations.values():
                    for item in rep['items']:
                        if 'thumbstick' in item:
                            filename=item['thumbstick']['name']
                            members[filename]=project/'build'/filename
        shutil.copy2(project/'build'/f'{name}.riv',ROOT/'Dist'/f'{name}.riv')
        target=ROOT/'Dist'/f'{name}.deltaskin'
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for filename,path in sorted(members.items()):
                entry=zipfile.ZipInfo(filename,date_time=(2026,1,1,0,0,0))
                entry.compress_type=zipfile.ZIP_DEFLATED
                archive.writestr(entry,path.read_bytes())
        print(f'Packaged {target} ({target.stat().st_size} bytes)')

if __name__=='__main__':
    main()
