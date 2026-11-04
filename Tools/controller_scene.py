#!/usr/bin/env python3
"""Shared RML primitives and typed view-model authoring for the two controllers."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NES_BUTTONS = ['up', 'down', 'left', 'right', 'a', 'b', 'start', 'select', 'menu']

class Scene:
    def __init__(self, showcase, analog=False, buttons=None, numbers=None):
        self.root = ET.Element('Rive', version='1', kind='fragment')
        self.counter = 100
        self.showcase = showcase
        self.analog = analog
        self.vm, self.instance = '0:1', '0:2'
        self.numbers = numbers if numbers is not None else (['stickX', 'stickY'] if analog else [])
        self.properties = {n: f'0:{i + 3}' for i, n in enumerate(
            [b + 'Pressed' for b in (buttons if buttons is not None else NES_BUTTONS)] + ['reduceMotion'] + (['stickActive'] if analog else []) + self.numbers)}
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

    def finish(self):
        vm=self.el(self.root,'ViewModel',id=self.vm,name='Controller',defaultInstanceId=self.instance)
        for name,pid in self.properties.items():
            self.el(vm,'ViewModelPropertyNumber' if name in self.numbers else 'ViewModelPropertyBoolean',name=name,id=pid)
        instance=self.el(vm,'ViewModelInstance',id=self.instance,name='Default',exports=True)
        for name,pid in self.properties.items():
            number=name in self.numbers
            self.el(instance,'ViewModelInstanceNumber' if number else 'ViewModelInstanceBoolean',viewModelPropertyId=pid,propertyValue=0 if number else False)
        ET.indent(self.root,space='    ')
        return ET.tostring(self.root,encoding='unicode')+'\n'


N64_BUTTONS = ['up', 'down', 'left', 'right', 'analogStickUp', 'analogStickDown',
           'analogStickLeft', 'analogStickRight', 'cUp', 'cDown', 'cLeft', 'cRight',
           'a', 'b', 'l', 'r', 'z', 'start', 'menu']
CYAN = 'FF63E8F1'
DIRECTIONS = ['Up', 'Right', 'Down', 'Left']


class AnalogScene(Scene):
    def __init__(self):
        super().__init__(True, analog=True, buttons=N64_BUTTONS,
                         numbers=['stickX', 'stickY', 'stickMagnitude'])
        self.color = CYAN

    def numeric(self, target, key, prop, low, high, minimum=0, maximum=1):
        converter = self.el(self.root, 'DataConverterRangeMapper', minInput=minimum,
                            maxInput=maximum, minOutput=low, maxOutput=high,
                            clampLower=True, clampUpper=True, name=prop+' mapping')
        self.bind(target, key, prop, converter.get('id'))
