from fastapi import APIRouter, File, UploadFile, HTTPException, Header
from typing import Optional, List
import trimesh
import uuid
import os
import time
import aiofiles

router = APIRouter(prefix="/api/giga", tags=["giga_extensions"])

@router.post("/generate-animal")
async def generate_animal(animal_type: str, species: str, detail: int = 5, api_key: Optional[str] = Header(None)):
    """Generate any animal (500+ species)"""
    start_time = time.time()
    try:
        from engine.generators.giga_world_generator import GigaWorldGenerator
        
        request_id = str(uuid.uuid4())
        animal = GigaWorldGenerator.generate_animal(animal_type, species, detail)
        
        os.makedirs("assets/animals", exist_ok=True)
        output_path = f"assets/animals/{request_id}_{species}.glb"
        animal.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'animal_type': animal_type,
            'species': species,
            'vertices': len(animal.vertices),
            'faces': len(animal.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-person")
async def generate_person(profession: str = 'civilian', age: str = 'adult', 
                         body_type: str = 'average', pose: str = 'standing',
                         gender: str = 'male', detail: int = 5, api_key: Optional[str] = Header(None)):
    """Generate person (100+ variations)"""
    start_time = time.time()
    try:
        from engine.generators.giga_world_generator import GigaWorldGenerator
        
        request_id = str(uuid.uuid4())
        person = GigaWorldGenerator.generate_person(profession, age, body_type, pose, gender, detail)
        
        os.makedirs("assets/people", exist_ok=True)
        output_path = f"assets/people/{request_id}_{profession}_{age}.glb"
        person.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'profession': profession,
            'age': age,
            'pose': pose,
            'vertices': len(person.vertices),
            'faces': len(person.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-world-object")
async def generate_world_object(category: str, object_type: str, detail: int = 5, api_key: Optional[str] = Header(None)):
    """Generate any real-world object"""
    start_time = time.time()
    try:
        from engine.generators.giga_world_generator import GigaWorldGenerator
        
        request_id = str(uuid.uuid4())
        obj = GigaWorldGenerator.generate_all_world_objects(category, object_type, detail)
        
        os.makedirs(f"assets/{category}", exist_ok=True)
        output_path = f"assets/{category}/{request_id}_{object_type}.glb"
        obj.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'category': category,
            'object_type': object_type,
            'vertices': len(obj.vertices),
            'faces': len(obj.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-complete-game")
async def generate_complete_game(game_type: str, size: int = 10000, api_key: Optional[str] = Header(None)):
    """Generate complete AAA game"""
    start_time = time.time()
    try:
        from engine.generators.giga_game_generator import GigaGameGenerator
        
        request_id = str(uuid.uuid4())
        
        if game_type == 'open_world':
            game_data = GigaGameGenerator.generate_open_world_game(size, 'modern')
        elif game_type == 'fps':
            game_data = GigaGameGenerator.generate_fps_game(10, 50)
        elif game_type == 'racing':
            game_data = GigaGameGenerator.generate_racing_game(20, 100)
        elif game_type == 'rpg':
            game_data = GigaGameGenerator.generate_rpg_game(size, 50)
        elif game_type == 'survival':
            game_data = GigaGameGenerator.generate_survival_game(size, 10000)
        elif game_type == 'battle_royale':
            game_data = GigaGameGenerator.generate_battle_royale_game(size, 100)
        else:
            raise HTTPException(status_code=400, detail="Invalid game type")
        
        output_dir = f"assets/games/{request_id}_{game_type}"
        os.makedirs(output_dir, exist_ok=True)
        
        asset_count = 0
        for category, items in game_data.items():
            if isinstance(items, list) and len(items) > 0:
                cat_dir = f"{output_dir}/{category}"
                os.makedirs(cat_dir, exist_ok=True)
                for i, item in enumerate(items[:100]):
                    if hasattr(item, 'export'):
                        item.export(f"{cat_dir}/{i}.glb")
                        asset_count += 1
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'game_type': game_type,
            'output_directory': output_dir,
            'asset_count': asset_count,
            'categories': list(game_data.keys()),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-cartoon-advanced")
async def generate_cartoon_advanced(character_type: str = 'hero', style: str = 'disney', api_key: Optional[str] = Header(None)):
    """Generate advanced cartoon character"""
    start_time = time.time()
    try:
        from engine.core.giga_cartoon_engine import GigaCartoonEngine
        
        request_id = str(uuid.uuid4())
        character = GigaCartoonEngine.generate_cartoon_character_advanced(character_type, style)
        
        os.makedirs("assets/cartoons", exist_ok=True)
        output_path = f"assets/cartoons/{request_id}_{character_type}_{style}.glb"
        character.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'character_type': character_type,
            'style': style,
            'vertices': len(character.vertices),
            'faces': len(character.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-cartoon-world")
async def generate_cartoon_world(world_type: str = 'fantasy', size: int = 5000, style: str = 'disney', api_key: Optional[str] = Header(None)):
    """Generate complete cartoon world"""
    start_time = time.time()
    try:
        from engine.core.giga_cartoon_engine import GigaCartoonEngine
        
        request_id = str(uuid.uuid4())
        world = GigaCartoonEngine.generate_cartoon_world(world_type, size, style)
        
        combined = trimesh.util.concatenate(world)
        os.makedirs("assets/cartoons", exist_ok=True)
        output_path = f"assets/cartoons/{request_id}_{world_type}_world.glb"
        combined.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'world_type': world_type,
            'style': style,
            'objects': len(world),
            'vertices': len(combined.vertices),
            'faces': len(combined.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-prompt-ai")
async def generate_from_prompt_ai(prompt: str, style: str = 'realistic', detail: int = 5, api_key: Optional[str] = Header(None)):
    """AI-powered generation from any prompt"""
    start_time = time.time()
    try:
        from engine.generators.giga_world_generator import GigaWorldGenerator
        
        request_id = str(uuid.uuid4())
        obj = GigaWorldGenerator.generate_from_prompt_advanced(prompt, style, detail)
        
        output_path = f"assets/{request_id}_ai_generated.glb"
        obj.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'prompt': prompt,
            'style': style,
            'vertices': len(obj.vertices),
            'faces': len(obj.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-image-ai")
async def generate_from_image_ai(file: UploadFile = File(...), style: str = 'realistic', detail: int = 5, api_key: Optional[str] = Header(None)):
    """AI-powered 3D from image"""
    start_time = time.time()
    try:
        from engine.generators.giga_world_generator import GigaWorldGenerator
        
        request_id = str(uuid.uuid4())
        
        image_path = f"uploads/{request_id}_{file.filename}"
        async with aiofiles.open(image_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        obj = GigaWorldGenerator.generate_from_image_advanced(image_path, style, detail)
        
        output_path = f"assets/{request_id}_from_image.glb"
        obj.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'input_image': image_path,
            'style': style,
            'vertices': len(obj.vertices),
            'faces': len(obj.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-animals")
async def list_animals():
    """List all available animals"""
    from engine.generators.giga_world_generator import GigaWorldGenerator
    return {'animals': GigaWorldGenerator.ANIMALS, 'total': sum(len(v) for v in GigaWorldGenerator.ANIMALS.values())}

@router.get("/list-people")
async def list_people():
    """List all people variations"""
    from engine.generators.giga_world_generator import GigaWorldGenerator
    return {'people': GigaWorldGenerator.PEOPLE}

@router.get("/list-cartoon-styles")
async def list_cartoon_styles():
    """List all cartoon styles"""
    from engine.core.giga_cartoon_engine import GigaCartoonEngine
    return {'styles': list(GigaCartoonEngine.CARTOON_STYLES.keys())}
