# Complete Asset File Extensions - All Categories

## 3D MODELS - Primary Asset Files

### Standard 3D Formats (Required for ALL 3D assets)
- **`.obj`** - Wavefront OBJ (Universal, required for all models)
- **`.fbx`** - Autodesk FBX (Required for animated models)
- **`.glb`** - Binary glTF (Required for web/real-time)
- **`.gltf`** - glTF JSON (Alternative web format)
- **`.usd`** - Universal Scene Description (High-end production)

### Additional 3D Formats (Optional but supported)
- **`.usda`** - USD ASCII format
- **`.usdc`** - USD Binary format
- **`.abc`** - Alembic (Animation cache)
- **`.dae`** - COLLADA (Interchange format)
- **`.blend`** - Blender native
- **`.stl`** - Stereolithography (3D printing)
- **`.ply`** - Polygon File Format
- **`.3ds`** - 3D Studio format
- **`.x3d`** - Web 3D format
- **`.mesh`** - Custom compressed binary

### Which Extensions for Each Asset Type:

**Animals (500+ species):**
- Primary: `.obj`, `.fbx`, `.glb`
- With animations: `.fbx` (required), `.abc`, `.gltf`
- Example: `lion.obj`, `lion.fbx`, `lion.glb`

**People (28,800 variations):**
- Primary: `.obj`, `.fbx`, `.glb`
- With animations: `.fbx` (required), `.abc`
- With clothing: `.obj` + `.fbx` per outfit
- Example: `doctor_male_adult.obj`, `doctor_male_adult.fbx`

**Vehicles (1000+ types):**
- Primary: `.obj`, `.fbx`, `.glb`, `.usd`
- With animations: `.fbx` (wheels, doors, etc.)
- Example: `ferrari_f40.obj`, `ferrari_f40.fbx`, `ferrari_f40.glb`

**Buildings (unlimited):**
- Primary: `.obj`, `.fbx`, `.glb`, `.usd`
- Large buildings: `.usd` (better for complex scenes)
- Example: `skyscraper_01.obj`, `skyscraper_01.usd`

**Nature (10,000+ objects):**
- Trees: `.obj`, `.fbx`, `.glb`
- Plants: `.obj`, `.glb`
- Rocks: `.obj`, `.glb`
- Example: `oak_tree.obj`, `oak_tree.fbx`

**Furniture (500+ types):**
- Primary: `.obj`, `.fbx`, `.glb`
- Example: `sofa_modern.obj`, `sofa_modern.glb`

**Weapons (100+ types):**
- Primary: `.obj`, `.fbx`, `.glb`
- With animations: `.fbx` (required)
- Example: `ak47.obj`, `ak47.fbx`

**Food (500+ types):**
- Primary: `.obj`, `.glb`
- Example: `apple.obj`, `apple.glb`

## TEXTURES - Required for ALL 3D Models

### PBR Texture Maps (Required for realistic rendering)
- **`.png`** - Diffuse/Albedo (Required, lossless with alpha)
- **`.jpg`** - Diffuse/Albedo (Alternative, compressed)
- **`.png`** - Normal maps (Required for detail)
- **`.png`** - Roughness maps (Required for PBR)
- **`.png`** - Metallic maps (Required for PBR)
- **`.png`** - Ambient Occlusion (Required for shadows)
- **`.png`** - Emissive maps (Optional, for glowing parts)
- **`.exr`** - HDR textures (Optional, high dynamic range)

### Texture Naming Convention:
- `{asset_name}_diffuse.png` - Base color
- `{asset_name}_normal.png` - Normal map
- `{asset_name}_roughness.png` - Roughness map
- `{asset_name}_metallic.png` - Metallic map
- `{asset_name}_ao.png` - Ambient occlusion
- `{asset_name}_emissive.png` - Emissive map
- `{asset_name}_height.png` - Height/displacement map

### Example for a Car:
```
ferrari_f40.obj
ferrari_f40_diffuse.png
ferrari_f40_normal.png
ferrari_f40_roughness.png
ferrari_f40_metallic.png
ferrari_f40_ao.png
```

### Texture Resolutions (Required):
- **Small objects** (food, tools): 1024x1024 or 2048x2048
- **Medium objects** (furniture, weapons): 2048x2048 or 4096x4096
- **Large objects** (vehicles, buildings): 4096x4096 or 8192x8192
- **Characters** (people, animals): 2048x2048 or 4096x4096

