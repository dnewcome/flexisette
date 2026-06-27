#!/usr/bin/env python3
"""
flexisette product renders — parametric Blender builder.
Usage:
  blender -b --factory-startup -P build_render.py -- <SPEC A|B|C|D> <out.png>
Models a cassette-format PCB object and renders a studio product shot.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector

def _new():
    """The just-created object — robust across headless (-b) and GUI-startup contexts."""
    o = bpy.context.view_layer.objects.active
    if o is None and len(bpy.context.scene.objects):
        o = bpy.context.scene.objects[-1]
    return o

# ---------------- args ----------------
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SPEC = (argv[0] if len(argv) > 0 else 'B').upper()
OUT  = argv[1] if len(argv) > 1 else f'/home/dan/sandbox/dnewcome/flexisette/render/out/flexisette_{SPEC}.png'
SAMPLES = int(argv[2]) if len(argv) > 2 else 180

# cassette dims (meters)
W, H, R = 0.1005, 0.064, 0.005

FONT_PATHS = [
    '/usr/share/fonts/truetype/lato/Lato-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
]

# ---------------- scene reset ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------- render config ----------------
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.refresh_devices()
for d in prefs.devices:
    d.use = (d.type == 'OPTIX')
scene.cycles.device = 'GPU'
scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
try: scene.cycles.denoiser = 'OPTIX'
except Exception: pass
scene.render.resolution_x = 1792
scene.render.resolution_y = 1120
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
scene.view_settings.exposure = -0.8
scene.render.film_transparent = False

# ---------------- font ----------------
FONT = None
for p in FONT_PATHS:
    if os.path.exists(p):
        try: FONT = bpy.data.fonts.load(p); break
        except Exception: pass

# ---------------- material helpers ----------------
def _set(node, name, val):
    if name in node.inputs:
        node.inputs[name].default_value = val

def mat_principled(name, base, rough=0.5, metal=0.0, spec=0.5, coat=0.0, transmission=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    _set(b, 'Base Color', (*base, 1)); _set(b, 'Roughness', rough)
    _set(b, 'Metallic', metal); _set(b, 'Specular IOR Level', spec)
    _set(b, 'Coat Weight', coat); _set(b, 'Transmission Weight', transmission)
    return m

def mat_emission(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs['Emission'], o.inputs['Surface'])
    return m

def mat_screen(name):
    """Glowing reactive-visualizer emission."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    wav = nt.nodes.new('ShaderNodeTexWave'); wav.wave_type = 'BANDS'; wav.bands_direction='X'
    wav.inputs['Scale'].default_value = 7.0; wav.inputs['Distortion'].default_value = 6.0
    grad = nt.nodes.new('ShaderNodeTexGradient'); grad.gradient_type = 'LINEAR'
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0;  cr.elements[0].color = (0.05, 0.02, 0.35, 1)   # indigo
    cr.elements[1].position = 1.0;  cr.elements[1].color = (1.0, 0.25, 0.55, 1)    # magenta
    e1 = cr.elements.new(0.45); e1.color = (0.0, 0.85, 1.0, 1)                      # cyan
    e2 = cr.elements.new(0.72); e2.color = (1.0, 0.85, 0.15, 1)                     # amber
    mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'OVERLAY'; mix.inputs['Fac'].default_value = 0.42
    emis = nt.nodes.new('ShaderNodeEmission'); emis.inputs['Strength'].default_value = 7.5
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    L = nt.links.new
    L(tc.outputs['Generated'], mp.inputs['Vector'])
    L(mp.outputs['Vector'], grad.inputs['Vector'])
    L(mp.outputs['Vector'], wav.inputs['Vector'])
    L(grad.outputs['Color'], ramp.inputs['Fac'])
    L(ramp.outputs['Color'], mix.inputs['Color1'])
    L(wav.outputs['Color'], mix.inputs['Color2'])
    L(mix.outputs['Color'], emis.inputs['Color'])
    L(emis.outputs['Emission'], out.inputs['Surface'])
    return m

