"""Read the saved Delta phone layouts as the placement reference for the controllers.

The default edge-to-edge portrait artwork includes 34 points for the home
indicator. UIKit supplies that inset for these safe-area-aware themes instead.
"""
import json
from controller_scene import ROOT


def layout_for(system, orientation):
    rep = json.loads((ROOT/'Assets/DefaultLayouts.json').read_text())[system][orientation]
    width = 390 if orientation == 'portrait' else 844
    scale = width / rep['mappingSize']['width']
    height = round((rep['mappingSize']['height'] - (34 if orientation == 'portrait' else 0)) * scale)
    controls = {}
    for item in rep['items']:
        inputs = item['inputs']
        name = ('stick' if 'thumbstick' in item else 'pad') if isinstance(inputs, dict) else inputs[0]
        frame = item['frame']
        controls[name] = ((frame['x'] + frame['width']/2)*scale,
                          (frame['y'] + frame['height']/2)*scale,
                          frame['width']*scale, frame['height']*scale)
    # Keep the Menu label legible rather than reproducing the default icon.
    x,y,_,_ = controls['menu']
    controls['menu'] = (x,y,42 if orientation == 'portrait' else 76,20 if orientation == 'portrait' else 26)
    if system == 'N64':
        # Retain the requested duplicated Z controls above each shoulder.
        left,right = (58,332) if orientation == 'portrait' else (70,774)
        for name,x in [('l',left),('r',right)]:
            controls[name] = (x,55 if orientation == 'portrait' else 65,90,26)
        controls['z'] = (right,18 if orientation == 'portrait' else 22,52,22)
        controls['zLeft'] = (left,18 if orientation == 'portrait' else 22,52,22)
        x,y,_,_ = controls['stick']
        controls['stick'] = (x,y,108,108)
    return width,height,controls
