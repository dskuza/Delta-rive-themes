#!/usr/bin/env python3
"""Orbit N64: native analog hit testing with a data-bound vector instrument panel."""
import json
import math
from generate_themes import ROOT, Scene

BUTTONS = ['up', 'down', 'left', 'right', 'analogStickUp', 'analogStickDown',
           'analogStickLeft', 'analogStickRight', 'cUp', 'cDown', 'cLeft', 'cRight',
           'a', 'b', 'l', 'r', 'z', 'start', 'menu']
CYAN, VIOLET, GOLD = 'FF63E8F1', 'FFB4A0FF', 'FFFFD375'


class Orbit(Scene):
    def __init__(self):
        super().__init__(True, analog=True, buttons=BUTTONS,
                         numbers=['stickX', 'stickY', 'stickMagnitude'])
        self.color = CYAN

    def numeric(self, target, key, prop, low, high, minimum=0, maximum=1):
        converter = self.el(self.root, 'DataConverterRangeMapper', minInput=minimum,
                            maxInput=maximum, minOutput=low, maxOutput=high,
                            clampLower=True, clampUpper=True, name=prop+' mapping')
        self.bind(target, key, prop, converter.get('id'))

    def dpad(self, a, sm, x, y):
        pad = self.el(a, 'Node', x=x, y=y, name='Digital navigation pad')
        for i, name in enumerate(['up', 'right', 'down', 'left']):
            dx, dy = [(0,-1),(1,0),(0,1),(-1,0)][i]
            arm = self.el(pad, 'Node', x=dx*26, y=dy*26, rotation=i*math.pi/2)
            arrow = self.el(arm, 'Shape', y=-2, name=name+' engraving')
            self.el(arrow, 'Triangle', width=7, height=5)
            self.paint(arrow, 'FFB8C9DD')
            glow = self.el(arm, 'Node', opacity=0.06, name=name+' navigation glow')
            self.rect(glow, 0, -12, 13, 2, VIOLET, 1)
            halo = self.rect(glow, 0, -12, 13, 2, VIOLET, 1)
            self.paint(halo, VIOLET, 4, 7)
            self.rect(arm, 0, 0, 23, 30, 'FF283549', 3)
            self.animate(a, sm, name+'Pressed', [(glow.get('id'), 'glow')])
        self.ellipse(pad, 0, 0, 7, 'FF101827')
        self.rect(pad, 0, 0, 28, 28, 'FF283549', 2)
        self.rect(pad, 0, 2, 32, 84, 'FF070D18', 4)
        self.rect(pad, 0, 2, 84, 32, 'FF070D18', 4)
        return dict(inputs=dict(up='up', down='down', left='left', right='right'),
                    frame=dict(x=x-44, y=y-44, width=88, height=88))

    def stick(self, a, sm, x, y):
        socket = self.el(a, 'Node', x=x, y=y, name='Orbit analog instrument')
        cap = self.el(socket, 'Node', name='Continuous XY cap')
        self.numeric(cap, 13, 'stickX', -27, 27, -1, 1)
        self.numeric(cap, 14, 'stickY', 27, -27, -1, 1)
        # The cap, its luminous core and the tracking halo move as one vector group.
        self.ellipse(cap, 0, 0, 7, 'FFD5FFFF')
        self.ellipse(cap, 0, 0, 14, CYAN, 1)
        for i in range(3):
            self.rect(cap, 0, 12+i*3, 14-i*4, 0.7, 'FF52657A')
        self.ellipse(cap, 0, 0, 46, 'FF455B72', 1)
        self.ellipse(cap, 0, 0, 46, 'FF24364B')
        self.ellipse(cap, 0, 3, 51, 'FF050B16')
        halo = self.el(cap, 'Node', name='Magnitude driven feather halo')
        self.numeric(halo, 18, 'stickMagnitude', 0.08, 1)
        self.ellipse(halo, 0, 0, 58, CYAN, 1.5)
        self.ellipse(halo, 0, 0, 60, CYAN, 5, 11)
        # Independent sectors make cardinal and diagonal values visible at a glance.
        for i, direction in enumerate(['Up', 'Right', 'Down', 'Left']):
            theta = i*math.pi/2
            sector = self.el(socket, 'Node', x=math.sin(theta)*60,
                             y=-math.cos(theta)*60, rotation=theta,
                             opacity=0.06, name=direction+' axis sector')
            self.rect(sector, 0, 0, 19, 2, CYAN, 1)
            light = self.rect(sector, 0, 0, 19, 2, CYAN, 1)
            self.paint(light, CYAN, 4, 9)
            self.animate(a, sm, 'analogStick'+direction+'Pressed', [(sector.get('id'), 'glow')])
        ring = self.el(socket, 'Node', name='Radial magnitude light')
        self.numeric(ring, 18, 'stickMagnitude', 0.08, 0.85)
        self.ellipse(ring, 0, 0, 115, CYAN, 1)
        self.ellipse(ring, 0, 0, 116, CYAN, 3, 8)
        for i in range(48):
            theta = i*math.pi/24
            tick = self.el(socket, 'Node', x=math.cos(theta)*72,
                           y=math.sin(theta)*72, rotation=theta)
            self.rect(tick, 0, 0, 5 if i%6==0 else 2, 0.8,
                      'FF8290AD' if i%6==0 else 'FF34435A')
        self.ellipse(socket, 0, 0, 158, 'FF3B4B68', 1)
        self.ellipse(socket, 0, 0, 150, 'FF101A2D')
        self.ellipse(socket, 0, 0, 99, 'FF24354F', 1)
        self.ellipse(socket, 0, 0, 96, 'FF080F20')
        return dict(inputs={d.lower():'analogStick'+d for d in ['Up','Down','Left','Right']},
                    frame=dict(x=x-72, y=y-72, width=144, height=144),
                    thumbstick=dict(name='stick.pdf', width=51, height=51))

    def artboard(self, orientation):
        portrait = orientation == 'portrait'
        w, h = (390,400) if portrait else (844,390)
        a = self.el(self.root, 'Artboard', name=orientation.title(), width=w, height=h,
                    viewModelId=self.vm, viewModelInstanceId=self.instance,
                    x=0 if portrait else 460)
        style = self.el(a, 'LayoutComponentStyle')
        a.set('styleId', style.get('id'))
        sm = self.el(a, 'StateMachine', name='Controller')
        a.set('defaultStateMachineId', sm.get('id'))
        self.text(a, 24, 27, 'O R B I T' if portrait else 'ORBIT', 19, 'FFE1EBFF')
        self.text(a, 25, 48, 'ANALOG FLIGHT SYSTEM / N64' if portrait else 'FLIGHT / N64', 7)
        if portrait:
            self.text(a, 364, 28, '64', 19, VIOLET, True)
            self.text(a, 106, 272, 'VECTOR / 360', 7, center=True)
            self.text(a, 307, 223, 'C / NAVIGATION', 7, center=True)
        items = [self.stick(a, sm, 106 if portrait else 105, 180 if portrait else 173),
                 self.dpad(a, sm, 90 if portrait else 95, 324 if portrait else 312)]
        cx, cy = (307,165) if portrait else (745,140)
        for direction, dx, dy, label in [('Up',0,-33,'▲'),('Down',0,33,'▼'),('Left',-33,0,'◀'),('Right',33,0,'▶')]:
            # ASCII labels stay within the bundled font's glyph set.
            label = {'Up':'CU','Down':'CD','Left':'CL','Right':'CR'}[direction]
            items.append(self.button(a, sm, 'c'+direction, cx+dx, cy+dy, 36, 36, GOLD, label, True))
        positions = [('a',323,262,56,56,CYAN,'A',True),
                     ('b',253,298,46,46,VIOLET,'B',True),
                     ('l',44,83,60,20,VIOLET,'L',False),
                     ('r',346,83,60,20,VIOLET,'R',False),
                     ('z',194,88,52,24,'FFFF9F7C','Z',False),
                     ('start',199,356,52,18,CYAN,'START',False),
                     ('menu',40,378,38,16,VIOLET,'MENU',False)] if portrait else [
                     ('a',779,241,52,52,CYAN,'A',True),
                     ('b',708,275,46,46,VIOLET,'B',True),
                     ('l',55,65,60,20,VIOLET,'L',False),
                     ('r',782,49,60,20,VIOLET,'R',False),
                     ('z',179,347,36,24,'FFFF9F7C','Z',False),
                     ('start',422,369,52,18,CYAN,'START',False),
                     ('menu',422,20,38,16,VIOLET,'MENU',False)]
        items += [self.button(a, sm, *p) for p in positions]
        # Button hit extensions must not bleed into adjacent C-buttons or the game.
        for item in items:
            if isinstance(item['inputs'], list):
                item['extendedEdges'] = dict(top=3,bottom=3,left=3,right=3)
        if portrait:
            for x in range(157,232,8):
                self.rect(a,x,384,3,1,'FF425375')
            self.rect(a,w/2,2,w,2,CYAN)
            self.rect(a,w/2,h/2,w,h,'FF0E1627')
        else:
            self.rect(a,102,h/2,204,h,'FF0E1627',18)
            self.rect(a,w-102,h/2,204,h,'FF0E1627',18)
            self.rect(a,w/2,17,84,34,'FF0E1627',14)
            self.rect(a,w/2,h-19,w-408,38,'FF0E1627',14)
        rep = dict(assets=dict(resizable=orientation+'.pdf'), mappingSize=dict(width=w,height=h), items=items)
        if not portrait:
            rep['screens'] = [dict(outputFrame=dict(x=218,y=40,width=408,height=306))]
        return rep


