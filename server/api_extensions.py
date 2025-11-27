from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import trimesh
import uuid
import os

from engine.generators.model_to_cartoon import CartoonStyler, NPRRenderer
from engine.generators.model_to_game import ModelToGameConverter, GameObjectType

router = APIRouter(prefix="/api/convert", tags=["conversion"])

# Initialize converters
cartoon_styler = CartoonStyler()
npr_renderer = NPRRenderer()
game_converter = ModelToGameConverter()

class CartoonConversionRequest(BaseModel):
    style: str = "cel_shaded"  # cel_shaded, toon, anime, comic
    add_outlines: bool = True
    outline_thickness: Optional[int] = 3
    color_levels: Optional[int] = 8

class GameConversionRequest(BaseModel):
    object_type: str = "prop"  # static_mesh, dynamic_object, character, vehicle, prop, collectible
    generate_lods: bool = True
    generate_collision: bool = True
    generate_navmesh: bool = False
    collision_type: str = "convex"  # box, sphere, convex, mesh, capsule
    physics_enabled: bool = True
    mass: float = 1.0
    friction: float = 0.5
    restitution: float = 0.3

@router.post("/3d-to-cartoon")
async def convert_3d_to_cartoon(file: UploadFile = File(...), request: CartoonConversionRequest = None):
    """Convert 3D model to cartoon style"""
    try:
        if not file.filename.endswith(('.obj', '.ply', '.stl', '.glb', '.gltf')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        request_id = str(uuid.uuid4())
        
        # Save uploaded file
        input_path = f"uploads/{request_id}_{file.filename}"
        with open(input_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Load mesh
        mesh = trimesh.load(input_path)
        
        # Apply cartoon style
        style = request.style if request else "cel_shaded"
        cartoon_mesh = cartoon_styler.convert_to_cartoon(mesh, style)
        
        # Add outlines if requested
        if request and request.add_outlines:
            npr_renderer.outline_width = request.outline_thickness or 3
            cartoon_mesh = npr_renderer.render_with_outlines(cartoon_mesh)
        
        # Save output
        output_paths = {}
        for fmt in ['obj', 'ply', 'stl', 'glb']:
            output_path = f"assets/{request_id}_cartoon.{fmt}"
            cartoon_mesh.export(output_path)
            output_paths[fmt] = output_path
        
        return {
            'success': True,
            'request_id': request_id,
            'style': style,
            'output_paths': output_paths,
            'vertices': len(cartoon_mesh.vertices),
            'faces': len(cartoon_mesh.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/3d-to-game")
async def convert_3d_to_game(file: UploadFile = File(...), request: GameConversionRequest = None):
    """Convert 3D model to game-ready asset"""
    try:
        if not file.filename.endswith(('.obj', '.ply', '.stl', '.glb', '.gltf')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        request_id = str(uuid.uuid4())
        
        # Save uploaded file
        input_path = f"uploads/{request_id}_{file.filename}"
        with open(input_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Load mesh
        mesh = trimesh.load(input_path)
        
        # Convert object type
        object_type_map = {
            'static_mesh': GameObjectType.STATIC_MESH,
            'dynamic_object': GameObjectType.DYNAMIC_OBJECT,
            'character': GameObjectType.CHARACTER,
            'vehicle': GameObjectType.VEHICLE,
            'prop': GameObjectType.PROP,
            'collectible': GameObjectType.COLLECTIBLE,
            'obstacle': GameObjectType.OBSTACLE,
            'platform': GameObjectType.PLATFORM
        }
        
        obj_type = object_type_map.get(request.object_type if request else 'prop', GameObjectType.PROP)
        
        # Custom properties
        custom_props = {}
        if request:
            custom_props = {
                'collision_type': request.collision_type,
                'physics_enabled': request.physics_enabled,
                'mass': request.mass,
                'friction': request.friction,
                'restitution': request.restitution
            }
        
        # Convert to game asset
        game_asset = game_converter.convert_to_game_asset(mesh, obj_type, custom_props)
        
        # Export game asset
        output_dir = f"assets/{request_id}_game"
        game_converter.export_game_asset(game_asset, output_dir, "model")
        
        # Prepare response
        response = {
            'success': True,
            'request_id': request_id,
            'object_type': obj_type.value,
            'output_directory': output_dir,
            'files': {
                'main_mesh': f"{output_dir}/model.obj",
                'glb': f"{output_dir}/model.glb",
                'metadata': f"{output_dir}/model_metadata.json"
            },
            'lods': [],
            'collision_meshes': {},
            'properties': game_asset['properties'].__dict__,
            'bounds': game_asset['bounds'],
            'metadata': game_asset['metadata']
        }
        
        # Add LOD paths
        if request and request.generate_lods:
            for i in range(len(game_asset['lods'])):
                response['lods'].append(f"{output_dir}/model_LOD{i}.obj")
        
        # Add collision mesh paths
        if request and request.generate_collision:
            for coll_type in game_asset['collision_meshes'].keys():
                response['collision_meshes'][coll_type] = f"{output_dir}/model_collision_{coll_type}.obj"
        
        # Add navmesh if generated
        if game_asset['navmesh']:
            response['files']['navmesh'] = f"{output_dir}/model_navmesh.obj"
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-cartoon")
async def text_to_cartoon(description: str, style: str = "cel_shaded"):
    """Generate cartoon 3D model from text"""
    try:
        from engine.generators.text_to_3d import TextTo3DGenerator
        
        request_id = str(uuid.uuid4())
        
        # Generate base mesh
        text_gen = TextTo3DGenerator()
        mesh = text_gen.generate_from_text(description)
        
        # Apply cartoon style
        cartoon_mesh = cartoon_styler.convert_to_cartoon(mesh, style)
        cartoon_mesh = npr_renderer.render_with_outlines(cartoon_mesh)
        
        # Save output
        output_paths = {}
        for fmt in ['obj', 'ply', 'glb']:
            output_path = f"assets/{request_id}_cartoon.{fmt}"
            cartoon_mesh.export(output_path)
            output_paths[fmt] = output_path
        
        return {
            'success': True,
            'request_id': request_id,
            'description': description,
            'style': style,
            'output_paths': output_paths,
            'vertices': len(cartoon_mesh.vertices),
            'faces': len(cartoon_mesh.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-game")
async def text_to_game(description: str, object_type: str = "prop"):
    """Generate game-ready asset from text"""
    try:
        from engine.generators.text_to_3d import TextTo3DGenerator
        
        request_id = str(uuid.uuid4())
        
        # Generate base mesh
        text_gen = TextTo3DGenerator()
        mesh = text_gen.generate_from_text(description)
        
        # Convert to game asset
        object_type_map = {
            'static_mesh': GameObjectType.STATIC_MESH,
            'dynamic_object': GameObjectType.DYNAMIC_OBJECT,
            'character': GameObjectType.CHARACTER,
            'vehicle': GameObjectType.VEHICLE,
            'prop': GameObjectType.PROP,
            'collectible': GameObjectType.COLLECTIBLE
        }
        
        obj_type = object_type_map.get(object_type, GameObjectType.PROP)
        game_asset = game_converter.convert_to_game_asset(mesh, obj_type)
        
        # Export
        output_dir = f"assets/{request_id}_game"
        game_converter.export_game_asset(game_asset, output_dir, "model")
        
        return {
            'success': True,
            'request_id': request_id,
            'description': description,
            'object_type': obj_type.value,
            'output_directory': output_dir,
            'files': {
                'main_mesh': f"{output_dir}/model.obj",
                'glb': f"{output_dir}/model.glb",
                'metadata': f"{output_dir}/model_metadata.json"
            },
            'properties': game_asset['properties'].__dict__,
            'metadata': game_asset['metadata']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image-to-cartoon")
async def image_to_cartoon(file: UploadFile = File(...), style: str = "cel_shaded"):
    """Generate cartoon 3D model from image"""
    try:
        from engine.generators.image_to_3d import ImageTo3DGenerator
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        request_id = str(uuid.uuid4())
        
        # Save uploaded image
        image_path = f"uploads/{request_id}_{file.filename}"
        with open(image_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Generate base mesh
        image_gen = ImageTo3DGenerator()
        mesh = image_gen.generate_from_image(image_path, method='advanced')
        
        # Apply cartoon style
        cartoon_mesh = cartoon_styler.convert_to_cartoon(mesh, style)
        cartoon_mesh = npr_renderer.render_with_outlines(cartoon_mesh)
        
        # Save output
        output_paths = {}
        for fmt in ['obj', 'ply', 'glb']:
            output_path = f"assets/{request_id}_cartoon.{fmt}"
            cartoon_mesh.export(output_path)
            output_paths[fmt] = output_path
        
        return {
            'success': True,
            'request_id': request_id,
            'style': style,
            'output_paths': output_paths,
            'vertices': len(cartoon_mesh.vertices),
            'faces': len(cartoon_mesh.faces)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image-to-game")
async def image_to_game(file: UploadFile = File(...), object_type: str = "prop"):
    """Generate game-ready asset from image"""
    try:
        from engine.generators.image_to_3d import ImageTo3DGenerator
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        request_id = str(uuid.uuid4())
        
        # Save uploaded image
        image_path = f"uploads/{request_id}_{file.filename}"
        with open(image_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Generate base mesh
        image_gen = ImageTo3DGenerator()
        mesh = image_gen.generate_from_image(image_path, method='advanced')
        
        # Convert to game asset
        object_type_map = {
            'static_mesh': GameObjectType.STATIC_MESH,
            'dynamic_object': GameObjectType.DYNAMIC_OBJECT,
            'character': GameObjectType.CHARACTER,
            'vehicle': GameObjectType.VEHICLE,
            'prop': GameObjectType.PROP,
            'collectible': GameObjectType.COLLECTIBLE
        }
        
        obj_type = object_type_map.get(object_type, GameObjectType.PROP)
        game_asset = game_converter.convert_to_game_asset(mesh, obj_type)
        
        # Export
        output_dir = f"assets/{request_id}_game"
        game_converter.export_game_asset(game_asset, output_dir, "model")
        
        return {
            'success': True,
            'request_id': request_id,
            'object_type': obj_type.value,
            'output_directory': output_dir,
            'files': {
                'main_mesh': f"{output_dir}/model.obj",
                'glb': f"{output_dir}/model.glb",
                'metadata': f"{output_dir}/model_metadata.json"
            },
            'properties': game_asset['properties'].__dict__,
            'metadata': game_asset['metadata']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))