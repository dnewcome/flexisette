"""Render the two spacer variants side by side: dummy (infill) vs head-ready."""
import bpy, math, sys, os

def _new():
    """The just-created object — robust across headless (-b) and GUI-startup contexts."""
    o = bpy.context.view_layer.objects.active
    if o is None and len(bpy.context.scene.objects):
        o = bpy.context.scene.objects[-1]
    return o

ASM = '/home/dan/sandbox/dnewcome/flexisette/cad/build'
OUT = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '/home/dan/sandbox/dnewcome/flexisette/render/out/flexisette_spacers.png'
S = 0.001
FONT = next((p for p in ['/usr/share/fonts/truetype/lato/Lato-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'] if os.path.exists(p)), None)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
pr = bpy.context.preferences.addons['cycles'].preferences
pr.compute_device_type = 'OPTIX'; pr.refresh_devices()
for d in pr.devices: d.use = (d.type == 'OPTIX')
sc.cycles.device = 'GPU'; sc.cycles.samples = 180; sc.cycles.use_denoising = True
sc.render.resolution_x = 1792; sc.render.resolution_y = 1080
sc.render.filepath = OUT
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.view_settings.exposure = -0.5

def setp(n,k,v):
    if k in n.inputs: n.inputs[k].default_value = v
def principled(name, base, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes=True
    b = m.node_tree.nodes.get('Principled BSDF'); setp(b,'Base Color',(*base,1)); setp(b,'Roughness',rough)
    return m
def emission(name,col,st):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    e=nt.nodes.new('ShaderNodeEmission'); o=nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value=(*col,1); e.inputs['Strength'].default_value=st
    nt.links.new(e.outputs['Emission'],o.inputs['Surface']); return m

M_RESIN = principled('resin',(0.78,0.78,0.80),0.5)
M_ACCENT = principled('accent',(0.95,0.55,0.15),0.45)

def imp(path):
    pre=set(bpy.data.objects); bpy.ops.wm.stl_import(filepath=path)
    return [o for o in bpy.data.objects if o not in pre][0]

def add_spacer(variant, x, mat):
    o = imp(f'{ASM}/spacer_{variant}.stl')
    o.scale=(S,S,S); o.location=(x,0,0); o.data.materials.append(mat)
    return o

add_spacer('dummy', -0.062, M_RESIN)
add_spacer('head',   0.062, M_ACCENT)

def label(txt, x):
    bpy.ops.object.text_add(location=(x,-0.052,0.0005))
    t=_new(); t.data.body=txt; t.data.size=0.007; t.data.align_x='CENTER'; t.data.align_y='CENTER'
    t.data.extrude=0.0003
    if FONT: t.data.font=bpy.data.fonts.load(FONT)
    t.data.materials.append(principled('txt',(0.85,0.85,0.85),0.6))
label('DUMMY  ·  infill', -0.062)
label('HEAD-READY', 0.062)

# studio
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0,0,-0.0045))
fl=_new(); fm=bpy.data.materials.new('floor'); fm.use_nodes=True
setp(fm.node_tree.nodes['Principled BSDF'],'Base Color',(0.02,0.02,0.025,1))
setp(fm.node_tree.nodes['Principled BSDF'],'Roughness',0.5); fl.data.materials.append(fm)
wd=bpy.data.worlds.new('w'); sc.world=wd; wd.use_nodes=True
wd.node_tree.nodes['Background'].inputs['Color'].default_value=(0.012,0.012,0.016,1)
bpy.ops.object.empty_add(location=(0,0,0)); tgt=_new()
def soft(loc,rot,size,st):
    bpy.ops.mesh.primitive_plane_add(size=size,location=loc); s=_new()
    s.rotation_euler=rot; s.data.materials.append(emission('sb',(1,1,1),st)); s.visible_camera=False
soft((0.12,-0.18,0.34),(math.radians(50),0,math.radians(18)),0.5,3.0)
soft((-0.24,0.06,0.28),(math.radians(65),0,math.radians(-70)),0.4,1.5)
def area(loc,en,sz):
    bpy.ops.object.light_add(type='AREA',location=loc); l=_new()
    l.data.energy=en; l.data.size=sz; l.constraints.new('TRACK_TO').target=tgt
area((0.18,-0.20,0.30),16,0.4); area((-0.2,-0.05,0.24),5,0.4); area((0,0.2,0.28),9,0.3)
bpy.ops.object.camera_add(location=(0.0,-0.150,0.300)); cam=_new()
sc.camera=cam; cam.data.lens=42; cam.constraints.new('TRACK_TO').target=tgt
cam.data.dof.use_dof=True; cam.data.dof.focus_object=tgt; cam.data.dof.aperture_fstop=10

print('SPACERS_RENDER scene built')
if bpy.app.background:                      # headless: render. GUI (make blend-spacers): open scene, F12 to render.
    bpy.ops.render.render(write_still=True)
    print('SPACERS_RENDER done')