# palette per spec
SOLDER = {
    'A': (0.012, 0.012, 0.014),   # near-black
    'B': (0.012, 0.03, 0.09),     # deep blue
    'C': (0.012, 0.012, 0.014),   # black rigid islands
    'D': (0.012, 0.012, 0.014),
}.get(SPEC, (0.012, 0.012, 0.014))

M_PCB    = mat_principled('pcb', SOLDER, rough=0.42, spec=0.45, coat=0.25)
M_GOLD   = mat_principled('enig_gold', (0.92, 0.66, 0.22), rough=0.28, metal=1.0)
M_SILK   = mat_principled('silk', (0.86, 0.86, 0.84), rough=0.6)
M_DARK   = mat_principled('dark', (0.02, 0.02, 0.02), rough=0.5)
M_FLEX   = mat_principled('flex_pi', (0.68, 0.17, 0.008), rough=0.45, spec=0.4, coat=0.05, transmission=0.04)
M_SPACER = mat_principled('spacer', (0.85, 0.85, 0.88), rough=0.55)
M_SCREEN = mat_screen('screen')

# ---------------- geometry helpers ----------------
def rrect_pts(w, h, r, seg=12):
    hw, hh = w/2, h/2
    out = []
    cs = [( hw-r, -hh+r, -math.pi/2, 0.0),
          ( hw-r,  hh-r, 0.0, math.pi/2),
          (-hw+r,  hh-r, math.pi/2, math.pi),
          (-hw+r, -hh+r, math.pi, 1.5*math.pi)]
    for cx, cy, a0, a1 in cs:
        for i in range(seg+1):
            a = a0 + (a1-a0)*i/seg
            out.append((cx+math.cos(a)*r, cy+math.sin(a)*r))
    return out

def add_board(w, h, d, r, mat, name='board', z=0.0):
    pts = rrect_pts(w, h, r)
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z-d/2)) for (x, y) in pts]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, d))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    # subtle edge bevel
    bev = ob.modifiers.new('bev', 'BEVEL'); bev.width = 0.0004; bev.segments = 2
    bev.harden_normals = True
    # smooth shading
    for poly in ob.data.polygons: poly.use_smooth = False
    return ob

def add_screen(cx, cy, w, h, ztop):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, ztop+0.0006))
    o = _new(); o.scale = (w/2, h/2, 1); o.name = 'screen'
    o.data.materials.append(M_SCREEN)
    # thin black bezel under it
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, ztop+0.0004))
    bz = _new(); bz.scale = (w/2+0.0018, h/2+0.0018, 1); bz.name='bezel'
    bz.data.materials.append(M_DARK)
    return o

def add_ring(cx, cy, rad, ztop, mat=M_GOLD, minor=0.0006):
    bpy.ops.mesh.primitive_torus_add(location=(cx, cy, ztop+0.0003),
        major_radius=rad, minor_radius=minor, major_segments=64, minor_segments=8)
    o = _new(); o.scale.z = 0.35
    o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    return o

def add_hub(cx, cy, ztop):
    for rad in (0.006, 0.009, 0.0118):
        add_ring(cx, cy, rad, ztop)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0035, depth=0.0006,
        location=(cx, cy, ztop+0.0003), vertices=32)
    c = _new(); c.data.materials.append(M_GOLD)
    for p in c.data.polygons: p.use_smooth = True

def add_trace(x, y, length, ztop, width=0.0008, ang=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, ztop+0.0002))
    o = _new(); o.scale = (length/2, width/2, 0.00012)
    o.rotation_euler.z = ang; o.data.materials.append(M_GOLD)
    return o

def add_text(body, size, loc, mat, align='CENTER', extrude=0.00025, rotz=0.0):
    bpy.ops.object.text_add(location=loc)
    t = _new(); t.data.body = body; t.data.size = size
    t.data.align_x = align; t.data.align_y = 'CENTER'; t.data.extrude = extrude
    if FONT: t.data.font = FONT
    t.rotation_euler.z = rotz
    t.data.materials.append(mat)
    return t

