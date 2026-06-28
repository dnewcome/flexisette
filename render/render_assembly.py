"""Render the flexisette stack: printed panel + frame + PCB + tape-head insert -> 9mm cassette."""
import bpy, math, sys, os

def _new():
    o = bpy.context.view_layer.objects.active
    if o is None and len(bpy.context.scene.objects):
        o = bpy.context.scene.objects[-1]
    return o

B = '/home/dan/sandbox/dnewcome/flexisette/cad/build'
OUT = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '/home/dan/sandbox/dnewcome/flexisette/render/out/flexisette_assembly.png'
S = 0.001
ZC = -0.0045          # centre the 9mm stack about z=0
EXPL = 0.0016         # small explode so the layers read

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
pr = bpy.context.preferences.addons['cycles'].preferences
pr.compute_device_type = 'OPTIX'; pr.refresh_devices()
for d in pr.devices: d.use = (d.type == 'OPTIX')
sc.cycles.device = 'GPU'; sc.cycles.samples = 220; sc.cycles.use_denoising = True
sc.render.resolution_x = 1792; sc.render.resolution_y = 1120
sc.render.filepath = OUT
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.view_settings.exposure = -0.6

def setp(n,k,v):
    if k in n.inputs: n.inputs[k].default_value = v
def principled(name, base, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes=True
    b = m.node_tree.nodes.get('Principled BSDF')
    setp(b,'Base Color',(*base,1)); setp(b,'Roughness',rough); setp(b,'Metallic',metal); setp(b,'Coat Weight',coat)
    return m
def emission(name,c,s):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    e=nt.nodes.new('ShaderNodeEmission'); o=nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value=(*c,1); e.inputs['Strength'].default_value=s
    nt.links.new(e.outputs['Emission'],o.inputs['Surface']); return m

M_PCB   = principled('pcb',(0.02,0.16,0.07), rough=0.4, coat=0.2)      # green soldermask
M_FRAME = principled('frame',(0.62,0.63,0.66), rough=0.5)             # grey resin
M_PANEL = principled('panel',(0.83,0.34,0.06), rough=0.45)            # printed face (warm)
M_PROTR = principled('protr',(0.45,0.06,0.06), rough=0.5)             # tape-head (maroon)

def imp(path):
    pre=set(bpy.data.objects); bpy.ops.wm.stl_import(filepath=path)
    return [o for o in bpy.data.objects if o not in pre][0]

def place(path, zmm, mat, expl=0.0):
    o=imp(path); o.scale=(S,S,S); o.location.z = zmm*S + ZC + expl
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth=False
    return o

_pcb = f'{B}/pcb.stl' if os.path.exists(f'{B}/pcb.stl') else f'{B}/panel.stl'  # real board if imported
place(_pcb, 0.0, M_PCB,   -EXPL)                    # bottom = real PCB (cad/import_pcb.py) or stand-in
place(f'{B}/frame.stl', 1.57, M_FRAME, 0.0)         # frame
place(f'{B}/panel.stl', 7.43, M_PANEL, +EXPL)       # top = printed panel (warm)

# insert: recentre, orient (thickness->Z, head face -> -Y), seat at the bottom edge
ins = imp(f'{B}/insert.stl')
bpy.context.view_layer.objects.active = ins; ins.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS'); ins.location=(0,0,0); ins.select_set(False)
ins.scale=(S,S,S)
ins.rotation_euler=(math.radians(-90),0,0)
ins.location=(0.0, -0.0245, ZC + 0.0045)            # bottom-front edge, spans the thickness
ins.data.materials.append(M_PROTR)

# studio
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0,0,ZC-0.005)); fl=_new()
fm=bpy.data.materials.new('floor'); fm.use_nodes=True
setp(fm.node_tree.nodes['Principled BSDF'],'Base Color',(0.02,0.02,0.025,1)); setp(fm.node_tree.nodes['Principled BSDF'],'Roughness',0.45)
fl.data.materials.append(fm)
wd=bpy.data.worlds.new('w'); sc.world=wd; wd.use_nodes=True
wd.node_tree.nodes['Background'].inputs['Color'].default_value=(0.012,0.012,0.016,1)
bpy.ops.object.empty_add(location=(0,0,0)); tgt=_new()
def soft(loc,rot,size,st):
    bpy.ops.mesh.primitive_plane_add(size=size,location=loc); s=_new()
    s.rotation_euler=rot; s.data.materials.append(emission('sb',(1,1,1),st)); s.visible_camera=False
soft((0.10,-0.16,0.30),(math.radians(50),0,math.radians(20)),0.40,3.2)
soft((-0.22,0.04,0.24),(math.radians(65),0,math.radians(-70)),0.30,1.6)
def area(loc,en,sz):
    bpy.ops.object.light_add(type='AREA',location=loc); l=_new(); l.data.energy=en; l.data.size=sz
    l.constraints.new('TRACK_TO').target=tgt
area((0.14,-0.18,0.24),11,0.30); area((-0.15,-0.06,0.18),3,0.34); area((0.03,0.18,0.22),6,0.22)
bpy.ops.object.camera_add(location=(0.075,-0.175,0.150)); cam=_new()
sc.camera=cam; cam.data.lens=70; cam.constraints.new('TRACK_TO').target=tgt
cam.data.dof.use_dof=True; cam.data.dof.focus_object=tgt; cam.data.dof.aperture_fstop=8.0

bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0] + '.blend')
print('ASSEMBLY_RENDER scene built (+.blend)')
if bpy.app.background:
    bpy.ops.render.render(write_still=True)
    print('ASSEMBLY_RENDER done ->', OUT)
