# Advanced 3D Game Engine API Documentation

## Overview
Production-ready API for 3D model generation, conversion, and game integration.

## Base URL
```
http://localhost:5000
```

## Core Features

### 1. Text-to-3D Generation
**Endpoint:** `POST /api/generate/text`

**Request:**
```json
{
  "description": "large metallic spinning tower with rough texture",
  "position": [0, 0, 0],
  "enable_physics": true,
  "physics_properties": {
    "mass": 10.0,
    "friction": 0.7,
    "restitution": 0.3
  },
  "quality": "high"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "abc123",
  "model_paths": {
    "obj": "assets/abc123.obj",
    "ply": "assets/abc123.ply",
    "stl": "assets/abc123.stl"
  },
  "vertices": 5420,
  "faces": 10840
}
```

### 2. Image-to-3D Conversion
**Endpoint:** `POST /api/generate/image`

**Request:** Multipart form-data with image file

**Parameters:**
- `method`: "advanced", "photogrammetry", "volumetric"
- `position`: [x, y, z]
- `enable_physics`: boolean

**Response:**
```json
{
  "success": true,
  "request_id": "def456",
  "model_paths": {
    "obj": "assets/def456.obj",
    "ply": "assets/def456.ply",
    "stl": "assets/def456.stl"
  },
  "vertices": 8192,
  "faces": 16384
}
```

### 3. 3D-to-Cartoon Conversion
**Endpoint:** `POST /api/convert/3d-to-cartoon`

**Request:** Multipart form-data with 3D model file

**Parameters:**
```json
{
  "style": "cel_shaded",
  "add_outlines": true,
  "outline_thickness": 3,
  "color_levels": 8
}
```

**Styles:**
- `cel_shaded`: Classic cel-shading effect
- `toon`: Aggressive toon shading
- `anime`: Anime-style rendering
- `comic`: Comic book style

**Response:**
```json
{
  "success": true,
  "request_id": "ghi789",
  "style": "cel_shaded",
  "output_paths": {
    "obj": "assets/ghi789_cartoon.obj",
    "ply": "assets/ghi789_cartoon.ply",
    "glb": "assets/ghi789_cartoon.glb"
  },
  "vertices": 3200,
  "faces": 6400
}
```

### 4. 3D-to-Game Conversion
**Endpoint:** `POST /api/convert/3d-to-game`

**Request:** Multipart form-data with 3D model file

**Parameters:**
```json
{
  "object_type": "dynamic_object",
  "generate_lods": true,
  "generate_collision": true,
  "generate_navmesh": false,
  "collision_type": "convex",
  "physics_enabled": true,
  "mass": 1.0,
  "friction": 0.5,
  "restitution": 0.3
}
```

**Object Types:**
- `static_mesh`: Non-moving environment objects
- `dynamic_object`: Physics-enabled objects
- `character`: Player/NPC characters
- `vehicle`: Drivable vehicles
- `prop`: Interactive props
- `collectible`: Pickup items
- `obstacle`: Barriers
- `platform`: Moving platforms

**Collision Types:**
- `box`: Oriented bounding box
- `sphere`: Bounding sphere
- `convex`: Convex hull
- `mesh`: Simplified mesh
- `capsule`: Capsule (for characters)

**Response:**
```json
{
  "success": true,
  "request_id": "jkl012",
  "object_type": "dynamic_object",
  "output_directory": "assets/jkl012_game",
  "files": {
    "main_mesh": "assets/jkl012_game/model.obj",
    "glb": "assets/jkl012_game/model.glb",
    "metadata": "assets/jkl012_game/model_metadata.json",
    "navmesh": "assets/jkl012_game/model_navmesh.obj"
  },
  "lods": [
    "assets/jkl012_game/model_LOD0.obj",
    "assets/jkl012_game/model_LOD1.obj",
    "assets/jkl012_game/model_LOD2.obj",
    "assets/jkl012_game/model_LOD3.obj"
  ],
  "collision_meshes": {
    "box": "assets/jkl012_game/model_collision_box.obj",
    "sphere": "assets/jkl012_game/model_collision_sphere.obj",
    "convex": "assets/jkl012_game/model_collision_convex.obj",
    "mesh": "assets/jkl012_game/model_collision_mesh.obj"
  },
  "properties": {
    "object_type": "dynamic_object",
    "collision_type": "convex",
    "physics_enabled": true,
    "mass": 1.0,
    "friction": 0.5,
    "restitution": 0.3
  },
  "bounds": {
    "min": [-1.5, -1.0, -1.5],
    "max": [1.5, 2.0, 1.5],
    "center": [0, 0.5, 0],
    "extents": [3.0, 3.0, 3.0],
    "radius": 2.12
  }
}
```

