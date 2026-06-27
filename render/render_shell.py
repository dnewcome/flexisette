"""Render the flexisette shell assembly (PCB + spacer + PCB + head-holes insert) — exploded hero."""
import bpy, math, sys, os
from mathutils import Vector

def _new():
    """The just-created object — robust across headless (-b) and GUI-startup contexts."""
    o = bpy.context.view_layer.objects.active
    if o is None and len(bpy.context.scene.objects):
        o = bpy.context.scene.objects[-1]
    return o

ASM = '/home/dan/sandbox/dnewcome/flexisette/cad/build'
INSERT = '/home/dan/sandbox/dnewcome/flexisette/assets/cassette-shell-minecraft/side-1-insert.stl'
OUT = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '/home/dan/sandbox/dnewcome/flexisette/render/out/flexisette_shell.png'
S = 0.001  # mm -> m

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
pr = bpy.context.preferences.addons['cycles'].preferences
pr.compute_device_type = 'OPTIX'; pr.refresh_devices()
for d in pr.devices: d.use = (d.type == 'OPTIX')
sc.cycles.device = 'GPU'; sc.cycles.samples = 200; sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPTIX'
except Exception: pass
sc.render.resolution_x = 1792; sc.render.resolution_y = 1120
sc.render.filepath = OUT
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.view_settings.exposure = -0.6

def setp(n, k, v):
    if k in n.inputs: n.inputs[k].default_value = v

def principled(name, base, rough=0.5, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    setp(b, 'Base Color', (*base, 1)); setp(b, 'Roughness', rough)
    setp(b, 'Metallic', metal); setp(b, 'Coat Weight', coat)
    return m

def emission(name, col, st):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = st
    nt.links.new(e.outputs['Emission'], o.inputs['Surface']); return m

M_PCB    = principled('pcb', (0.015, 0.05, 0.03), rough=0.62, coat=0.0)   # matte PCB green-black
M_GOLD   = principled('gold', (0.92, 0.66, 0.22), rough=0.28, metal=1.0)
M_SPACER = principled('spacer', (0.80, 0.80, 0.83), rough=0.5)
M_INSERT = principled('insert', (0.14, 0.14, 0.16), rough=0.5)
M_SCREEN = emission('screen', (0.1, 0.8, 1.0), 6.0)

def imp(path):
    pre = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    return [o for o in bpy.data.objects if o not in pre][0]

def recenter(o):
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    o.location = (0, 0, 0); o.select_set(False)

# import assembly parts (already positioned in mm), scale to m, shift so mid-stack at z=0
parts = {}
for nm in ('pcb_bottom', 'spacer', 'pcb_top'):
    o = imp(f'{ASM}/{nm}.stl'); o.scale = (S, S, S); parts[nm] = o
ZC = -0.006  # centre the 12 mm stack
for o in parts.values(): o.location.z += ZC
parts['pcb_bottom'].data.materials.append(M_PCB)
parts['pcb_top'].data.materials.append(M_PCB)
parts['spacer'].data.materials.append(M_SPACER)

# explode along Z
E = 0.019
parts['pcb_bottom'].location.z -= E
parts['pcb_top'].location.z += E

# head-holes insert: recenter, orient (thickness->Z, height->Y), drop into spacer front slot
ins = imp(INSERT); recenter(ins)
ins.scale = (S, S, S)
ins.rotation_euler = (math.radians(-90), 0, 0)
ins.location = (0, -0.030, ZC + 0.004)   # front edge, in the spacer layer
ins.data.materials.append(M_INSERT)

# glowing screen on the top PCB
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.0, -0.013, ZC + E + 0.0096))
scr = _new(); scr.scale = (0.025, 0.010, 1); scr.data.materials.append(M_SCREEN)
# gold reel rings on top PCB (decorative)
for cx in (-0.026, 0.026):
    bpy.ops.mesh.primitive_torus_add(location=(cx, 0.014, ZC + E + 0.0093),
        major_radius=0.011, minor_radius=0.0007, major_segments=48, minor_segments=8)
    r = _new(); r.scale.z = 0.4; r.data.materials.append(M_GOLD)

# ---- studio ----
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, ZC - E - 0.004))
fl = _new()
fm = bpy.data.materials.new('floor'); fm.use_nodes = True
fb = fm.node_tree.nodes['Principled BSDF']; setp(fb, 'Base Color', (0.02, 0.02, 0.025, 1)); setp(fb, 'Roughness', 0.45)
fl.data.materials.append(fm)
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True
wd.node_tree.nodes['Background'].inputs['Color'].default_value = (0.012, 0.012, 0.016, 1)

bpy.ops.object.empty_add(location=(0, 0, ZC)); tgt = _new()
def soft(loc, rot, size, st):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc); s = _new()
    s.rotation_euler = rot; s.data.materials.append(emission('sb', (1, 1, 1), st)); s.visible_camera = False
soft((0.10, -0.16, 0.30), (math.radians(50), 0, math.radians(20)), 0.40, 3.2)
soft((-0.22, 0.04, 0.24), (math.radians(65), 0, math.radians(-70)), 0.30, 1.6)
def area(loc, en, sz):
    bpy.ops.object.light_add(type='AREA', location=loc); l = _new()
    l.data.energy = en; l.data.size = sz; l.constraints.new('TRACK_TO').target = tgt
area((0.14, -0.18, 0.26), 11, 0.30); area((-0.15, -0.06, 0.20), 3, 0.34); area((0.03, 0.18, 0.24), 6, 0.22)

bpy.ops.object.camera_add(location=(0.070, -0.190, 0.235)); cam = _new()
sc.camera = cam; cam.data.lens = 72; cam.constraints.new('TRACK_TO').target = tgt
cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 8.5

print('SHELL_RENDER scene built')
if bpy.app.background:                      # headless: render. GUI (make blend-shell): open scene, F12 to render.
    bpy.ops.render.render(write_still=True)
    print('SHELL_RENDER done ->', OUT)