def add_pads(ztop):
    for i in range(8):
        add_trace(-0.028 + i*0.008, -0.0285, 0.004, ztop, width=0.0022)

def cassette_face(ztop, flex=False):
    """Shared top-face art: two reel hubs, glowing letterbox screen, wordmark, traces."""
    add_hub(-0.026, 0.0145, ztop)
    add_hub( 0.026, 0.0145, ztop)
    add_screen(0.0, -0.0135, 0.050, 0.020, ztop)
    gold = M_GOLD
    add_text('flexisette', 0.0066, (0.0, 0.0285, ztop+0.0006), gold)
    add_text('SIDE A', 0.0030, (-0.040, 0.0145, ztop+0.0006), M_SILK, align='CENTER', rotz=math.pi/2)
    add_text('DROP 001 / 50', 0.0030, (0.030, -0.0285, ztop+0.0006), M_SILK, align='CENTER')
    add_text('night drives  ·  side a', 0.0030, (-0.047, -0.0285, ztop+0.0006), M_SILK, align='LEFT')
    # decorative traces
    for yy in (0.001, -0.0005, -0.002):
        add_trace(-0.030, yy, 0.02, ztop, width=0.0006)
        add_trace(0.030, yy, 0.02, ztop, width=0.0006)
    add_pads(ztop)

# ---------------- studio ----------------
def studio(focus=(0,0,0)):
    # floor with soft radial gradient
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0,0,-0.0001))
    fl = _new(); fl.name='floor'
    fm = bpy.data.materials.new('floor'); fm.use_nodes=True
    nt = fm.node_tree; bsdf = nt.nodes.get('Principled BSDF')
    _set(bsdf,'Roughness',0.42); _set(bsdf,'Specular IOR Level',0.5)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value=(1.4,1.4,1.4)
    gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type='SPHERICAL'
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.color_ramp.elements[0].color=(0.004,0.004,0.006,1)
    rmp.color_ramp.elements[1].color=(0.05,0.05,0.06,1)
    rmp.color_ramp.elements[0].position=0.30; rmp.color_ramp.elements[1].position=1.0
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], gr.inputs['Vector'])
    nt.links.new(gr.outputs['Color'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], bsdf.inputs['Base Color'])
    fl.data.materials.append(fm)
    # world dim
    wd = bpy.data.worlds.new('w'); scene.world = wd; wd.use_nodes=True
    wd.node_tree.nodes['Background'].inputs['Color'].default_value=(0.012,0.012,0.016,1)
    wd.node_tree.nodes['Background'].inputs['Strength'].default_value=1.0
    # softboxes (emissive planes) for metal/screen reflections
    def softbox(loc, rot, size, strength):
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
        s=_new(); s.rotation_euler=rot
        s.data.materials.append(mat_emission('sb', (1,1,1), strength))
        s.visible_camera=False
        return s
    softbox((0.10,-0.16,0.30),(math.radians(50),0,math.radians(20)),0.40,3.2)
    softbox((-0.22,0.04,0.24),(math.radians(65),0,math.radians(-70)),0.30,1.6)
    # key + rim area lights
    bpy.ops.object.empty_add(location=focus); tgt=_new()
    def area(loc, energy, size):
        bpy.ops.object.light_add(type='AREA', location=loc)
        l=_new(); l.data.energy=energy; l.data.size=size
        cons=l.constraints.new('TRACK_TO'); cons.target=tgt
        return l
    area((0.14,-0.18,0.22), 9.0, 0.28)
    area((-0.15,-0.06,0.18), 2.2, 0.34)
    area((0.03,0.18,0.20), 5.0, 0.22)   # back rim
    # camera
    bpy.ops.object.camera_add(location=(0.060,-0.178,0.150))
    cam=_new(); scene.camera=cam
    cam.data.lens=80; cam.data.sensor_width=36
    cc=cam.constraints.new('TRACK_TO'); cc.target=tgt
    cam.data.dof.use_dof=True; cam.data.dof.focus_object=tgt; cam.data.dof.aperture_fstop=9.0

