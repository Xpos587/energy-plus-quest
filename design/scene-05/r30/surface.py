"""Procedural gouache-like colour fields in world coordinates, shared by both cameras."""
import math
from pathlib import Path
import bpy
from PIL import Image, ImageOps
from mathutils import Vector, noise


def colour(hexcol):
    rgb = [int(hexcol[i:i+2], 16)/255 for i in (0,2,4)]
    return (*[(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4) for c in rgb], 1)


def set_input(nt, socket, value):
    if isinstance(value,bpy.types.NodeSocket): nt.links.new(value,socket)
    else: socket.default_value=value


def math_node(nt, op, a, b):
    n=nt.nodes.new('ShaderNodeMath'); n.operation=op
    set_input(nt,n.inputs[0],a); set_input(nt,n.inputs[1],b)
    return n.outputs[0]


def mix(nt, rate, a, b, mode='MIX'):
    n=nt.nodes.new('ShaderNodeMixRGB'); n.blend_type=mode
    for s,v in zip(n.inputs,(rate,a,b)): set_input(nt,s,v)
    return n.outputs[0]


def ramp(nt, inp, stops):
    n=nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(inp,n.inputs[0]); r=n.color_ramp
    for i,(pos,col) in enumerate(stops):
        e=r.elements[i] if i<2 else r.elements.new(pos); e.position=pos; e.color=colour(col)
    r.interpolation='EASE'; return n.outputs[0]


def scaled(nt, coord, xyz):
    v=nt.nodes.new('ShaderNodeVectorMath'); v.operation='MULTIPLY'; nt.links.new(coord,v.inputs[0]); v.inputs[1].default_value=xyz
    return v.outputs[0]


def field(nt, coord, xyz, detail=3, warp=.18):
    n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=1; n.inputs['Detail'].default_value=detail
    n.inputs['Distortion'].default_value=warp; nt.links.new(scaled(nt,coord,xyz),n.inputs['Vector']); return n.outputs['Fac']


def swatch(nt, coord, name, source, box, metres):
    # Tile a small LAND-COVER swatch in world space, not a plate in camera space.
    # Low-frequency distortion breaks mirror symmetry. Source boxes contain no story objects.
    root=Path(__file__).resolve().parents[3]; out=Path(bpy.data.filepath).parent/(name+'.png')
    if not out.is_file():
        tile=Image.open(root/source).convert('RGB').crop(box); w,h=tile.size
        art=Image.new('RGB',(w*2,h*2)); art.paste(tile); art.paste(ImageOps.mirror(tile),(w,0)); art.paste(ImageOps.flip(art.crop((0,0,2*w,h))),(0,h)); art.save(out)
    tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(out),check_existing=True)
    v=scaled(nt,coord,(1/metres[0],1/metres[1],.001)); warp=nt.nodes.new('ShaderNodeTexNoise'); warp.inputs['Scale'].default_value=1.4; nt.links.new(v,warp.inputs[0]); offset=scaled(nt,warp.outputs['Color'],((.09,.10,0) if name=='water-wash' else (.25,.31,0))); add=nt.nodes.new('ShaderNodeVectorMath'); add.operation='ADD'; nt.links.new(v,add.inputs[0]);nt.links.new(offset,add.inputs[1]);nt.links.new(add.outputs[0],tex.inputs[0]); return tex.outputs[0]