def generate():
    path = ROOT/'Orbit'
    path.mkdir(exist_ok=True)
    scene = Orbit()
    reps = {o:scene.artboard(o) for o in ['portrait','landscape']}
    (path/'scene.rml').write_text(scene.finish())
    (path/'rive.yaml').write_text('name: Orbit\nmain: Portrait\n')
    info = dict(name='Orbit N64', identifier='com.delta.rive.orbit.n64',
                gameTypeIdentifier='com.rileytestut.delta.game.n64', debug=False,
                representations=dict(iphone=dict(standard=reps,edgeToEdge=reps)))
    (path/'info.json').write_text(json.dumps(info,indent=2)+'\n')
    manifest = dict(schemaVersion=1, representations={
        f'iphone-{display}-{orientation}':dict(file='Orbit.riv',artboard=orientation.title(),
            stateMachine='Controller',viewModel='Controller',buttons={b:b+'Pressed' for b in BUTTONS},
            sticks=[dict(up='analogStickUp',down='analogStickDown',left='analogStickLeft',right='analogStickRight',
                         x='stickX',y='stickY',active='stickActive',magnitude='stickMagnitude')],reduceMotion='reduceMotion')
        for display in ['standard','edgeToEdge'] for orientation in reps})
    (path/'rive.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    generate()
