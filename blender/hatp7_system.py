import bpy

print("Blender version:", bpy.app.version)

# --- 1. Полная очистка сцены ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 2. Наши измеренные параметры (1 BU = 1 R_sun) ---
R_STAR = 1.84
R_PLANET = R_STAR * (0.00628 ** 0.5)   # из измеренной глубины транзита
A_ORBIT = 0.0377 * 215.05              # AU -> R_sun
T_EFF = 6350.0                         # K, из литературы

# --- 3. Звезда ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=R_STAR, location=(0, 0, 0))
star = bpy.context.object
star.name = "HAT-P-7"
bpy.ops.object.shade_smooth()

mat = bpy.data.materials.new("StarMat")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
em = nt.nodes.new('ShaderNodeEmission')
bb = nt.nodes.new('ShaderNodeBlackbody')
bb.inputs['Temperature'].default_value = T_EFF   # физический цвет звезды!
nt.links.new(bb.outputs['Color'], em.inputs['Color'])
em.inputs['Strength'].default_value = 8.0
nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
star.data.materials.append(mat)

# --- 4. Планета ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=R_PLANET, location=(A_ORBIT, 0, 0))
planet = bpy.context.object
planet.name = "HAT-P-7b"
bpy.ops.object.shade_smooth()
pmat = bpy.data.materials.new("PlanetMat")
pmat.use_nodes = True
bsdf = pmat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.35, 0.32, 0.30, 1.0)
planet.data.materials.append(pmat)

# --- 5. Кольцо орбиты ---
bpy.ops.mesh.primitive_torus_add(major_radius=A_ORBIT, minor_radius=0.02,
                                 location=(0, 0, 0))
bpy.context.object.name = "Orbit"

# --- 6. Точечный свет в центре звезды ---
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
light = bpy.context.object
light.data.energy = 5000.0

# --- 7. Камера, смотрящая на начало координат ---
bpy.ops.object.camera_add(location=(0, -20, 8))
cam = bpy.context.object
cam.name = "Cam_System"
cam.data.clip_end = 10000.0
bpy.ops.object.empty_add(location=(0, 0, 0))
target = bpy.context.object
con = cam.constraints.new('TRACK_TO')
con.target = target
con.track_axis = 'TRACK_NEGATIVE_Z'
con.up_axis = 'UP_Y'
bpy.context.scene.camera = cam

print("Сцена создана. Звезда R=%.2f, планета R=%.3f на a=%.2f BU"
      % (R_STAR, R_PLANET, A_ORBIT))