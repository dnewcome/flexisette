"""Render the head_frame part — front-3/4 hero showing the head window + corner screw bosses."""
import bpy, math, sys, os

def _new():
    o = bpy.context.view_layer.objects.active
    if o is None and len(bpy.context.scene.objects):
        o = bpy.context.scene.objects[-1]
    return o

_args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
OUT = _args[0] if len(_args) > 0 else '/home/dan/sandbox/dnewcome/flexisette/render/out/flexisette_head_frame.png'
STL = _args[1] if len(_args) > 1 else '/home/dan/sandbox/dnewcome/flexisette/cad/build/head_frame.stl'
S = 0.001

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
pr = bpy.context.preferences.addons['cycles'].preferences
pr.compute_device_type = 'OPTIX'; pr.refresh_devices()
for d in pr.devices: d.use = (d.type == 'OPTIX')
sc.cycles.device = 'GPU'; sc.cycles.samples = 200; sc.cycles.use_denoising = True
sc.render.resolution_x = 1792; sc.render.resolution_y = 1120
sc.render.filepath = OUT
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.view_settings.exposure = -0.5

def setp(n, k, v):
    if k in n.inputs: n.inputs[k].default_value = v
def principled(name, base, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF'); setp(b, 'Base Color', (*base, 1)); setp(b, 'Roughness', rough)
    return m
def emission(name, col, st):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = st
    nt.links.new(e.outputs['Emission'], o.inputs['Surface']); return m

pre = set(bpy.data.objects)
bpy.ops.wm.stl_import(filepath=STL)
o = [x for x in bpy.data.objects if x not in pre][0]
bpy.context.view_layer.objects.active = o; o.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')   # auto-centre any part
o.location = (0, 0, 0); o.select_set(False)
_dz = o.dimensions.z                               # unscaled height (mm) — read BEFORE scaling
o.scale = (S, S, S)
PART_CZ = _dz * S / 2
o.location.z = PART_CZ                              # sit the part on the floor (z=0)
o.data.materials.append(principled('resin', (0.62, 0.66, 0.72), 0.45))
for p in o.data.polygons: p.use_smooth = False

# studio
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, -0.0002))
fl = _new(); fm = bpy.data.materials.new('floor'); fm.use_nodes = True
setp(fm.node_tree.nodes['Principled BSDF'], 'Base Color', (0.02, 0.02, 0.025, 1))
setp(fm.node_tree.nodes['Principled BSDF'], 'Roughness', 0.5); fl.data.materials.append(fm)
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True
wd.node_tree.nodes['Background'].inputs['Color'].default_value = (0.012, 0.012, 0.016, 1)
bpy.ops.object.empty_add(location=(0, 0, PART_CZ)); tgt = _new()
def soft(loc, rot, size, st):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc); s = _new()
    s.rotation_euler = rot; s.data.materials.append(emission('sb', (1, 1, 1), st)); s.visible_camera = False
soft((0.10, -0.16, 0.30), (math.radians(50), 0, math.radians(18)), 0.4, 3.2)
soft((-0.20, 0.05, 0.26), (math.radians(65), 0, math.radians(-70)), 0.34, 1.6)
def area(loc, en, sz):
    bpy.ops.object.light_add(type='AREA', location=loc); l = _new()
    l.data.energy = en; l.data.size = sz; l.constraints.new('TRACK_TO').target = tgt
area((0.14, -0.18, 0.24), 12, 0.30); area((-0.15, -0.05, 0.18), 3, 0.34); area((0.03, 0.16, 0.22), 6, 0.22)
bpy.ops.object.camera_add(location=(0.052, -0.150, 0.105)); cam = _new()
sc.camera = cam; cam.data.lens = 62; cam.constraints.new('TRACK_TO').target = tgt
cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 8.0

bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0] + '.blend')
print('FRAME_RENDER scene built (+.blend)')
if bpy.app.background:
    bpy.ops.render.render(write_still=True)
    print('FRAME_RENDER done ->', OUT)
