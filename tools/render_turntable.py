#!/usr/bin/env python3
"""
Atelier Nilaya — Blender Turntable Studio Renderer (render_turntable.py)
Automates 360-degree turntable rendering of 3D CAD jewellery models (.glb / .gltf)
using Blender's Python API (bpy).

Features:
- PBR Metal Shaders: Yellow gold (22K/24K), Rose gold (18K), Platinum (950), Silver (925)
  with metallic 1.0, calibrated base color, and micro-roughness.
- Preserves gemstone materials (refractive indices, dispersion, and faceted brilliance).
- Three-light softbox studio setup (Key, Fill, Rim) on a seamless #f6f6f6 backdrop.
- 36 frames at 1200x1200 square resolution rotated 10 degrees per frame around vertical Z-axis.
- Saves frames directly to:
    static/products/<slug>/<metal>/spin/001.webp ... 036.webp
    static/products/<slug>/<metal>/front.webp, side.webp, top.webp

================================================================================
EXACT BLENDER CLI INVOCATION:
================================================================================
blender -b -P tools/render_turntable.py -- --input path/to/model.glb --slug aarohi-solitaire --metal yellow_gold

Optional parameters:
  --frames 36                 (Default: 36 frames, 10 degrees each)
  --output-dir static/products (Default: static/products)
  --resolution 1200           (Default: 1200px)
  --format WEBP               (Default: WEBP, quality 82)
================================================================================
"""

import sys
import os
import math

# Check if running inside Blender
try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False

# Metal Physical Material Presets (PBR Principled BSDF)
METAL_PRESETS = {
    'yellow_gold': {
        'name': 'Atelier_Yellow_Gold_22K',
        'color': (0.902, 0.776, 0.529, 1.0), # #E6C687
        'metallic': 1.0,
        'roughness': 0.20
    },
    'rose_gold': {
        'name': 'Atelier_Rose_Gold_18K',
        'color': (0.886, 0.655, 0.580, 1.0), # #E2A794
        'metallic': 1.0,
        'roughness': 0.22
    },
    'platinum': {
        'name': 'Atelier_Platinum_950',
        'color': (0.898, 0.910, 0.925, 1.0), # #E5E8EC
        'metallic': 1.0,
        'roughness': 0.16
    },
    'silver': {
        'name': 'Atelier_Silver_925',
        'color': (0.847, 0.863, 0.878, 1.0), # #D8DCE0
        'metallic': 1.0,
        'roughness': 0.28
    }
}

def parse_cli_args():
    args = {
        'input': None,
        'slug': 'jewellery-piece',
        'metal': 'yellow_gold',
        'output_dir': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'products'),
        'frames': 36,
        'resolution': 1200,
        'format': 'WEBP',
        'quality': 82
    }
    
    if '--' in sys.argv:
        custom_args = sys.argv[sys.argv.index('--') + 1:]
        i = 0
        while i < len(custom_args):
            key = custom_args[i]
            if key == '--input' and i + 1 < len(custom_args):
                args['input'] = custom_args[i + 1]
                i += 2
            elif key == '--slug' and i + 1 < len(custom_args):
                args['slug'] = custom_args[i + 1]
                i += 2
            elif key == '--metal' and i + 1 < len(custom_args):
                args['metal'] = custom_args[i + 1]
                i += 2
            elif key == '--output-dir' and i + 1 < len(custom_args):
                args['output_dir'] = custom_args[i + 1]
                i += 2
            elif key == '--frames' and i + 1 < len(custom_args):
                args['frames'] = int(custom_args[i + 1])
                i += 2
            elif key == '--resolution' and i + 1 < len(custom_args):
                args['resolution'] = int(custom_args[i + 1])
                i += 2
            else:
                i += 1
    return args