# ---------------- spec builders ----------------
def build_B():
    d=0.0050
    add_board(W, H, d, R, M_PCB, 'slim', z=d/2)  # bottom on floor
    cassette_face(d)

def build_A():
    # bottom board, spacer ring, top board -> visible PCB/resin/PCB edge
    db=0.0016; ds=0.0080; dt=0.0016
    z0=db/2
    add_board(W, H, db, R, M_PCB, 'mainboard', z=z0)
    # spacer frame (perimeter ring): big rrect minus inner -> fake with a slightly inset solid band
    add_board(W-0.001, H-0.001, ds, R, M_SPACER, 'spacer', z=db+ds/2)
    top_z = db+ds
    add_board(W, H, dt, R, M_PCB, 'frontboard', z=top_z+dt/2)
    cassette_face(top_z+dt)
    # USB-C notch hint + bottom-edge head window/capstan features
    for x in (-0.018, 0.0, 0.018):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -H/2+0.001, db+ds*0.5))
        o=_new(); o.scale=(0.006,0.0016,ds*0.5); o.data.materials.append(M_DARK)

def _weld(pre, board_name):
    """Convert any text since `pre` to mesh and join all new meshes into the board; return it."""
    new = [o for o in bpy.data.objects if o not in pre]
    fonts = [o for o in new if o.type == 'FONT']
    if fonts:
        bpy.ops.object.select_all(action='DESELECT')
        for o in fonts: o.select_set(True)
        bpy.context.view_layer.objects.active = fonts[0]
        bpy.ops.object.convert(target='MESH')
    board = [o for o in new if o.name.startswith(board_name)][0]
    bpy.ops.object.select_all(action='DESELECT')
    for o in new:
        if o.type == 'MESH': o.select_set(True)
    bpy.context.view_layer.objects.active = board
    bpy.ops.object.join()
    for m in list(board.modifiers):
        if m.type == 'BEVEL':   # bevel would eat the small welded ring/trace geometry
            board.modifiers.remove(m)
    return board

def build_C():
    d = 0.0016
    pre = set(bpy.data.objects)
    add_board(W, H, d, R, M_FLEX, 'flexboard', z=d/2)
    cassette_face(d, flex=True)
    board = _weld(pre, 'flexboard')
    sd = board.modifiers.new('bend', 'SIMPLE_DEFORM'); sd.deform_method = 'BEND'
    sd.angle = math.radians(18); sd.deform_axis = 'Y'
    board.location.z += 0.005
    board.rotation_euler.x = math.radians(-3)

def build_D():
    # flat flex J-card front panel (crisp art) + a real folded spine + tuck at the right edge
    d = 0.0010
    Wd, Hd = 0.100, 0.063
    add_board(Wd, Hd, d, 0.004, M_FLEX, 'front', z=d/2)
    cassette_face(d, flex=True)
    # spine: hinge welded to local origin (left edge), folds up at the right edge
    sw = 0.013
    sp = add_board(sw, Hd, d, 0.0008, M_FLEX, 'spine', z=0)
    for v in sp.data.vertices: v.co.x += sw/2
    sp.location = (Wd/2, 0, d/2)
    sp.rotation_euler.y = math.radians(-82)
    # tuck flap continues the fold, parented to the spine's far edge
    tw = 0.016
    tk = add_board(tw, Hd, d, 0.0008, M_FLEX, 'tuck', z=0)
    for v in tk.data.vertices: v.co.x += tw/2
    tk.parent = sp
    tk.location = (sw, 0, 0)
    tk.rotation_euler.y = math.radians(-92)

# ---------------- run ----------------
studio()
{'A':build_A,'B':build_B,'C':build_C,'D':build_D}.get(SPEC, build_B)()
bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0] + '.blend')
print(f'FLEXI_RENDER scene built spec={SPEC} (+.blend)')
if bpy.app.background:                      # headless: render. GUI (make blend): just open the scene, press F12.
    bpy.ops.render.render(write_still=True)
    print(f'FLEXI_RENDER done spec={SPEC} -> {OUT}')
