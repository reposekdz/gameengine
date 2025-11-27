from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import trimesh
import uuid
import os
import time

router = APIRouter(prefix="/api/customize", tags=["customization"])

class CityCustomization(BaseModel):
    building_height_multiplier: Optional[float] = 1.0
    color_scheme: Optional[str] = 'modern'
    density: Optional[float] = 0.9
    architectural_style: Optional[str] = 'modern'
    weather: Optional[str] = None
    time_of_day: Optional[str] = 'day'
    detail_level: Optional[str] = 'high'

class PersonCustomization(BaseModel):
    skin_tone: Optional[str] = 'medium'
    height: Optional[float] = 1.0
    width: Optional[float] = 1.0
    muscle_definition: Optional[float] = 0.5
    clothing_color: Optional[List[int]] = [100, 100, 200]
    hair_style: Optional[str] = 'short'
    hair_color: Optional[List[int]] = [50, 30, 20]
    accessories: Optional[List[str]] = []
    facial_features: Optional[Dict] = {}

class CartoonCustomization(BaseModel):
    exaggeration: Optional[float] = 0.5
    saturation: Optional[float] = 1.5
    outline_thickness: Optional[float] = 0.08
    expression: Optional[str] = 'happy'
    animation_style: Optional[str] = 'bouncy'

class VehicleCustomization(BaseModel):
    paint_color: Optional[List[int]] = [255, 0, 0]
    metallic: Optional[float] = 0.8
    wear_level: Optional[float] = 0.0
    custom_parts: Optional[List[str]] = []
    decals: Optional[List[str]] = []

class AnimalCustomization(BaseModel):
    pattern: Optional[str] = None
    color_variation: Optional[float] = 0.1
    size_multiplier: Optional[float] = 1.0
    age: Optional[str] = 'adult'

@router.post("/city")
async def customize_city(asset_id: str, params: CityCustomization, api_key: Optional[str] = Header(None)):
    """Customize generated city"""
    start_time = time.time()
    try:
        from engine.core.customization_engine import CustomizationEngine
        
        # Load original city
        city_path = f"assets/{asset_id}_megacity.glb"
        if not os.path.exists(city_path):
            raise HTTPException(status_code=404, detail="City not found")
        
        city_mesh = trimesh.load(city_path)
        
        # Apply customizations
        customized = CustomizationEngine.customize_city([city_mesh], params.dict())
        combined = trimesh.util.concatenate(customized)
        
        # Save customized version
        request_id = str(uuid.uuid4())
        output_path = f"assets/{request_id}_customized_city.glb"
        combined.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'original_asset_id': asset_id,
            'customizations': params.dict(),
            'vertices': len(combined.vertices),
            'faces': len(combined.faces),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/person")
async def customize_person(asset_id: str, params: PersonCustomization, api_key: Optional[str] = Header(None)):
    """Customize generated person"""
    start_time = time.time()
    try:
        from engine.core.customization_engine import CustomizationEngine
        
        person_path = f"assets/people/{asset_id}.glb"
        if not os.path.exists(person_path):
            raise HTTPException(status_code=404, detail="Person not found")
        
        person_mesh = trimesh.load(person_path)
        customized = CustomizationEngine.customize_person(person_mesh, params.dict())
        
        request_id = str(uuid.uuid4())
        output_path = f"assets/people/{request_id}_customized.glb"
        customized.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'customizations': params.dict(),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cartoon")
async def customize_cartoon(asset_id: str, params: CartoonCustomization, api_key: Optional[str] = Header(None)):
    """Customize cartoon character"""
    start_time = time.time()
    try:
        from engine.core.customization_engine import CustomizationEngine
        
        cartoon_path = f"assets/cartoons/{asset_id}.glb"
        if not os.path.exists(cartoon_path):
            raise HTTPException(status_code=404, detail="Cartoon not found")
        
        cartoon_mesh = trimesh.load(cartoon_path)
        customized = CustomizationEngine.customize_cartoon(cartoon_mesh, params.dict())
        
        request_id = str(uuid.uuid4())
        output_path = f"assets/cartoons/{request_id}_customized.glb"
        customized.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'customizations': params.dict(),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vehicle")
