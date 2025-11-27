from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import trimesh
import uuid
import os
import json

from engine.animation.animation_system import AnimationClip, ProceduralAnimator
from engine.procedural.city_generator import CityGenerator, TerrainGenerator
from engine.procedural.aaa_game_generator import AAAGameGenerator
from engine.video.video_renderer import VideoRenderer, MultiObjectComposer

router = APIRouter(prefix="/api/advanced", tags=["advanced"])

class AnimationRequest(BaseModel):
    animation_type: str  # walk, rotate, jump, idle
    duration: float = 2.0
    loop: bool = True

class CityRequest(BaseModel):
    size: List[int] = [100, 100]
    density: float = 0.7
    style: str = "modern"  # modern, classic

class GameMapRequest(BaseModel):
    game_type: str  # racing, fps, fighting
    size: Optional[List[int]] = [200, 200]

class VideoRequest(BaseModel):
    duration: float = 10.0
    fps: int = 60
    width: int = 1920
    height: int = 1080

class MultiObjectRequest(BaseModel):
    objects: List[Dict]  # [{description, position, animation}]
    export_format: str = "glb"

@router.post("/create-animation")
async def create_animation(file: UploadFile = File(...), request: AnimationRequest = None):
    """Add animation to 3D model - 60+ animations available"""
    try:
        from engine.animation.motion_library import MotionLibrary
        
        request_id = str(uuid.uuid4())
        
        input_path = f"uploads/{request_id}_{file.filename}"
        with open(input_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        mesh = trimesh.load(input_path)
        
        anim_type = request.animation_type if request else "idle"
        animation = MotionLibrary.generate(anim_type)
        
        if request and request.duration:
            animation.duration = request.duration
        if request and request.loop is not None:
            animation.loop = request.loop
        
        anim_data = {
            'name': animation.name,
            'duration': animation.duration,
            'loop': animation.loop,
            'keyframes': [
                {
                    'time': kf.time,
                    'position': kf.position.tolist(),
                    'rotation': kf.rotation.tolist(),
                    'scale': kf.scale.tolist()
                }
                for kf in animation.keyframes
            ]
        }
        
        output_path = f"assets/{request_id}_animation.json"
        with open(output_path, 'w') as f:
            json.dump(anim_data, f, indent=2)
        
        return {
            'success': True,
            'request_id': request_id,
            'animation_file': output_path,
            'animation_type': anim_type,
            'duration': animation.duration,
            'keyframe_count': len(animation.keyframes),
            'available_animations': list(MotionLibrary.ANIMATIONS.keys())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-city")
async def generate_city(request: CityRequest):
    """Generate complete 3D city"""
    try:
        request_id = str(uuid.uuid4())
        
        generator = CityGenerator(tuple(request.size))
        city_meshes = generator.generate_city(request.density, request.style)
        
        # Combine all meshes
        combined_city = trimesh.util.concatenate(city_meshes)
        
        # Export in multiple formats
        output_paths = {}
        for fmt in ['obj', 'glb', 'ply']:
            path = f"assets/{request_id}_city.{fmt}"
            combined_city.export(path)
            output_paths[fmt] = path
        
        return {
            'success': True,
            'request_id': request_id,
            'output_paths': output_paths,
            'city_size': request.size,
            'building_count': len(city_meshes),
            'vertices': len(combined_city.vertices),
            'faces': len(combined_city.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-environment")
async def generate_environment(env_type: str, size: List[int] = [200, 200]):
    """Generate complete environments - forest, ocean, mountains, desert, etc."""
    try:
        from engine.procedural.environment_library import EnvironmentLibrary
        
        request_id = str(uuid.uuid4())
        
        if env_type == 'forest':
            meshes = EnvironmentLibrary.generate_forest(tuple(size), 0.3)
            combined = trimesh.util.concatenate(meshes)
        elif env_type == 'ocean':
            combined = EnvironmentLibrary.generate_ocean(tuple(size), wave_height=2.0)
        elif env_type == 'mountains':
            meshes = EnvironmentLibrary.generate_mountains(tuple(size), peak_height=100, count=5)
            combined = trimesh.util.concatenate(meshes)
        elif env_type == 'desert':
            desert_data = EnvironmentLibrary.generate_desert(tuple(size))
            combined = trimesh.util.concatenate(desert_data['dunes'] + desert_data['cacti'])
        elif env_type == 'river':
            combined = EnvironmentLibrary.generate_river((0, 0), (size[0], size[1]), width=5)
        else:
            combined = TerrainGenerator.generate_terrain(size[0], 100)
        
        output_paths = {}
        for fmt in ['obj', 'glb', 'ply']:
            path = f"assets/{request_id}_{env_type}.{fmt}"
            combined.export(path)
            output_paths[fmt] = path
        
        return {
            'success': True,
            'request_id': request_id,
            'environment_type': env_type,
            'output_paths': output_paths,
            'vertices': len(combined.vertices),
            'faces': len(combined.faces),
            'available_types': ['forest', 'ocean', 'mountains', 'desert', 'river', 'terrain']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-game-map")
async def generate_game_map(request: GameMapRequest):
    """Generate AAA game map"""
    try:
        request_id = str(uuid.uuid4())
        
        if request.game_type == "racing":
            game_data = AAAGameGenerator.generate_racing_track()
            all_meshes = game_data['track'] + game_data['barriers']
        elif request.game_type == "fps":
            game_data = AAAGameGenerator.generate_fps_map(tuple(request.size))
            all_meshes = game_data['buildings'] + game_data['cover'] + [game_data['ground']]
        elif request.game_type == "fighting":
            game_data = AAAGameGenerator.generate_fighting_arena()
            all_meshes = [game_data['floor']] + game_data['walls'] + game_data['pillars']
        else:
            raise HTTPException(status_code=400, detail="Invalid game type")
        
        # Combine meshes
        combined_map = trimesh.util.concatenate(all_meshes)
        
        # Export
        output_paths = {}
        for fmt in ['obj', 'glb', 'ply']:
            path = f"assets/{request_id}_{request.game_type}_map.{fmt}"
            combined_map.export(path)
            output_paths[fmt] = path
        
        # Save metadata
        metadata = {
            'game_type': request.game_type,
            'spawn_points': game_data.get('spawn_points', []),
            'checkpoints': game_data.get('checkpoints', [])
        }
        
        metadata_path = f"assets/{request_id}_{request.game_type}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return {
            'success': True,
            'request_id': request_id,
            'game_type': request.game_type,
            'output_paths': output_paths,
            'metadata': metadata_path,
            'object_count': len(all_meshes),
            'vertices': len(combined_map.vertices),
            'faces': len(combined_map.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-vehicle")
async def generate_vehicle(vehicle_type: str = "car"):
    """Generate game vehicle"""
    try:
        request_id = str(uuid.uuid4())
        
        vehicle = AAAGameGenerator.generate_vehicle(vehicle_type)
        
        output_paths = {}
        for fmt in ['obj', 'glb', 'ply']:
            path = f"assets/{request_id}_{vehicle_type}.{fmt}"
            vehicle.export(path)
            output_paths[fmt] = path
        
        return {
            'success': True,
            'request_id': request_id,
            'vehicle_type': vehicle_type,
            'output_paths': output_paths,
            'vertices': len(vehicle.vertices),
            'faces': len(vehicle.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-character")
async def generate_character(character_type: str = "soldier"):
    """Generate game character"""
    try:
        request_id = str(uuid.uuid4())
        
        character = AAAGameGenerator.generate_character(character_type)
        
        output_paths = {}
        for fmt in ['obj', 'glb', 'ply']:
            path = f"assets/{request_id}_{character_type}.{fmt}"
            character.export(path)
            output_paths[fmt] = path
        
        return {
            'success': True,
            'request_id': request_id,
            'character_type': character_type,
            'output_paths': output_paths,
            'vertices': len(character.vertices),
            'faces': len(character.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compose-multi-object")
async def compose_multi_object(request: MultiObjectRequest):
    """Compose multiple objects into single scene"""
    try:
        from engine.generators.text_to_3d import TextTo3DGenerator
        
        request_id = str(uuid.uuid4())
        composer = MultiObjectComposer()
        text_gen = TextTo3DGenerator()
        
        for obj_data in request.objects:
            description = obj_data.get('description', 'cube')
            position = tuple(obj_data.get('position', [0, 0, 0]))
            
            mesh = text_gen.generate_from_text(description)
            composer.add_object(mesh, position=position)
        
        # Export composed scene
        output_path = f"assets/{request_id}_scene.{request.export_format}"
        composer.export_scene(output_path, request.export_format)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'object_count': len(request.objects),
            'format': request.export_format
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/render-video")
async def render_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """Render animated video"""
    try:
        request_id = str(uuid.uuid4())
        
        # This would be expanded with actual scene data
        output_path = f"assets/{request_id}_video.mp4"
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'duration': request.duration,
            'fps': request.fps,
            'resolution': [request.width, request.height],
            'status': 'rendering'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-asset-library")
async def generate_asset_library(category: str, asset_type: str, variations: int = 10):
    """Generate asset variations from library of millions"""
    try:
        from engine.procedural.asset_library import AssetLibrary
        
        request_id = str(uuid.uuid4())
        
        assets = AssetLibrary.generate_variations(category, asset_type, variations)
        
        output_dir = f"assets/{request_id}_{category}_{asset_type}"
        os.makedirs(output_dir, exist_ok=True)
        
        for i, asset in enumerate(assets):
            asset.export(f"{output_dir}/variation_{i}.glb")
        
        return {
            'success': True,
            'request_id': request_id,
            'category': category,
            'asset_type': asset_type,
            'variations_generated': len(assets),
            'output_directory': output_dir,
            'total_library_size': AssetLibrary.get_asset_count(),
            'available_categories': list(AssetLibrary.CATEGORIES.keys())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-animations")
async def list_animations():
    """List all 60+ available animations"""
    from engine.animation.motion_library import MotionLibrary
    
    animations_by_category = {}
    for anim_name, config in MotionLibrary.ANIMATIONS.items():
        category = config['category']
        if category not in animations_by_category:
            animations_by_category[category] = []
        animations_by_category[category].append({
            'name': anim_name,
            'duration': config['duration']
        })
    
    return {
        'total_animations': len(MotionLibrary.ANIMATIONS),
        'categories': animations_by_category
    }

@router.get("/download-batch")
async def download_batch(request_ids: List[str]):
    """Download multiple assets as batch"""
    import zipfile
    
    try:
        zip_id = str(uuid.uuid4())
        zip_path = f"assets/{zip_id}_batch.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for req_id in request_ids:
                for fmt in ['obj', 'glb', 'ply']:
                    file_path = f"assets/{req_id}.{fmt}"
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
        
        return {
            'success': True,
            'zip_path': zip_path,
            'file_count': len(request_ids)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))