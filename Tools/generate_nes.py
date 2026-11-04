#!/usr/bin/env python3
"""NES: the clear circuit material with the original gray/black/red palette."""
import copy
import json
from controller_scene import ROOT, Scene, NES_BUTTONS as BUTTONS
from generate_n64 import CircuitController, CAP_COLORS, ICE, RED
from default_layout import layout_for


class NESController(CircuitController):
    cap_colors={**CAP_COLORS,'a':CAP_COLORS['start'],'b':CAP_COLORS['start'],
                'start':CAP_COLORS['neutral']}
    dpad_led=RED

    def __init__(self):
        Scene.__init__(self,True,buttons=BUTTONS)
        self.material_counter=900000
        self.circuits={}

    def artboard(self,orientation):
        portrait=orientation=='portrait'
        w,h,controls=layout_for('NES',orientation)
        a=self.el(self.root,'Artboard',name=orientation.title(),width=w,height=h,
                  viewModelId=self.vm,viewModelInstanceId=self.instance,x=0 if portrait else 460)
        style=self.el(a,'LayoutComponentStyle')
        a.set('styleId',style.get('id'))
        sm=self.el(a,'StateMachine',name='Controller')
        a.set('defaultStateMachineId',sm.get('id'))
        dx,dy,dw,dh=controls['pad']
        scale=dw/88
        items=[self.placed_pad(a,sm,controls['pad'])]
        buttons=[]
        for name in ['b','a','select','start','menu']:
            x,y,bw,bh=controls[name]
            buttons.append((name,x,y,bw,bh,RED if name in ['a','b'] else ICE,name.upper(),name in ['a','b']))
        for button in buttons:
            items.append(self.button(a,sm,*button))
        panels=[(195,h/2,382,h-8)] if portrait else [(102,195,196,382),(742,195,196,382)]
        for px,py,pw,ph in panels:
            self.glass(a,px,py,pw,ph,20)
        headers=[] if portrait else [(422,25,106,42),(422,367,208,38)]
        for header in headers:
            self.glass(a,*header,16)
        chips=[(195,54)] if portrait else [(180,120),(664,120)]
        for cx,cy in chips:
            self.chip(a,cx,cy,system='NES')
        for px,py,pw,ph in panels:
            for sx in [-pw/2+12,pw/2-12]:
                for sy in [-ph/2+13,ph/2-13]:
                    self.screw(a,px+sx,py+sy)
            for i in range(8):
                self.rect(a,px-pw/2+12+i*7,py+ph/2-24,3,5,'FF516D72',.5,name='SMT array')
        traces=[]
        for index,(name,bx,by,bw,bh,color,*_) in enumerate(buttons):
            if name=='menu':
                continue
            if portrait:
                lane=220+index*6
                points=[(bx,by),(lane,by),(lane,91+index*4),(203,67),(195,54),(195,5)]
            elif name in ['select','start']:
                points=[(bx,by),(bx,347)]
            else:
                lane=678+index*6
                points=[(bx,by),(lane,by),(lane,139),(664,120),(627,120)]
            self.signal(a,sm,name+'Pressed',points,color,name.upper())
            traces.append(dict(name=name,points=points,color=color))
        for i,name in enumerate(['up','right','down','left']):
            ox,oy=[(0,-26),(26,0),(0,26),(-26,0)][i]
            lane=151+i*4 if portrait else 157+i*4
            chip=chips[0]
            points=[(dx+ox*scale,dy+oy*scale),(lane,dy+oy*scale),
                    (lane,88 if portrait else 142),chip,(195,5) if portrait else (217,120)]
            self.signal(a,sm,name+'Pressed',points,RED,'DPAD '+name.upper())
            traces.append(dict(name=name,points=points,color=RED))
        for px,py,pw,ph in panels:
            board=self.rect(a,px,py,pw-9,ph-9,'FF3A515D',16,.5,name='PCB edge')
            self.gradient(board,['FF14262E','FF0C1C26'],ph/2)
        if portrait:
            self.rect(a,w/2,h/2,w,h,'FF07131E',name='Backdrop')
        self.circuits[orientation]=dict(panels=panels,headers=headers,chips=chips,traces=traces)
        rep=dict(assets=dict(resizable=orientation+'.pdf'),mappingSize=dict(width=w,height=h),items=items)
        if not portrait:
            rep['screens']=[dict(outputFrame=dict(x=234,y=53,width=376,height=282))]
        return rep


def generate():
    path=ROOT/'nes'
    path.mkdir(exist_ok=True)
    scene=NESController()
    reps={o:scene.artboard(o) for o in ['portrait','landscape']}
    edge=copy.deepcopy(reps)
    for rep in edge.values():
        rep['respectsSafeArea']=True
    info=dict(name='NES',identifier='com.dskuza.delta.rive.nes',
              gameTypeIdentifier='com.rileytestut.delta.game.nes',debug=False,
              representations=dict(iphone=dict(standard=reps,edgeToEdge=edge)))
    manifest=dict(schemaVersion=1,representations={
        f'iphone-{display}-{orientation}':dict(file='nes.riv',artboard=orientation.title(),
            stateMachine='Controller',viewModel='Controller',buttons={b:b+'Pressed' for b in BUTTONS},
            reduceMotion='reduceMotion',preview=orientation+'-preview.png')
        for display in ['standard','edgeToEdge'] for orientation in reps})
    (path/'scene.rml').write_text(scene.finish())
    (path/'rive.yaml').write_text('name: nes\nmain: Portrait\n')
    (path/'info.json').write_text(json.dumps(info,indent=2)+'\n')
    (path/'rive.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (path/'circuit-layout.json').write_text(json.dumps(scene.circuits,indent=2)+'\n')


if __name__=='__main__':
    generate()