async def customize_vehicle(asset_id: str, params: VehicleCustomization, api_key: Optional[str] = Header(None)):
    """Customize vehicle"""
    start_time = time.time()
    try:
        from engine.core.customization_engine import CustomizationEngine
        
        vehicle_path = f"assets/vehicles/{asset_id}.glb"
        if not os.path.exists(vehicle_path):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        vehicle_mesh = trimesh.load(vehicle_path)
        customized = CustomizationEngine.customize_vehicle(vehicle_mesh, params.dict())
        
        request_id = str(uuid.uuid4())
        output_path = f"assets/vehicles/{request_id}_customized.glb"
        customized.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'customizations': params.dict(),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/animal")
async def customize_animal(asset_id: str, params: AnimalCustomization, api_key: Optional[str] = Header(None)):
    """Customize animal"""
    start_time = time.time()
    try:
        from engine.core.customization_engine import CustomizationEngine
        
        animal_path = f"assets/animals/{asset_id}.glb"
        if not os.path.exists(animal_path):
            raise HTTPException(status_code=404, detail="Animal not found")
        
        animal_mesh = trimesh.load(animal_path)
        customized = CustomizationEngine.customize_animal(animal_mesh, params.dict())
        
        request_id = str(uuid.uuid4())
        output_path = f"assets/animals/{request_id}_customized.glb"
        customized.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'customizations': params.dict(),
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-pbr-materials")
async def apply_pbr_materials(asset_id: str, material_type: str, api_key: Optional[str] = Header(None)):
    """Apply photorealistic PBR materials"""
    start_time = time.time()
    try:
        from engine.algorithms.photorealistic_generator import PhotorealisticGenerator
        
        asset_path = f"assets/{asset_id}.glb"
        if not os.path.exists(asset_path):
            raise HTTPException(status_code=404, detail="Asset not found")
        
        mesh = trimesh.load(asset_path)
        materials = PhotorealisticGenerator.generate_pbr_materials(mesh, material_type)
        
        request_id = str(uuid.uuid4())
        output_path = f"assets/{request_id}_pbr.glb"
        mesh.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'material_type': material_type,
            'materials': {k: v for k, v in materials.items() if not isinstance(v, np.ndarray)},
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-realistic-lighting")
async def apply_realistic_lighting(asset_id: str, light_setup: str = 'studio', api_key: Optional[str] = Header(None)):
    """Apply realistic lighting"""
    start_time = time.time()
    try:
        from engine.algorithms.photorealistic_generator import PhotorealisticGenerator
        
        asset_path = f"assets/{asset_id}.glb"
        if not os.path.exists(asset_path):
            raise HTTPException(status_code=404, detail="Asset not found")
        
        mesh = trimesh.load(asset_path)
        lit_mesh = PhotorealisticGenerator.apply_realistic_lighting(mesh, light_setup)
        
        request_id = str(uuid.uuid4())
        output_path = f"assets/{request_id}_lit.glb"
        lit_mesh.export(output_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'request_id': request_id,
            'output_path': output_path,
            'light_setup': light_setup,
            'processing_time_ms': processing_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-preset")
async def save_preset(preset_name: str, params: Dict[str, Any], api_key: Optional[str] = Header(None)):
    """Save customization preset"""
    try:
        from engine.core.customization_engine import CustomizationEngine
        CustomizationEngine.save_customization_preset(preset_name, params)
        return {'success': True, 'preset_name': preset_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load-preset/{preset_name}")
async def load_preset(preset_name: str, api_key: Optional[str] = Header(None)):
    """Load customization preset"""
    try:
        from engine.core.customization_engine import CustomizationEngine
        params = CustomizationEngine.load_customization_preset(preset_name)
        return {'success': True, 'preset_name': preset_name, 'params': params}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