def setup_studio_scene(res=1200):
    # Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # Render settings
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100

    # Backdrop #f6f6f6
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.965, 0.965, 0.965, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0

    # Camera
    cam_data = bpy.data.cameras.new("MacroCamera")
    cam_data.lens = 85 # 85mm macro lens
    cam_obj = bpy.data.objects.new("MacroCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, -2.2, 0.8)
    cam_obj.rotation_euler = (math.radians(72), 0, 0)

    # 1. Key Light (Softbox 45 deg right)
    key_data = bpy.data.lights.new("KeyLight", type='AREA')
    key_data.energy = 160.0
    key_data.size = 1.5
    key_data.color = (1.0, 0.96, 0.92)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    scene.collection.objects.link(key_obj)
    key_obj.location = (1.8, -1.8, 2.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-35))

    # 2. Fill Light (Softbox 45 deg left)
    fill_data = bpy.data.lights.new("FillLight", type='AREA')
    fill_data.energy = 85.0
    fill_data.size = 2.0
    fill_data.color = (0.95, 0.98, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.location = (-1.8, -1.5, 1.5)
    fill_obj.rotation_euler = (math.radians(45), math.radians(-15), math.radians(35))

    # 3. Rim/Top Light
    rim_data = bpy.data.lights.new("RimLight", type='AREA')
    rim_data.energy = 110.0
    rim_data.size = 1.2
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.location = (0, 1.8, 2.5)
    rim_obj.rotation_euler = (math.radians(-45), 0, math.radians(180))

    return scene, cam_obj

def apply_metal_material(imported_objects, metal_type='yellow_gold'):
    preset = METAL_PRESETS.get(metal_type, METAL_PRESETS['yellow_gold'])
    
    mat = bpy.data.materials.new(name=preset['name'])
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    
    if bsdf:
        bsdf.inputs['Base Color'].default_value = preset['color']
        bsdf.inputs['Metallic'].default_value = preset['metallic']
        bsdf.inputs['Roughness'].default_value = preset['roughness']

    for obj in imported_objects:
        if obj.type == 'MESH':
            # Check existing material names; only replace metal, keep gemstones untouched
            for slot in obj.material_slots:
                mat_name = slot.material.name.lower() if slot.material else ''
                is_gem = any(g in mat_name for g in ['stone', 'gem', 'diamond', 'sapphire', 'emerald', 'pearl', 'glass'])
                if not is_gem:
                    slot.material = mat

def render_sequence(args):
    if not IN_BLENDER:
        print("ERROR: This script must be run inside Blender using the CLI:")
        print(f"blender -b -P {__file__} -- --input <model.glb> --slug <slug> --metal <metal>")
        sys.exit(1)

    if not args['input'] or not os.path.exists(args['input']):
        print(f"ERROR: Input .glb file not found: {args['input']}")
        sys.exit(1)

    slug = args['slug']
    metal = args['metal']
    frames = args['frames']
    res = args['resolution']

    metal_dir = os.path.join(args['output_dir'], slug, metal)
    spin_dir = os.path.join(metal_dir, 'spin')
    os.makedirs(spin_dir, exist_ok=True)

    print(f"Starting Turntable Studio Render for {slug} [{metal}] ({frames} frames @ {res}x{res})...")

    scene, cam_obj = setup_studio_scene(res=res)

    # Import GLB
    bpy.ops.import_scene.gltf(filepath=args['input'])
    imported_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    # Apply selected PBR metal preset
    apply_metal_material(imported_objects, metal)

    # Parent all mesh objects to an empty at origin for clean Z-axis rotation
    empty = bpy.data.objects.new("TurntableCenter", None)
    scene.collection.objects.link(empty)
    for obj in imported_objects:
        obj.parent = empty

    scene.render.image_settings.file_format = 'WEBP'
    scene.render.image_settings.quality = args['quality']

    # Render 36 frames
    step_deg = 360.0 / frames
    for i in range(1, frames + 1):
        angle = math.radians((i - 1) * step_deg)
        empty.rotation_euler = (0, 0, angle)
        
        frame_num = f"{i:03d}"
        output_file = os.path.join(spin_dir, f"{frame_num}.webp")
        scene.render.filepath = output_file
        bpy.ops.render.render(write_still=True)
        print(f"  Rendered frame {frame_num}/{frames} -> {output_file}")

    # Render still views: front (0 deg), side (90 deg), top
    empty.rotation_euler = (0, 0, 0)
    scene.render.filepath = os.path.join(metal_dir, 'front.webp')
    bpy.ops.render.render(write_still=True)

    empty.rotation_euler = (0, 0, math.radians(90))
    scene.render.filepath = os.path.join(metal_dir, 'side.webp')
    bpy.ops.render.render(write_still=True)

    # Top view camera position
    cam_obj.location = (0, 0, 2.2)
    cam_obj.rotation_euler = (0, 0, 0)
    scene.render.filepath = os.path.join(metal_dir, 'top.webp')
    bpy.ops.render.render(write_still=True)

    print(f"\nCompleted turntable render for {slug} [{metal}].")

if __name__ == '__main__':
    args = parse_cli_args()
    if IN_BLENDER:
        render_sequence(args)
    else:
        print(__doc__)