def paint():
    s=bpy.context.scene
    sun=bpy.data.lights['sun']; sun.energy=3.6; sun.angle=math.radians(3)
    mountains=[o for o in s.objects if o.get('group')=='mountains']
    if mountains:
        ridge=bpy.data.materials.new('ridge wash'); ridge.use_nodes=True; nt=ridge.node_tree; nt.nodes.clear(); em=nt.nodes.new('ShaderNodeEmission'); out=nt.nodes.new('ShaderNodeOutputMaterial'); a=nt.nodes.new('ShaderNodeAttribute'); a.attribute_name='col'; nt.links.new(a.outputs['Color'],em.inputs[0]); nt.links.new(em.outputs[0],out.inputs[0]);
        for o in mountains: o.data.materials[0]=ridge
    for mat in bpy.data.materials:
        if not mat.use_nodes: continue
        nt=mat.node_tree
        # The source toon lights keep contact shadows. Increase the temperature and value separation.
        for n in nt.nodes:
            if n.type=='VALTORGB' and len(n.color_ramp.elements)==3:
                for e,f in zip(n.color_ramp.elements,(.53,.80,1.0)):
                    e.color=(f*.98,f*.995,f+(1-f)*.12,1)
        em=next((n for n in nt.nodes if n.type=='EMISSION'),None)
        if not em: continue
        surface=em.inputs[0].links[0].from_socket
        p=nt.nodes.new('ShaderNodeNewGeometry').outputs['Position']
        if mat.name.startswith('ochre ground'):
            # Shade wash: rust willow / grey reindeer moss / golden sedge form patches, not a grid.
            m=field(nt,p,(.047,.082,.04),4,.75)
            wash=ramp(nt,m,[(.22,'785340'),(.38,'A87740'),(.47,'ACA057'),(.55,'D0B568'),(.64,'AF8755'),(.76,'9C5140')])
            # Exclude bare gravel / darkest pools using the material's vertex saturation.
            attr=next(n for n in nt.nodes if n.type=='ATTRIBUTE').outputs['Color']; sep=nt.nodes.new('ShaderNodeSeparateColor'); sep.mode='HSV'; nt.links.new(attr,sep.inputs[0]); hsv=sep.outputs
            dry=math_node(nt,'MINIMUM',1,math_node(nt,'MULTIPLY',hsv[2],4.4)); fac=math_node(nt,'MULTIPLY',dry,.52)
            grass=swatch(nt,p,'sedge-wash','public/scene-art/lastmile-family-v1/revision-28/choice-wide.webp',(1930,340,2370,585),(67,72))
            heath=swatch(nt,p,'heath-wash','public/scene-art/lastmile-family-v1/revision-28/choice-wide.webp',(15,480,240,630),(24,31))
            grasses=mix(nt,m,grass,heath); base=mix(nt,.53,surface,mix(nt,.81,wash,grasses))
            yp=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(p,yp.inputs[0]); y=yp.outputs['Y']
            mire=swatch(nt,p,'mire-wash','public/scene-art/lastmile-family-v1/revision-28/choice-wide.webp',(10,900,325,1080),(39,36))
            # Map muddy ground by its original vertex VALUE, not an artificial rectangular band.
            bog=math_node(nt,'MINIMUM',1,math_node(nt,'MAXIMUM',0,math_node(nt,'MULTIPLY',math_node(nt,'SUBTRACT',.39,hsv[2]),5)))
            base=mix(nt,math_node(nt,'MULTIPLY',bog,.85),base,mix(nt,.48,surface,mire))
            gravel=math_node(nt,'MINIMUM',1,math_node(nt,'MAXIMUM',0,math_node(nt,'MULTIPLY',math_node(nt,'SUBTRACT',.55,hsv[1]),4)))
            base=mix(nt,gravel,base,surface)
            grit=field(nt,p,(1.4,2.7,1),2,.47)
            grain=ramp(nt,grit,[(.20,'A29A83'),(.42,'C6BFA7'),(.60,'FFF7E2'),(.75,'FFFFFF')]); base=mix(nt,.49,base,grain,'MULTIPLY')
            # Air perspective on distant vegetation; preserve the blue river against the land.
            y=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(p,y.inputs[0]); dist=math_node(nt,'MAXIMUM',0,math_node(nt,'SUBTRACT',y.outputs['Y'],150)); haze=math_node(nt,'MINIMUM',.84,math_node(nt,'MULTIPLY',dist,.0008))
            nt.links.new(mix(nt,haze,base,colour('A8B8C3')),em.inputs[0])
        elif mat.name in ('cobalt','peat'):
            wave=field(nt,p,(.24,.92,.15),2,.55); broad=field(nt,p,(.046,.13,.1),3,.38)
            if mat.name=='cobalt':
                water=ramp(nt,broad,[(.22,'337AA7'),(.4,'397FAA'),(.54,'4D91B9'),(.68,'65A8C7'),(.78,'82B7C9')]); ink='B3DAE7'
            else:
                water=ramp(nt,broad,[(.22,'46554E'),(.4,'5B6252'),(.55,'69746A'),(.66,'788C85'),(.8,'9CA99A')]); ink='B9B9A2'
            if mat.name=='cobalt':
                ripples=swatch(nt,p,'water-wash','design/scene-04/barge-v2/style-a.png',(1415,480,1595,625),(25,12)); water=mix(nt,.40,water,ripples)
            crest=ramp(nt,wave,[(.56,'000000'),(.60,'151515'),(.624,'AEAEAE'),(.655,'282828'),(.69,'000000')]); nt.links.new(mix(nt,math_node(nt,'MULTIPLY',crest,.63),water,colour(ink)),em.inputs[0])
        elif mat.name in ('paving','obj','flat','glass'):
            # Small material variation, never a full-image canvas-noise overlay.
            grain=field(nt,p,(1.2,1.6,.9),2,.3); shade=ramp(nt,grain,[(.2,'B6B3A6'),(.45,'DEDCCF'),(.74,'FFFFFF')])
            nt.links.new(mix(nt,.27,surface,shade,'MULTIPLY'),em.inputs[0])
    nt=s.world.node_tree; out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD')
    bg=next(n for n in nt.nodes if n.type=='BACKGROUND'); bg.inputs[1].default_value=.45
    tex=nt.nodes.new('ShaderNodeTexCoord').outputs['Generated']; sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tex,sep.inputs[0]); z=sep.outputs['Z']
    sky=ramp(nt,z,[(0,'C8D9E6'),(.07,'A7CBE1'),(.18,'80B2D7'),(.34,'629BCD'),(.65,'5289C0')]); v=nt.nodes.new('ShaderNodeVectorMath'); v.operation='SCALE'; nt.links.new(tex,v.inputs[0]); nt.links.new(math_node(nt,'DIVIDE',1,math_node(nt,'MAXIMUM',z,.023)),v.inputs['Scale']); ray=v.outputs[0]
    clouds=field(nt,ray,(.58,.66,.1),4,.43); a=ramp(nt,clouds,[(.46,'000000'),(.525,'090909'),(.57,'999999'),(.63,'E9E9E9'),(.7,'FFFFFF')]); cf=math_node(nt,'MINIMUM',1,math_node(nt,'MULTIPLY',z,10)); cloud=math_node(nt,'MULTIPLY',cf,a)
    tint=ramp(nt,clouds,[(.46,'B7CBD9'),(.56,'DAE6E9'),(.63,'F9F6ED'),(.76,'FFFCF2')]); sky=mix(nt,cloud,sky,tint)
    b=nt.nodes.new('ShaderNodeBackground'); nt.links.new(sky,b.inputs[0]); mx=nt.nodes.new('ShaderNodeMixShader'); lp=nt.nodes.new('ShaderNodeLightPath'); nt.links.new(lp.outputs['Is Camera Ray'],mx.inputs[0]); nt.links.new(bg.outputs[0],mx.inputs[1]); nt.links.new(b.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs[0])