## MATERIALS - Shader Definitions

### Material Files (Required for each asset)
- **`.json`** - Material definition (Required)
- **`.mat`** - Material file (Alternative)
- **`.mtl`** - Wavefront material (For .obj files)

### Shader Files (Optional, for custom rendering)
- **`.glsl`** - OpenGL shaders
- **`.hlsl`** - DirectX shaders
- **`.shader`** - Unity shaders

### Example Material JSON:
```json
{
  "name": "ferrari_f40_material",
  "diffuse": "ferrari_f40_diffuse.png",
  "normal": "ferrari_f40_normal.png",
  "roughness": "ferrari_f40_roughness.png",
  "metallic": "ferrari_f40_metallic.png",
  "ao": "ferrari_f40_ao.png"
}
```

## ANIMATIONS - For Animated Assets

### Animation Formats (Required for animated models)
- **`.fbx`** - Primary animation format (Required)
- **`.bvh`** - BioVision Hierarchy (Motion capture)
- **`.abc`** - Alembic cache (Complex animations)
- **`.anim`** - Animation data
- **`.gltf`** - glTF with animations

### Animation Files Needed:
**Animals (with movement):**
- `lion_walk.fbx`
- `lion_run.fbx`
- `lion_idle.fbx`
- `lion_attack.fbx`
- `lion_eat.fbx`

**People (with actions):**
- `doctor_walk.fbx`
- `doctor_run.fbx`
- `doctor_idle.fbx`
- `doctor_work.fbx`
- `doctor_wave.fbx`

**Vehicles (with movement):**
- `ferrari_wheels_rotate.fbx`
- `ferrari_door_open.fbx`
- `ferrari_suspension.fbx`

## AUDIO - Sound Effects

### Audio Formats (Required for interactive assets)
- **`.wav`** - Uncompressed (High quality, required)
- **`.ogg`** - Compressed (Game audio, required)
- **`.mp3`** - Compressed (Alternative)

### Audio Files Needed:
**Animals:**
- `lion_roar.wav`
- `lion_growl.wav`
- `lion_footsteps.wav`

**Vehicles:**
- `ferrari_engine_idle.wav`
- `ferrari_engine_rev.wav`
- `ferrari_horn.wav`
- `ferrari_door_open.wav`

**Weapons:**
- `ak47_fire.wav`
- `ak47_reload.wav`
- `ak47_empty.wav`

## SCENES - Complete Environments

### Scene Formats
- **`.json`** - Scene definition (Required)
- **`.scene`** - Custom scene format
- **`.unity`** - Unity scene
- **`.unreal`** - Unreal scene

## SCRIPTS - Behavior & Logic

### Script Formats
- **`.py`** - Python scripts (AI, gameplay)
- **`.lua`** - Lua scripts (Game logic)
- **`.js`** - JavaScript (Web integration)

## COMPLETE FILE STRUCTURE FOR EACH ASSET

### Example: Lion (Animal)
```
assets/animals/mammals/lion/
├── lion.obj                    # 3D model (required)
├── lion.fbx                    # Animated model (required)
├── lion.glb                    # Web format (required)
├── lion_diffuse.png           # Base color texture (required)
├── lion_normal.png            # Normal map (required)
├── lion_roughness.png         # Roughness map (required)
├── lion_metallic.png          # Metallic map (required)
├── lion_ao.png                # Ambient occlusion (required)
├── lion.json                  # Material definition (required)
├── lion_walk.fbx              # Walk animation (required)
├── lion_run.fbx               # Run animation (required)
├── lion_idle.fbx              # Idle animation (required)
├── lion_attack.fbx            # Attack animation (required)
├── lion_roar.wav              # Roar sound (required)
├── lion_growl.wav             # Growl sound (required)
└── lion_footsteps.wav         # Footstep sounds (required)
```

### Example: Ferrari F40 (Vehicle)
```
assets/vehicles/cars/sports/ferrari_f40/
├── ferrari_f40.obj            # 3D model (required)
├── ferrari_f40.fbx            # Animated model (required)
├── ferrari_f40.glb            # Web format (required)
├── ferrari_f40.usd            # High-end format (optional)
├── ferrari_f40_diffuse.png    # Base color (required)
├── ferrari_f40_normal.png     # Normal map (required)
├── ferrari_f40_roughness.png  # Roughness (required)
├── ferrari_f40_metallic.png   # Metallic (required)
├── ferrari_f40_ao.png         # AO (required)
├── ferrari_f40.json           # Material (required)
├── ferrari_f40_wheels.fbx     # Wheel animation (required)
├── ferrari_f40_doors.fbx      # Door animation (required)
├── ferrari_f40_engine.wav     # Engine sound (required)
├── ferrari_f40_horn.wav       # Horn sound (required)
└── ferrari_f40_brake.wav      # Brake sound (required)
```

