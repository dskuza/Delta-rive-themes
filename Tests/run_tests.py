#!/usr/bin/env python3
"""Compile tests against fresh copies of the production parser and archive reader."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
with tempfile.TemporaryDirectory(prefix='delta-rive-tests-') as temporary:
    package=Path(temporary)
    sources=package/'Sources'/'ThemeTests'
    sources.mkdir(parents=True)
    for name in ['RiveControllerSkinManifest.swift','RiveControllerSkinArchive.swift']:
        shutil.copy2(REPO/'Delta'/'Controller Themes'/name,sources/name)
    shutil.copy2(ROOT/'Tests'/'ManifestTests.swift',sources/'ManifestTests.swift')
    dependency=str(REPO/'Cores'/'DeltaCore'/'External'/'ZIPFoundation')
    (package/'Package.swift').write_text('''// swift-tools-version: 5.10
import PackageDescription
let package = Package(name: "ThemeTests", dependencies: [.package(path: '''+json.dumps(dependency)+''')], targets: [.executableTarget(name: "ThemeTests", dependencies: ["ZIPFoundation"])])
''')
    subprocess.run(['swift','run','--package-path',str(package),'--scratch-path',str(package/'build'),'ThemeTests',str(ROOT)],check=True)
