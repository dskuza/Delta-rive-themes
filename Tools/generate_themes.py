#!/usr/bin/env python3
"""Generate editable, script-free RML and matching Delta native hit targets.

All coordinates originate here. Run build_themes.py to compile and package.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BUTTONS = ['up', 'down', 'left', 'right', 'a', 'b', 'start', 'select', 'menu']

class Scene:
    def __init__(self, showcase, analog=False):
        self.root = ET.Element('Rive', version='1', kind='fragment')
        self.counter = 100
        self.showcase = showcase
        self.analog = analog
        self.vm, self.instance = '0:1', '0:2'
        self.properties = {n: f'0:{i + 3}' for i, n in enumerate(
            [b + 'Pressed' for b in BUTTONS] + ['reduceMotion'] + (['stickActive', 'stickX', 'stickY'] if analog else []))}
        self.color = 'FF65E7D4' if showcase else 'FF76A8FF'
        self.font = self.el(self.root, 'FontAsset', file='../Assets/SpaceGrotesk.ttf', name='Space Grotesk').get('id')

    def el(self, parent, tag, **attrs):
        if 'id' not in attrs:
            self.counter += 1
            attrs['id'] = f'0:{self.counter}'
        return ET.SubElement(parent, tag, {k: str(v).lower() if isinstance(v, bool) else str(v) for k,v in attrs.items()})

    def paint(self, parent, color, stroke=0, feather=0):
        p = self.el(parent, 'Stroke' if stroke else 'Fill', name='Glow' if feather else 'Paint', **({'thickness':stroke} if stroke else {}))
        self.el(p, 'SolidColor', name='Color', colorValue=color)
        if feather:
            self.el(p, 'Feather', name='Vector feather', strength=feather)

    def rect(self, parent, x,y,w,h,color, radius=0, stroke=0, name='Panel'):
        s=self.el(parent,'Shape',x=x,y=y,name=name)
        self.el(s,'Rectangle',width=w,height=h,originX=0.5,originY=0.5,cornerRadiusTL=radius,cornerRadiusTR=radius,cornerRadiusBL=radius,cornerRadiusBR=radius,name='Path')
        self.paint(s,color,stroke)
        return s

    def ellipse(self,parent,x,y,d,color,stroke=0,feather=0,name='Ring'):
        s=self.el(parent,'Shape',x=x,y=y,name=name)
        self.el(s,'Ellipse',width=d,height=d,name='Path')
        self.paint(s,color,stroke,feather)
        return s

    def text(self,parent,x,y,text,size=12,color='FF80909F',center=False):
        t=self.el(parent,'Text',x=x,y=y,name=text,originX=0.5 if center else 0,originY=0.5,sizingValue='autoWidth')
        style=self.el(t,'TextStylePaint',fontSize=size,fontAssetId=self.font,familyName='Space Grotesk',styleName='Regular',letterSpacing=1.2 if size<14 else 0,name='Label')
        self.paint(style,color)
        self.el(t,'TextValueRun',styleId=style.get('id'),text=text,name='Text')

    def bind(self,parent,key,prop,converter=None):
        return self.el(parent,'DataBindContext',sourcePathIds=f'{self.vm}-{self.properties[prop]}',propertyKey=key,**({'converterId':converter} if converter else {}))

    def condition(self,transition,prop,value):
        c=self.el(transition,'TransitionViewModelCondition',opValue='equal')
        cmp=self.el(c,'TransitionPropertyViewModelComparator')
        bp=self.el(cmp,'BindablePropertyBoolean')
        self.bind(bp,634,prop)
        self.el(c,'TransitionValueBooleanComparator',value=value)

    def animate(self,artboard,machine,prop,targets):
        """Three states: released, pressed, and a reduced-motion pressed pose."""
        animations=[]
        for label,pressed,motion in [('Rest',False,False),('Press',True,True),('Still',True,False)]:
            anim=self.el(artboard,'LinearAnimation',duration=1,name=f'{prop} {label}')
            for object_id,kind in targets:
                values={18:1 if pressed else 0.06} if kind=='glow' else {16:0.94 if motion else 1,17:0.94 if motion else 1}
                ko=self.el(anim,'KeyedObject',objectId=object_id)
                for key,value in values.items():
                    kp=self.el(ko,'KeyedProperty',propertyKey=key)
                    self.el(kp,'KeyFrameDouble',value=value,interpolationType='linear')
            animations.append(anim.get('id'))
        layer=self.el(machine,'StateMachineLayer',name=prop)
        states=[self.el(layer,'AnimationState',animationId=a,x=160+i*180,y=[0,-100,100][i]) for i,a in enumerate(animations)]
        entry=self.el(layer,'EntryState',x=0,y=0)
        self.el(entry,'StateTransition',stateToId=states[0].get('id'))
        self.el(layer,'AnyState',x=600,y=-180)
        self.el(layer,'ExitState',x=780,y=-180)
        for i,state in enumerate(states):
            if i==0:
                for j,reduced in [(1,False),(2,True)]:
                    tr=self.el(state,'StateTransition',stateToId=states[j].get('id'),duration=45 if j==1 else 0)
                    self.condition(tr,prop,True);self.condition(tr,'reduceMotion',reduced)
            else:
                tr=self.el(state,'StateTransition',stateToId=states[0].get('id'),duration=110 if i==1 else 0)
                self.condition(tr,prop,False)
                tr=self.el(state,'StateTransition',stateToId=states[3-i].get('id'),duration=0)
                self.condition(tr,'reduceMotion',i==1)

    def button(self,a,sm,name,x,y,w,h,color,label=None,round=False):
        # Sibling source order is front to back in Rive.
        cap=self.el(a,'Node',x=x,y=y,name=f'{name} cap')
        self.text(cap,0,0,label or name.upper(),20 if round else 9,'FFDAE5EF',True)
        if round:
            self.ellipse(cap,0,0,w-5,'FF28313F')
            self.ellipse(cap,0,2,w,'FF0C111B')
        else:
            self.rect(cap,0,0,w,h,'FF263240',h/2)
            self.rect(cap,0,2,w+2,h+2,'FF090E17',h/2)
        glow=self.el(a,'Node',x=x,y=y,opacity=0.06,name=f'{name} LED')
        if round:
            self.ellipse(glow,0,0,w+8,color,2)
            self.ellipse(glow,0,0,w+10,color,7,13)
        else:
            s=self.rect(glow,0,0,w+7,h+7,color,h/2,2)
            self.paint(s,color,5,10)
        self.animate(a,sm,name+'Pressed',[(glow.get('id'),'glow'),(cap.get('id'),'cap')])
        return {'inputs':[name],'frame':{'x':x-w/2,'y':y-h/2,'width':w,'height':h},'extendedEdges':{'top':7,'bottom':7,'left':7,'right':7},'mask':'circle' if round else 'rectangle'}

    def artboard(self,orientation):
        portrait=orientation=='portrait'; w,h=(390,330) if portrait else (844,390)
        a=self.el(self.root,'Artboard',width=w,height=h,name=orientation.title(),viewModelId=self.vm,viewModelInstanceId=self.instance,x=0 if portrait else 460,y=0)
        style=self.el(a,'LayoutComponentStyle',name='Artboard Style');a.set('styleId',style.get('id'))
        sm=self.el(a,'StateMachine',name='Controller');a.set('defaultStateMachineId',sm.get('id'))
        cx,cy=(100,158) if portrait else (105,207)
        items=[]
        if portrait:
            self.text(a,25,29,'ANALOG / LAB' if self.analog else ('NEON / CIRCUIT' if self.showcase else 'CONTROLLER / TEMPLATE'),18,'FFDCE9ED')
            self.text(a,25,52,'CONTINUOUS INPUT   /   X + Y' if self.analog else 'VECTOR INPUT SYSTEM   /   NES',8)
            for i in range(4):self.rect(a,334+i*8,27,3,9,self.color if i<3 else 'FF2B3845',1)
        else:
            self.text(a,29,37,'NEON' if self.showcase else 'VECTOR',15,'FFDCE9ED')
            self.text(a,29,56,'CIRCUIT / NES' if self.showcase else 'TEMPLATE / NES',8)
        ax,ay=(326,141) if portrait else (763,173)
        bx,by=(253,178) if portrait else (692,226)
        items += [self.button(a,sm,'a',ax,ay,55,55,'FFFF9F66',round=True),self.button(a,sm,'b',bx,by,55,55,'FFE88BDB',round=True)]
        sy=265 if portrait else 350
        items += [self.button(a,sm,'select',153 if portrait else 337,sy,48,16,self.color,'SELECT'),self.button(a,sm,'start',233 if portrait else 507,sy,48,16,self.color,'START')]
        items += [self.button(a,sm,'menu',40 if portrait else 422,292 if portrait else 20,34,15,self.color,'MENU')]
        self.text(a,366 if portrait else 796,305 if portrait else 354,'AXIS / XY' if self.analog else '01 / NES',8,center=True)
        if self.analog:
            # Stick cap displacement is data-bound, not a bitmap or scripted drawable.
            stick=self.el(a,'Node',x=cx,y=cy,name='Stick socket')
            moving=self.el(stick,'Node',name='Stick cap')
            for prop,key,out in [('stickX',13,22),('stickY',14,-22)]:
                conv=self.el(self.root,'DataConverterRangeMapper',minInput=-1,maxInput=1,minOutput=-out,maxOutput=out,clampLower=True,clampUpper=True,name=prop+' travel')
                self.bind(moving,key,prop,conv.get('id'))
            self.ellipse(moving,0,0,9,self.color)
            for i in range(5):self.rect(moving,0,-8+i*4,18 if i in (1,2,3) else 10,0.7,'FF3C4D5A')
            self.ellipse(moving,0,0,54,'FF283744',1)
            self.ellipse(moving,0,0,55,'FF17212E')
            self.ellipse(moving,0,3,58,'FF090F18')
            tracking=self.el(stick,'Node',opacity=0.06,name='Tracking halo')
            self.ellipse(tracking,0,0,73,self.color,2)
            self.ellipse(tracking,0,0,76,self.color,6,12)
            self.animate(a,sm,'stickActive',[(tracking.get('id'),'glow')])
            # Four independently lit sectors show diagonals and rotation.
            for i,name in enumerate(['up','right','down','left']):
                dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][i]
                node=self.el(stick,'Node',x=dx*53,y=dy*53,rotation=i*math.pi/2,opacity=0.06,name=name+' light')
                self.rect(node,0,0,24,3,self.color,1.5)
                s=self.rect(node,0,0,25,3,self.color,1.5)
                self.paint(s,self.color,4,9)
                self.animate(a,sm,name+'Pressed',[(node.get('id'),'glow')])
            # Tick marks make the control read as a physical, machined component.
            if self.showcase:
                for i in range(40):
                    theta=i*math.pi/20
                    n=self.el(stick,'Node',x=math.cos(theta)*65,y=math.sin(theta)*65,rotation=theta,name=f'Index {i:02}')
                    self.rect(n,0,0,5 if i%5==0 else 2,1,'FF50616C' if i%5==0 else 'FF293642')
            self.ellipse(stick,0,0,157,'FF263541',1)
            self.ellipse(stick,0,0,148,'FF0A111B')
            self.text(a,cx,cy+91,'DIRECTION / 360',8,center=True)
            items.insert(0,{'inputs':dict(up='up',down='down',left='left',right='right'),'frame':{'x':cx-76,'y':cy-76,'width':152,'height':152},'thumbstick':{'name':'stick.pdf','width':56,'height':56}})
        else:
            # NES has a digital D-pad. Native DeltaCore D-pad hit testing handles
            # cardinal directions, diagonal chords, sliding and simultaneous A/B.
            pad=self.el(a,'Node',x=cx,y=cy,name='NES D-pad')
            for i,name in enumerate(['up','right','down','left']):
                dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][i]
                arm=self.el(pad,'Node',x=dx*40,y=dy*40,rotation=i*math.pi/2,name=name+' arm')
                arrow=self.el(arm,'Shape',y=-3,name='Engraved direction')
                self.el(arrow,'Triangle',width=10,height=7,name='Arrow')
                self.paint(arrow,'FF8196A7')
                cap=self.rect(arm,0,0,35,44,'FF293746',4)
                glow=self.el(arm,'Node',opacity=0.06,name=name+' LED')
                self.rect(glow,0,-18,20,3,self.color,1.5)
                halo=self.rect(glow,0,-18,20,3,self.color,1.5)
                self.paint(halo,self.color,5,10)
                arm.remove(cap); arm.append(cap)
                self.animate(a,sm,name+'Pressed',[(glow.get('id'),'glow')])
            self.ellipse(pad,0,0,12,'FF111B28')
            self.rect(pad,0,0,44,44,'FF293746',3)
            self.rect(pad,0,2,48,124,'FF080E17',6)
            self.rect(pad,0,2,124,48,'FF080E17',6)
            self.text(a,cx,cy+91,'DIGITAL / D-PAD',8,center=True)
            if self.showcase:
                for i in range(8):
                    self.rect(a,cx-30+i*8,cy+110,3,1,self.color if i<4 else 'FF293642')
            items.insert(0,{'inputs':dict(up='up',down='down',left='left',right='right'),
                            'frame':{'x':cx-66,'y':cy-66,'width':132,'height':132}})
        # Decorative panel traces are simple vectors, with no baked glow images.
        if self.showcase:
            for i in range(5):
                self.rect(a,30+i*8,78,1,10+i*4,'FF263945',0)
                self.rect(a,w-30-i*8,h-55,1,10+i*4,'FF263945',0)
        if portrait:
            self.rect(a,w/2,h-1,w-48,1,'FF26313E')
            self.rect(a,w/2,2,w,3,self.color)
            self.rect(a,w/2,h/2,w,h,'FF111B28',0)
        else:
            self.rect(a,105,h/2,210,h,'FF111B28',20)
            self.rect(a,w-105,h/2,210,h,'FF111B28',20)
            self.rect(a,w/2,h-17,w-400,34,'FF111B28',16)
            self.rect(a,w/2,17,84,34,'FF111B28',14)
        rep={'assets':{'resizable':orientation+'.pdf'},'mappingSize':{'width':w,'height':h},'items':items}
        if not portrait:rep['screens']=[{'outputFrame':{'x':218,'y':40,'width':408,'height':306}}]
        return rep

    def finish(self):
        vm=self.el(self.root,'ViewModel',id=self.vm,name='Controller',defaultInstanceId=self.instance)
        for name,pid in self.properties.items():
            self.el(vm,'ViewModelPropertyNumber' if name in ('stickX','stickY') else 'ViewModelPropertyBoolean',name=name,id=pid)
        instance=self.el(vm,'ViewModelInstance',id=self.instance,name='Default',exports=True)
        for name,pid in self.properties.items():
            number=name in ('stickX','stickY')
            self.el(instance,'ViewModelInstanceNumber' if number else 'ViewModelInstanceBoolean',viewModelPropertyId=pid,propertyValue=0 if number else False)
        ET.indent(self.root,space='    ')
        return ET.tostring(self.root,encoding='unicode')+'\n'


def generate(name,showcase):
    path=ROOT/name; path.mkdir(exist_ok=True)
    scene=Scene(showcase)
    reps={o:scene.artboard(o) for o in ['portrait','landscape']}
    (path/'scene.rml').write_text(scene.finish())
    (path/'rive.yaml').write_text(f'name: {name}\nmain: Portrait\n')
    info={'name':'Neon Circuit NES' if showcase else 'Rive NES Template','identifier':'com.delta.rive.'+name.lower()+'.nes','gameTypeIdentifier':'com.rileytestut.delta.game.nes','debug':False,'representations':{'iphone':{'standard':reps,'edgeToEdge':reps}}}
    (path/'info.json').write_text(json.dumps(info,indent=2)+'\n')
    bindings={b:b+'Pressed' for b in BUTTONS}
    manifest={'schemaVersion':1,'representations':{f'iphone-{display}-{orientation}':{'file':name+'.riv','artboard':orientation.title(),'stateMachine':'Controller','viewModel':'Controller','buttons':bindings,'sticks':[dict(up='up',down='down',left='left',right='right',x='stickX',y='stickY',active='stickActive')],'reduceMotion':'reduceMotion'} for display in ['standard','edgeToEdge'] for orientation in reps}}
    for representation in manifest['representations'].values():
        representation.pop('sticks')
    (path/'rive.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':
    generate('Template',False)
    generate('NeonCircuit',True)
    path=ROOT/'AnalogStickLab'
    path.mkdir(exist_ok=True)
    lab=Scene(True,analog=True)
    lab.artboard('portrait')
    (path/'scene.rml').write_text(lab.finish())
    (path/'rive.yaml').write_text('name: AnalogStickLab\nmain: Portrait\n')
