#!/usr/bin/env python3
"""Orbit: Crystal — transparent vector shell, visible PCB, live signal traces."""
import copy
import json
import math
from generate_themes import ROOT
from generate_orbit import Orbit, BUTTONS, DIRECTIONS

ICE, MINT, BLUE, GREEN, GOLD, RED = ('FFCCD0D5','FF73F2D0','FF4B9CFF',
                                    'FF63D393','FFFFD23C','FFFF5C64')

# N64 hues use the original clear material's alpha levels, rather than solid caps.
CAP_COLORS = {
    'a': ['544D96E5','0D2567BB','1E16428A'],
    'b': ['544BB579','0D148649','1E075A30'],
    'c': ['54FFE783','0DEBC02F','1EAA8118'],
    'start': ['54F27A7F','0DD83844','1E96232F'],
    'neutral': ['54A4ABB4','0D737D88','1E56616E'],
}


class Crystal(Orbit):
    def __init__(self):
        super().__init__()
        self.properties['stickContact']='0:99'
        self.circuits={}
        self.material_counter=900000

    def gradient(self, shape, colors, extent, radial=False, new_ids=False):
        def element(parent,tag,**attrs):
            if new_ids:
                self.material_counter+=1
                attrs['id']=f'0:{self.material_counter}'
            return self.el(parent,tag,**attrs)
        paint=element(shape,'Fill',name='Transparent material')
        grad=element(paint,'RadialGradient' if radial else 'LinearGradient',
                     startX=-extent*.4,startY=-extent*.6,endX=extent*.5,endY=extent,
                     name='Clear polycarbonate')
        for i,color in enumerate(colors):
            element(grad,'GradientStop',colorValue=color,position=i/(len(colors)-1))

    def path(self, parent, points, color, width=1, name='Copper trace'):
        shape=self.el(parent,'Shape',name=name)
        path=self.el(shape,'PointsPath',isClosed=False,name='Routed path')
        for x,y in points:
            self.el(path,'StraightVertex',x=x,y=y,radius=3)
        paint=self.el(shape,'Stroke',thickness=width,cap='round',join='round')
        self.el(paint,'SolidColor',colorValue=color)
        return shape,path,paint

    def timeline(self, artboard, name, tracks, duration=48, loop='oneShot'):
        animation=self.el(artboard,'LinearAnimation',name=name,duration=duration,loopValue=loop)
        for obj,key,frames in tracks:
            target=self.el(animation,'KeyedObject',objectId=obj.get('id'))
            prop=self.el(target,'KeyedProperty',propertyKey=key)
            for frame,value in frames:
                self.el(prop,'KeyFrameDouble',frame=frame,value=value,interpolationType='linear')
        return animation

    def signal(self, artboard, machine, prop, points, color, name):
        """Held signals repeatedly travel into the display; reduced motion stays lit."""
        active=self.el(artboard,'Node',name=name+' / signal',opacity=0)
        _,_,stroke=self.path(active,points,color,1.65,'Moving data packet')
        trim=self.el(stroke,'TrimPath',start=0,end=.17,name='Packet travel')
        # A faint complete route makes source and destination readable while held.
        route=self.el(active,'Node',opacity=.2,name='Powered copper')
        self.path(route,points,color,.8)
        self.path(artboard,points,'FF29464E',.7,name+' / unpowered route')
        animations=[
            self.timeline(artboard,name+' / idle',[(active,18,[(0,0)]),(trim,114,[(0,0)]),(trim,115,[(0,.17)])]),
            self.timeline(artboard,name+' / transmitting',[
                (active,18,[(0,1)]),(trim,114,[(0,0),(48,.98)]),(trim,115,[(0,.17),(48,1.15)])],loop='loop'),
            self.timeline(artboard,name+' / reduced motion',[
                (active,18,[(0,.85)]),(trim,114,[(0,0)]),(trim,115,[(0,1)])])]
        layer=self.el(machine,'StateMachineLayer',name=name+' / bus')
        states=[self.el(layer,'AnimationState',animationId=a.get('id'),reset=True,
                        x=180+i*180,y=[0,-100,100][i]) for i,a in enumerate(animations)]
        entry=self.el(layer,'EntryState',x=0,y=0)
        self.el(entry,'StateTransition',stateToId=states[0].get('id'))
        self.el(layer,'AnyState',x=0,y=-200)
        self.el(layer,'ExitState',x=800,y=-200)
        for source in [0,1,2]:
            for destination in [0,1,2]:
                if source==destination:
                    continue
                tr=self.el(states[source],'StateTransition',stateToId=states[destination].get('id'),
                           duration=100 if destination==0 else 0,
                           **(dict(enableExitTime=True,exitTimeIsPercetange=True,exitTime=100)
                              if source==1 and destination==0 else {}))
                self.condition(tr,prop,destination!=0)
                if destination:
                    self.condition(tr,'reduceMotion',destination==2)

    def glass(self,parent,x,y,w,h,radius=12):
        # Details sit under the shell's translucent highlight, like a clear controller.
        shell=self.rect(parent,x,y,w,h,'158C939B',radius,.8,name='Clear shell / edge')
        self.gradient(shell,['37919DA6','0D6B7B85','1D75838F'],max(w,h)/2)
        self.rect(parent,x,y,w-4,h-4,'167B848E',max(radius-2,0),.5,name='Inner shell refraction')
        return shell

    def screw(self,parent,x,y):
        self.path(parent,[(x-1.8,y+1.8),(x+1.8,y-1.8)],'FF97B5BD',.7,'Screw slot')
        self.ellipse(parent,x,y,7,'FF8BA5AE',.8,name='Steel screw')
        self.ellipse(parent,x,y,4,'FF263C47',name='Screw recess')

    def chip(self,parent,x,y,label='INPUT'):
        self.text(parent,x,y-3,label,6.5,'FFA5C5C8',True)
        self.text(parent,x,y+6,'N64',5,'FF60838D',True)
        self.rect(parent,x,y,31,25,'FF101F2A',3,name='Input encoder')
        for i in range(6):
            for side in [-1,1]:
                self.rect(parent,x+side*18,y-9+i*3.5,5,1,'FF789198',.4,name='Exposed IC pin')

    def button(self,a,sm,name,x,y,w,h,color,label=None,round=False):
        cap=self.el(a,'Node',x=x,y=y,name=name+' / transparent cap')
        if name.startswith('c'):
            arrow=self.el(cap,'Shape',rotation=DIRECTIONS.index(name[1:])*math.pi/2,name=name+' arrow')
            self.el(arrow,'Triangle',width=10,height=9)
            self.paint(arrow,GOLD)
        else:
            self.text(cap,0,-1,label or name.upper(),22 if name in ('a','b') else
                      (7 if name=='start' else 9),'FFE3F4F5',True)
        palette=CAP_COLORS.get('c' if name.startswith('c') else name,CAP_COLORS['neutral'])
        if round:
            rim=self.ellipse(cap,0,0,w,'7197A6B4',.8,name='Clear cap rim')
            self.gradient(rim,palette,w/2)
            self.ellipse(cap,-w*.16,-w*.19,w*.42,'15FFFFFF',1,name='Moulded cap highlight')
        else:
            face=self.rect(cap,0,0,w,h,'7197A6B4',h/2,.75,name='Clear paddle rim')
            self.gradient(face,palette,w/2)
        led=self.el(a,'Node',x=x,y=y,opacity=.08,name=name+' / socket LED')
        if round:
            self.ellipse(led,0,0,w+5,color,1.3)
            self.ellipse(led,0,0,w+5,color,3,3 if name=='start' else 7)
        else:
            glow=self.rect(led,0,0,w+4,h+4,color,h/2,1.2)
            self.paint(glow,color,3,7)
        self.animate(a,sm,name+'Pressed',[(cap.get('id'),'cap'),(led.get('id'),'glow')])
        # Contacts and clear socket remain visible through the cap at rest.
        self.rect(a,x,y+h*.27,w*.22,1.5,color,.7,name=name+' / contact pad')
        if round:
            self.ellipse(a,x,y,w+9,'FF0B1B24',name='Exposed switch socket')
        else:
            self.rect(a,x,y,w+7,h+7,'FF0B1B24',h/2,name='Exposed switch socket')
        return dict(inputs=[name],frame=dict(x=x-w/2,y=y-h/2,width=w,height=h),
                    extendedEdges=dict(top=3,bottom=3,left=3,right=3),mask='circle' if round else 'rectangle')

    def dpad(self,a,sm,x,y):
        pad=self.el(a,'Node',x=x,y=y,name='Gray digital cross')
        for i,name in enumerate(['up','right','down','left']):
            dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][i]
            arm=self.el(pad,'Node',x=dx*26,y=dy*26,rotation=i*math.pi/2,name=name+' cap')
            arrow=self.el(arm,'Shape',y=-2)
            self.el(arrow,'Triangle',width=6,height=5)
            self.paint(arrow,'FFB2CED4')
            face=self.rect(arm,0,0,22,29,'748C9AA6',3,.7)
            # Retain the removed inner rectangle's IDs; new material IDs live
            # separately so a palette edit does not renumber the rest of the file.
            self.counter+=4
            self.gradient(face,CAP_COLORS['neutral'],17,new_ids=True)
            led=self.el(arm,'Node',opacity=.06,name=name+' LED')
            self.rect(led,0,-11,12,2,MINT,1)
            self.animate(a,sm,name+'Pressed',[(led.get('id'),'glow')])
        self.ellipse(pad,0,0,5,'FFA7B5C0')
        self.rect(pad,0,0,27,27,'505A6F80',3)
        self.rect(pad,0,1,30,84,'FF0A1B24',5)
        self.rect(pad,0,1,84,30,'FF0A1B24',5)
        return dict(inputs=dict(up='up',down='down',left='left',right='right'),
                    frame=dict(x=x-44,y=y-44,width=88,height=88))

    def stick(self,a,sm,x,y):
        socket=self.el(a,'Node',x=x,y=y,name='Transparent analog module')
        moving=self.el(socket,'RootBone',length=1,name='Continuous XY gimbal')
        ax=self.timeline(a,'Gimbal / X',[(moving,90,[(0,-27),(30,0),(60,27)])],60)
        ay=self.timeline(a,'Gimbal / Y',[(moving,91,[(0,27),(30,0),(60,-27)])],60)
        joystick=self.el(a,'Joystick',xId=ax.get('id'),yId=ay.get('id'),posX=x,posY=y,
                         width=144,height=144,name='Analog / two-axis pose')
        self.bind(joystick,299,'stickX')
        self.bind(joystick,300,'stickY')
        cap=self.el(socket,'Node',name='Transparent moving cap')
        self.el(cap,'TranslationConstraint',targetId=moving.get('id'))
        self.ellipse(cap,0,0,8,'FFDBFBFA',1,name='Thumb center')
        for radius in [13,18]:
            self.ellipse(cap,0,0,radius*2,'438E9FAB',.7,name='Concentric grip')
        face=self.ellipse(cap,0,0,49,'8FABBDC8',1,name='Gray thumb cap')
        self.gradient(face,['8C9BA8B5','28657485','36505D70'],25,True)
        self.ellipse(cap,0,3,53,'FF10232E',1,name='Cap refraction')
        contact=self.el(cap,'Node',opacity=.06,name='Cap contact LED')
        self.ellipse(contact,0,0,56,MINT,1.1)
        self.ellipse(contact,0,0,56,MINT,3,7)
        self.animate(a,sm,'stickContact',[(contact.get('id'),'glow')])
        # Cross slides make the two independent analog axes visible beneath the cap.
        for prop,key,horizontal in [('stickX',13,False),('stickY',14,True)]:
            slider=self.el(socket,'Node',name=prop+' / exposed potentiometer')
            self.numeric(slider,key,prop,-27 if key==13 else 27,27 if key==13 else -27,-1,1)
            self.rect(slider,0,0,91 if horizontal else 5,5 if horizontal else 91,
                      'FF56707B',2,.5)
            self.rect(slider,0,0,87 if horizontal else 2,2 if horizontal else 87,
                      'FF1C3F48',1)
        ring=self.el(socket,'Node',name='Analog displacement LED')
        self.numeric(ring,18,'stickMagnitude',.08,.9)
        self.ellipse(ring,0,0,123,MINT,1)
        self.ellipse(ring,0,0,123,MINT,2,5)
        self.ellipse(socket,0,0,139,'FF496B76',.75,name='Clear socket rim')
        self.ellipse(socket,0,0,129,'FF0D222B',name='Analog well')
        self.rect(socket,0,0,151,151,'FF3F6871',14,.75,name='Visible analog daughterboard')
        self.rect(socket,0,0,151,151,'FF102D34',14,name='Daughterboard substrate')
        for dx in [-65,65]:
            for dy in [-65,65]:
                self.screw(socket,dx,dy)
        return dict(inputs={d.lower():'analogStick'+d for d in ['Up','Down','Left','Right']},
                    frame=dict(x=x-72,y=y-72,width=144,height=144),
                    thumbstick=dict(name='stick.pdf',width=53,height=53))

    def artboard(self,orientation):
        portrait=orientation=='portrait'
        w,h=(390,400) if portrait else (844,390)
        a=self.el(self.root,'Artboard',name=orientation.title(),width=w,height=h,
                  viewModelId=self.vm,viewModelInstanceId=self.instance,x=0 if portrait else 460)
        style=self.el(a,'LayoutComponentStyle')
        a.set('styleId',style.get('id'))
        sm=self.el(a,'StateMachine',name='Controller')
        a.set('defaultStateMachineId',sm.get('id'))
        # Reserve the former header's IDs to keep generated changes reviewable.
        self.counter+=15 if portrait else 10
        items=[self.stick(a,sm,116 if portrait else 111,284 if portrait else 282),
               self.dpad(a,sm,78 if portrait else 70,139)]
        cx,cy=(317,150) if portrait else (755,145)
        self.text(a,cx,cy,'C',9,GOLD,True)
        buttons=[('c'+d,cx+dx,cy+dy,32,32,GOLD,None,True)
                 for d,dx,dy in [('Up',0,-29),('Down',0,29),('Left',-29,0),('Right',29,0)]]
        buttons += [('a',267,258,56,56,BLUE,'A',True),('b',227,206,46,46,GREEN,'B',True),
                    ('l',44,78,60,20,ICE,'L',False),('r',346,78,60,20,ICE,'R',False),
                    ('z',116,378,52,22,MINT,'Z',False),('start',195,141,34,34,RED,'START',True),
                    ('menu',40,378,38,16,ICE,'MENU',False)] if portrait else [
                    ('a',735,260,56,56,BLUE,'A',True),('b',687,204,46,46,GREEN,'B',True),
                    ('l',55,65,60,20,ICE,'L',False),('r',782,65,60,20,ICE,'R',False),
                    ('z',111,375,52,22,MINT,'Z',False),('start',422,18,28,28,RED,'START',True),
                    ('menu',40,375,38,16,ICE,'MENU',False)]
        for button in buttons:
            items.append(self.button(a,sm,*button))
        # Glass floats above all routed copper, chips and board details.
        panels=[(195,200,382,392)] if portrait else [(102,195,196,382),(742,195,196,382)]
        for px,py,pw,ph in panels:
            self.glass(a,px,py,pw,ph,20)
        self.glass(a,w/2,20,81,36,16) if not portrait else None
        chip=(195,69) if portrait else (180,189)
        self.chip(a,*chip)
        self.text(a,211,8,'DISPLAY',4.5,'FF789AA5') if portrait else None
        if not portrait:
            self.chip(a,664,189)
        # PCB pads, vias and fasteners supply physical scale through the shell.
        for px,py,pw,ph in panels:
            for dx in [-pw/2+12,pw/2-12]:
                for dy in [-ph/2+13,ph/2-13]:
                    self.screw(a,px+dx,py+dy)
            for i in range(8):
                self.rect(a,px-pw/2+12+i*7,py+ph/2-45,3,5,'FF516D72',.5,name='SMT array')
        traces=[]
        for index,(name,bx,by,bw,bh,color,*_) in enumerate(buttons):
            if name=='menu':
                continue
            if portrait:
                lane=159+(index%5)*5
                if bx>200:
                    lane=242+(index%4)*5
                points=[(bx,by),(lane,by),(lane,99+index%3*4),
                        (chip[0]+(8 if bx>200 else -8),chip[1]+13),chip,(195,5)]
            else:
                if name=='start':
                    points=[(bx,by),(422,39)]
                else:
                    target=(180,189) if bx<422 else (664,189)
                    lane=(161+index%4*4) if bx<422 else (680+index%4*4)
                    points=[(bx,by),(lane,by),(lane,target[1]+19),target,
                            (217 if bx<422 else 627,189)]
            self.signal(a,sm,name+'Pressed',points,color,name.upper())
            receiver=self.el(a,'Node',opacity=.06,name=name+' / display input LED')
            rx,ry=(178+index*3.3,6) if portrait else ((216,174+index*2.5) if bx<422 else (628,174+index*2.5))
            self.rect(receiver,rx,ry,1.5 if portrait else 2.5,2.5 if portrait else 1.5,color,.5)
            self.animate(a,sm,name+'Pressed',[(receiver.get('id'),'glow')])
            traces.append(dict(name=name,points=points,color=color))
        for i,name in enumerate(['up','right','down','left']):
            dx,dy=[(0,-26),(26,0),(0,26),(-26,0)][i]
            bx,by=(78 if portrait else 70)+dx,139+dy
            target=chip
            lane=143+i*4 if portrait else 143+i*4
            points=[(bx,by),(lane,by),(lane,93 if portrait else 169),target,
                    (195,5) if portrait else (217,189)]
            self.signal(a,sm,name+'Pressed',points,MINT,'DPAD '+name.upper())
            traces.append(dict(name=name,points=points,color=MINT))
        for i,direction in enumerate(DIRECTIONS):
            sx,sy=(116,284) if portrait else (111,282)
            target=chip
            points=[(sx,sy),(sx+58+i*3,sy),(sx+58+i*3,100 if portrait else 210),
                    target,(195,5) if portrait else (217,189)]
            self.signal(a,sm,'analogStick'+direction+'Pressed',points,MINT,'STICK '+direction.upper())
            traces.append(dict(name='analogStick'+direction,points=points,color=MINT))
        # Main board stays dark enough that the illuminated signals carry the hierarchy.
        for px,py,pw,ph in panels:
            board=self.rect(a,px,py,pw-9,ph-9,'FF3A515D',16,.5,name='PCB edge')
            self.gradient(board,['FF14262E','FF0C1C26'],ph/2)
        if portrait:
            self.rect(a,w/2,h/2,w,h,'FF07131E',name='Backdrop')
        self.circuits[orientation]=dict(panels=panels,traces=traces)
        rep=dict(assets=dict(resizable=orientation+'.pdf'),mappingSize=dict(width=w,height=h),items=items)
        if not portrait:
            rep['screens']=[dict(outputFrame=dict(x=218,y=40,width=408,height=306))]
        return rep