### 5. Text-to-Cartoon
**Endpoint:** `POST /api/convert/text-to-cartoon`

**Parameters:**
- `description`: Text description
- `style`: Cartoon style

**Response:** Same as 3D-to-Cartoon

### 6. Text-to-Game
**Endpoint:** `POST /api/convert/text-to-game`

**Parameters:**
- `description`: Text description
- `object_type`: Game object type

**Response:** Same as 3D-to-Game

### 7. Image-to-Cartoon
**Endpoint:** `POST /api/convert/image-to-cartoon`

**Request:** Multipart form-data with image file

**Parameters:**
- `style`: Cartoon style

**Response:** Same as 3D-to-Cartoon

### 8. Image-to-Game
**Endpoint:** `POST /api/convert/image-to-game`

**Request:** Multipart form-data with image file

**Parameters:**
- `object_type`: Game object type

**Response:** Same as 3D-to-Game

## Session Management

### Create Session
**Endpoint:** `POST /api/session/create`

**Response:**
```json
{
  "session_id": "uuid-here",
  "status": "created",
  "websocket_url": "/ws/uuid-here"
}
```

### Delete Session
**Endpoint:** `DELETE /api/session/{session_id}`

### List Objects
**Endpoint:** `GET /api/session/{session_id}/objects`

### Update Object
**Endpoint:** `PUT /api/session/{session_id}/object/{object_id}`

### Apply Force
**Endpoint:** `POST /api/session/{session_id}/object/{object_id}/force`

### Remove Object
**Endpoint:** `DELETE /api/session/{session_id}/object/{object_id}`

## WebSocket API

**Endpoint:** `ws://localhost:5000/ws/{session_id}`

**Messages:**
```json
{
  "type": "generate_text",
  "description": "red cube",
  "position": [0, 0, 0]
}
```

**Events:**
- `object_added`
- `object_updated`
- `object_removed`
- `force_applied`
- `collision`

## Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123,
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "memory_available": 8589934592
  },
  "active_sessions": 3,
  "active_connections": 5
}
```

## Download Files
**Endpoint:** `GET /download/{file_id}?format=obj`

**Formats:** obj, ply, stl, glb

## Complete Workflow Examples

### Example 1: Text → Cartoon → Game
```bash
# Step 1: Generate from text
curl -X POST http://localhost:5000/api/convert/text-to-cartoon \
  -H "Content-Type: application/json" \
  -d '{"description": "cute robot character", "style": "anime"}'

# Step 2: Convert to game asset
curl -X POST http://localhost:5000/api/convert/3d-to-game \
  -F "file=@assets/abc123_cartoon.obj" \
  -F 'request={"object_type": "character", "generate_lods": true}'
```

### Example 2: Image → 3D → Cartoon
```bash
# Step 1: Image to 3D
curl -X POST http://localhost:5000/api/generate/image \
  -F "file=@photo.jpg" \
  -F 'request={"method": "advanced"}'

# Step 2: Apply cartoon style
curl -X POST http://localhost:5000/api/convert/3d-to-cartoon \
  -F "file=@assets/def456.obj" \
  -F 'request={"style": "comic", "add_outlines": true}'
```

### Example 3: Direct Image → Game
```bash
curl -X POST http://localhost:5000/api/convert/image-to-game \
  -F "file=@building.jpg" \
  -F "object_type=static_mesh"
```

## Error Responses

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error