### Example: Doctor (Person)
```
assets/people/professions/medical/doctor/
├── doctor_male_adult.obj      # 3D model (required)
├── doctor_male_adult.fbx      # Animated model (required)
├── doctor_male_adult.glb      # Web format (required)
├── doctor_diffuse.png         # Skin/clothing texture (required)
├── doctor_normal.png          # Normal map (required)
├── doctor_roughness.png       # Roughness (required)
├── doctor_metallic.png        # Metallic (required)
├── doctor_ao.png              # AO (required)
├── doctor.json                # Material (required)
├── doctor_walk.fbx            # Walk animation (required)
├── doctor_run.fbx             # Run animation (required)
├── doctor_idle.fbx            # Idle animation (required)
├── doctor_work.fbx            # Working animation (required)
├── doctor_footsteps.wav       # Footstep sounds (required)
└── doctor_voice.wav           # Voice samples (optional)
```

### Example: Skyscraper (Building)
```
assets/buildings/commercial/skyscraper_01/
├── skyscraper_01.obj          # 3D model (required)
├── skyscraper_01.fbx          # Model with LODs (required)
├── skyscraper_01.glb          # Web format (required)
├── skyscraper_01.usd          # High-end format (recommended)
├── skyscraper_diffuse.png     # Base texture (required, 8192x8192)
├── skyscraper_normal.png      # Normal map (required)
├── skyscraper_roughness.png   # Roughness (required)
├── skyscraper_metallic.png    # Metallic (required)
├── skyscraper_ao.png          # AO (required)
├── skyscraper_emissive.png    # Window lights (required)
└── skyscraper.json            # Material (required)
```

## SUMMARY: REQUIRED EXTENSIONS BY CATEGORY

### 3D Models (ALL assets need these):
✅ `.obj` - Universal format (REQUIRED)
✅ `.fbx` - Animated format (REQUIRED for animated assets)
✅ `.glb` - Web/real-time format (REQUIRED)
✅ `.usd` - High-end format (OPTIONAL but recommended for large scenes)

### Textures (ALL 3D models need these):
✅ `_diffuse.png` - Base color (REQUIRED)
✅ `_normal.png` - Normal map (REQUIRED)
✅ `_roughness.png` - Roughness map (REQUIRED)
✅ `_metallic.png` - Metallic map (REQUIRED)
✅ `_ao.png` - Ambient occlusion (REQUIRED)
✅ `_emissive.png` - Emissive map (OPTIONAL, for glowing parts)

### Materials (ALL assets need):
✅ `.json` - Material definition (REQUIRED)
✅ `.mtl` - Wavefront material (REQUIRED for .obj files)

### Animations (Animated assets need):
✅ `.fbx` - Animation files (REQUIRED for each animation)
✅ `.bvh` - Motion capture (OPTIONAL)
✅ `.abc` - Animation cache (OPTIONAL)

### Audio (Interactive assets need):
✅ `.wav` - Sound effects (REQUIRED)
✅ `.ogg` - Compressed audio (REQUIRED for games)

## TOTAL FILES PER ASSET TYPE

**Simple Static Object** (e.g., apple):
- 3 model files (.obj, .glb, .mesh)
- 5 texture files (diffuse, normal, roughness, metallic, ao)
- 1 material file (.json)
- **Total: 9 files**

**Animated Character** (e.g., lion):
- 3 model files (.obj, .fbx, .glb)
- 5 texture files
- 1 material file
- 5 animation files (walk, run, idle, attack, eat)
- 3 audio files (roar, growl, footsteps)
- **Total: 17 files**

**Complex Vehicle** (e.g., car):
- 4 model files (.obj, .fbx, .glb, .usd)
- 6 texture files (including emissive for lights)
- 1 material file
- 3 animation files (wheels, doors, suspension)
- 5 audio files (engine, horn, brake, door, crash)
- **Total: 19 files**

**Large Building** (e.g., skyscraper):
- 4 model files (.obj, .fbx, .glb, .usd)
- 6 texture files (high resolution)
- 1 material file
- **Total: 11 files**
