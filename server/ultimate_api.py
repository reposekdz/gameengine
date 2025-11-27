from fastapi import APIRouter, File, UploadFile, HTTPException, Header
from pydantic import BaseModel
from typing import List, Dict, Optional
import trimesh
import uuid
import os
import json
import time
from database.models.db_manager import GigaDBManager

router = APIRouter(prefix="/api/giga", tags=["giga"])
db = GigaDBManager()

@router.post("/generate-universe")
async def generate_universe(galaxies: int = 100, size: int = 50000, api_key: Optional[str] = Header(None)):
    """Generate entire universe with galaxies"""
    start_time = time.time()
    try:
        if api_key:
            user = db.verify_api_key(api_key)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid API key")
            user_id = user['id']
        else:
            user_id = None
        
        from engine.generators.giga_generator import GigaGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'universe', f"Universe with {galaxies} galaxies", None, {'galaxies': galaxies, 'size': size}, user_id)
        
        meshes = GigaGenerator.generate_universe(size, galaxies)
        combined = trimesh.util.concatenate(meshes)
        
        output_path = f"assets/{request_id}_universe.glb"
        combined.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', [output_path], None, processing_time)
        
        asset_uuid = db.insert_asset(
            name=f"Universe_{galaxies}_galaxies",
            category='environment',
            asset_type='universe',
            style='realistic',
            vertices=len(combined.vertices),
            faces=len(combined.faces),
            files={'glb': output_path},
            metadata={'galaxies': galaxies, 'size': size, 'objects': len(meshes)},
            tags=['universe', 'space', 'procedural']
        )
        
        db.log_event('universe_generated', {'galaxies': galaxies, 'objects': len(meshes)}, user_id, request_id)
        
        return {
            'success': True,
            'request_id': request_id,
            'asset_uuid': asset_uuid,
            'output_path': output_path,
            'galaxies': galaxies,
            'total_objects': len(meshes),
            'vertices': len(combined.vertices),
            'faces': len(combined.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        db.update_generation(request_id, 'failed', None, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-planet")
async def generate_planet(radius: float = 6371, detail: int = 5, api_key: Optional[str] = Header(None)):
    """Generate realistic planet"""
    start_time = time.time()
    try:
        user_id = None
        if api_key:
            user = db.verify_api_key(api_key)
            if user:
                user_id = user['id']
        
        from engine.generators.giga_generator import GigaGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'planet', f"Planet radius {radius}", None, {'radius': radius, 'detail': detail}, user_id)
        
        planet = GigaGenerator.generate_planet(radius, detail)
        
        output_path = f"assets/{request_id}_planet.glb"
        planet.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', [output_path], None, processing_time)
        
        asset_uuid = db.insert_asset(
            name=f"Planet_R{radius}",
            category='environment',
            asset_type='planet',
            style='realistic',
            vertices=len(planet.vertices),
            faces=len(planet.faces),
            files={'glb': output_path},
            metadata={'radius': radius, 'detail': detail},
            tags=['planet', 'space', 'terrain']
        )
        
        return {
            'success': True,
            'request_id': request_id,
            'asset_uuid': asset_uuid,
            'output_path': output_path,
            'vertices': len(planet.vertices),
            'faces': len(planet.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-mega-city")
async def generate_mega_city(size: List[int] = [1000, 1000], style: str = "gta", api_key: Optional[str] = Header(None)):
    """Generate massive GTA 6 / Bad Guys style city"""
    start_time = time.time()
    try:
        user_id = None
        if api_key:
            user = db.verify_api_key(api_key)
            if user:
                user_id = user['id']
        
        from engine.procedural.mega_city_generator import MegaCityGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'city', f"Mega city {size[0]}x{size[1]}", None, {'size': size, 'style': style}, user_id)
        city_data = MegaCityGenerator.generate_mega_city(tuple(size), 0.9)
        
        all_meshes = []
        element_counts = {}
        
        for category, meshes in city_data.items():
            if meshes:
                all_meshes.extend(meshes)
                element_counts[category] = len(meshes)
        
        combined = trimesh.util.concatenate(all_meshes)
        
        output_paths = {}
        for fmt in ['obj', 'glb', 'ply']:
            path = f"assets/{request_id}_megacity.{fmt}"
            combined.export(path)
            output_paths[fmt] = path
        
        metadata = {
            'city_size': size,
            'style': style,
            'element_counts': element_counts,
            'total_objects': len(all_meshes)
        }
        
        metadata_path = f"assets/{request_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', list(output_paths.values()), None, processing_time)
        
        city_uuid = db.insert_city(
            name=f"MegaCity_{style}_{size[0]}x{size[1]}",
            size_x=size[0],
            size_z=size[1],
            style=style,
            density=0.9,
            total_objects=len(all_meshes),
            districts={},
            counts=element_counts,
            file_path=output_paths['glb'],
            metadata=metadata
        )
        
        db.log_event('city_generated', {'size': size, 'objects': len(all_meshes)}, user_id, request_id)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_paths': output_paths,
            'metadata': metadata_path,
            'total_objects': len(all_meshes),
            'element_counts': element_counts,
            'vertices': len(combined.vertices),
            'faces': len(combined.faces),
            'city_uuid': city_uuid,
            'processing_time_ms': processing_time
        }
    
    except Exception as e:
        db.update_generation(request_id, 'failed', None, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-cartoon-scene")
async def generate_cartoon_scene(
    objects: List[Dict],
    style: str = "toon",
    api_key: Optional[str] = Header(None)
):
    """Generate complete cartoon scene"""
    start_time = time.time()
    try:
        user_id = None
        if api_key:
            user = db.verify_api_key(api_key)
            if user:
                user_id = user['id']
        
        from engine.core.cartoon_engine import CartoonEngine
        from engine.generators.text_to_3d import TextTo3DGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'cartoon', f"Cartoon scene with {len(objects)} objects", None, {'objects': len(objects), 'style': style}, user_id)
        
        scene_objects = []
        for obj_desc in objects:
            mesh = TextTo3DGenerator.generate_from_description(obj_desc.get('description', 'cube'))
            scene_objects.append({
                'mesh': mesh,
                'position': obj_desc.get('position', [0, 0, 0]),
                'rotation': obj_desc.get('rotation', [0, 0, 0]),
                'scale': obj_desc.get('scale', 1.0)
            })
        
        scene = CartoonEngine.generate_cartoon_scene(scene_objects, style)
        
        output_path = f"assets/{request_id}_cartoon_scene.glb"
        scene.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', [output_path], None, processing_time)
        
        asset_uuid = db.insert_asset(
            name=f"CartoonScene_{style}",
            category='environment',
            asset_type='scene',
            style=style,
            vertices=len(scene.vertices),
            faces=len(scene.faces),
            files={'glb': output_path},
            metadata={'objects': len(objects), 'style': style},
            tags=['cartoon', 'scene', style]
        )
        
        return {
            'success': True,
            'request_id': request_id,
            'asset_uuid': asset_uuid,
            'output_path': output_path,
            'objects': len(objects),
            'vertices': len(scene.vertices),
            'faces': len(scene.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-multi-input")
async def generate_multi_input(
    text: str = None,
    images: List[UploadFile] = File(None),
    style: str = "realistic",
    api_key: Optional[str] = Header(None)
):
    """Generate 3 advanced objects from text, images, or both"""
    start_time = time.time()
    try:
        user_id = None
        if api_key:
            user = db.verify_api_key(api_key)
            if user:
                user_id = user['id']
        from engine.generators.multi_input_generator import MultiInputGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'multi_input', text, None, {'style': style, 'image_count': len(images) if images else 0}, user_id)
        
        image_paths = []
        if images:
            for img in images:
                img_path = f"uploads/{request_id}_{img.filename}"
                with open(img_path, 'wb') as f:
                    content = await img.read()
                    f.write(content)
                image_paths.append(img_path)
        
        objects = MultiInputGenerator.generate_from_multi_input(
            text=text,
            images=image_paths if image_paths else None,
            style=style
        )
        
        output_data = []
        for i, obj in enumerate(objects):
            obj_paths = {}
            for fmt in ['obj', 'glb', 'ply']:
                path = f"assets/{request_id}_object{i+1}.{fmt}"
                obj.export(path)
                obj_paths[fmt] = path
            
            output_data.append({
                'object_id': i + 1,
                'paths': obj_paths,
                'vertices': len(obj.vertices),
                'faces': len(obj.faces)
            })
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', [o['paths']['glb'] for o in output_data], None, processing_time)
        
        for i, obj_data in enumerate(output_data):
            asset_uuid = db.insert_asset(
                name=f"MultiInput_Object{i+1}",
                category='prop',
                asset_type='generated',
                style=style,
                vertices=obj_data['vertices'],
                faces=obj_data['faces'],
                files=obj_data['paths'],
                metadata={'source': 'multi_input', 'text': text},
                tags=['multi_input', style]
            )
            obj_data['asset_uuid'] = asset_uuid
        
        return {
            'success': True,
            'request_id': request_id,
            'objects_generated': 3,
            'style': style,
            'input_text': text,
            'input_images': len(image_paths),
            'objects': output_data,
            'processing_time_ms': processing_time
        }
    
    except Exception as e:
        db.update_generation(request_id, 'failed', None, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-vehicle-fleet")
async def generate_vehicle_fleet(count: int = 1000, vehicle_type: str = "mixed", api_key: Optional[str] = Header(None)):
    """Generate massive vehicle fleet"""
    start_time = time.time()
    try:
        user_id = None
        if api_key:
            user = db.verify_api_key(api_key)
            if user:
                user_id = user['id']
        
        from engine.generators.giga_generator import GigaGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'batch', f"Vehicle fleet {count} units", None, {'count': count, 'type': vehicle_type}, user_id)
        
        vehicles = GigaGenerator.generate_vehicle_fleet(count, vehicle_type)
        combined = trimesh.util.concatenate(vehicles)
        
        output_path = f"assets/{request_id}_fleet.glb"
        combined.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', [output_path], None, processing_time)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'vehicles': count,
            'type': vehicle_type,
            'vertices': len(combined.vertices),
            'faces': len(combined.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-batch")
async def generate_batch(text_prompts: List[str], count: int = 10, style: str = "realistic", api_key: Optional[str] = Header(None)):
    """Generate batch of objects"""
    start_time = time.time()
    try:
        user_id = None
        if api_key:
            user = db.verify_api_key(api_key)
            if user:
                user_id = user['id']
        from engine.generators.multi_input_generator import MultiInputGenerator
        
        request_id = str(uuid.uuid4())
        db.insert_generation(request_id, 'batch', f"Batch {count} objects", None, {'count': count, 'prompts': len(text_prompts), 'style': style}, user_id)
        
        objects = MultiInputGenerator.generate_batch(
            text_prompts=text_prompts,
            count=count,
            style=style
        )
        
        output_dir = f"assets/{request_id}_batch"
        os.makedirs(output_dir, exist_ok=True)
        
        for i, obj in enumerate(objects):
            obj.export(f"{output_dir}/object_{i}.glb")
        
        processing_time = int((time.time() - start_time) * 1000)
        db.update_generation(request_id, 'completed', [f"{output_dir}/object_{i}.glb" for i in range(len(objects))], None, processing_time)
        
        return {
            'success': True,
            'request_id': request_id,
            'objects_generated': len(objects),
            'output_directory': output_dir,
            'style': style,
            'processing_time_ms': processing_time
        }
    
    except Exception as e:
        db.update_generation(request_id, 'failed', None, str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get database statistics"""
    return db.get_stats()

@router.get("/asset/{asset_uuid}")
async def get_asset(asset_uuid: str):
    """Retrieve asset by UUID"""
    asset = db.get_asset(asset_uuid)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.get("/search")
async def search_assets(category: Optional[str] = None, style: Optional[str] = None, limit: int = 100):
    """Search assets"""
    return db.search_assets(category, style, None, limit)

@router.post("/user/create")
async def create_user(username: str, email: str, quota_daily: int = 1000):
    """Create new user"""
    user_id, api_key = db.create_user(username, email, quota_daily)
    return {'user_id': user_id, 'api_key': api_key, 'quota_daily': quota_daily}