def generate():
    path=ROOT/'OrbitCrystal'
    path.mkdir(exist_ok=True)
    scene=Crystal()
    reps={o:scene.artboard(o) for o in ['portrait','landscape']}
    edge=copy.deepcopy(reps)
    for rep in edge.values():
        rep['respectsSafeArea']=True
    info=dict(name='Orbit: Crystal',identifier='com.delta.rive.orbit-crystal.n64',
              gameTypeIdentifier='com.rileytestut.delta.game.n64',debug=False,
              representations=dict(iphone=dict(standard=reps,edgeToEdge=edge)))
    manifest=dict(schemaVersion=1,representations={
        f'iphone-{display}-{orientation}':dict(file='OrbitCrystal.riv',artboard=orientation.title(),
            stateMachine='Controller',viewModel='Controller',buttons={b:b+'Pressed' for b in BUTTONS},
            sticks=[dict(up='analogStickUp',down='analogStickDown',left='analogStickLeft',right='analogStickRight',
                         x='stickX',y='stickY',active='stickActive',magnitude='stickMagnitude',contact='stickContact')],
            reduceMotion='reduceMotion')
        for display in ['standard','edgeToEdge'] for orientation in reps})
    (path/'scene.rml').write_text(scene.finish())
    (path/'rive.yaml').write_text('name: OrbitCrystal\nmain: Portrait\n')
    (path/'info.json').write_text(json.dumps(info,indent=2)+'\n')
    (path/'rive.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (path/'circuit-layout.json').write_text(json.dumps(scene.circuits,indent=2)+'\n')


if __name__=='__main__':
    generate()
