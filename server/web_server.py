from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import asyncio
import aiofiles
import aioredis
import json
import os
import sys
import uuid
import time
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import threading
from celery import Celery
import psutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.generators.text_to_3d import TextTo3DGenerator
from engine.generators.image_to_3d import ImageTo3DGenerator
from engine.core.game_engine import GameEngine

# Pydantic models
class TextGenerationRequest(BaseModel):
    description: str
    position: Optional[List[float]] = [0, 0, 0]
    enable_physics: Optional[bool] = True
    physics_properties: Optional[Dict] = None
    quality: Optional[str] = "high"
    material_override: Optional[Dict] = None

class ImageGenerationRequest(BaseModel):
    position: Optional[List[float]] = [0, 0, 0]
    method: Optional[str] = "advanced"
    enable_physics: Optional[bool] = True
    physics_properties: Optional[Dict] = None

class ObjectUpdateRequest(BaseModel):
    position: Optional[List[float]] = None
    rotation: Optional[List[float]] = None
    scale: Optional[List[float]] = None

class ForceRequest(BaseModel):
    force: List[float]
    point: Optional[List[float]] = None

class SceneRequest(BaseModel):
    objects: List[Dict]
    lighting: Optional[Dict] = None
    camera: Optional[Dict] = None

# Initialize FastAPI app
app = FastAPI(
    title="Advanced 3D Game Engine API",
    description="Self-hosted 3D model generation and game engine",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs('assets', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize components
text_gen = TextTo3DGenerator()
image_gen = ImageTo3DGenerator()
executor = ThreadPoolExecutor(max_workers=4)

# Game engine instances (for multi-session support)
game_engines: Dict[str, GameEngine] = {}
active_sessions: Dict[str, Dict] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if session_id:
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            self.session_connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str = None):
        self.active_connections.remove(websocket)
        if session_id and session_id in self.session_connections:
            self.session_connections[session_id].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def send_to_session(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for connection in self.session_connections[session_id]:
                await connection.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Celery for background tasks
celery_app = Celery(
    'game_engine',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.task
def generate_text_model_task(description: str, session_id: str, request_id: str):
    """Background task for text-to-3D generation"""
    try:
        mesh = text_gen.generate_from_text(description)
        
        # Save mesh
        output_path = f"assets/{request_id}.obj"
        mesh.export(output_path)
        
        # Save additional formats
        mesh.export(f"assets/{request_id}.ply")
        mesh.export(f"assets/{request_id}.stl")
        
        return {
            'success': True,
            'request_id': request_id,
            'model_path': output_path,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
            'formats': ['obj', 'ply', 'stl']
        }
    except Exception as e:
        return {
            'success': False,
            'request_id': request_id,
            'error': str(e)
        }

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Advanced 3D Game Engine API",
        "version": "2.0.0",
        "features": [
            "Text-to-3D Generation",
            "Image-to-3D Conversion",
            "Real-time Physics",
            "Advanced Rendering",
            "Multi-session Support",
            "WebSocket Integration"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available": memory.available
        },
        "active_sessions": len(active_sessions),
        "active_connections": len(manager.active_connections)
    }

@app.post("/api/session/create")
async def create_session():
    """Create new game engine session"""
    session_id = str(uuid.uuid4())
    
    # Initialize game engine for session
    game_engines[session_id] = GameEngine(enable_physics=True)
    active_sessions[session_id] = {
        'created_at': time.time(),
        'objects': {},
        'last_activity': time.time()
    }
    
    return {
        "session_id": session_id,
        "status": "created",
        "websocket_url": f"/ws/{session_id}"
    }

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete game engine session"""
    if session_id in game_engines:
        # Cleanup game engine
        game_engines[session_id]._cleanup()
        del game_engines[session_id]
        del active_sessions[session_id]
        
        return {"status": "deleted"}
    
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/generate/text")
async def generate_from_text(request: TextGenerationRequest, background_tasks: BackgroundTasks, session_id: str = None):
    """Generate 3D model from text description"""
    try:
        request_id = str(uuid.uuid4())
        
        if session_id and session_id in game_engines:
            # Add to game engine directly
            engine = game_engines[session_id]
            obj_id = engine.add_object_from_text(
                request.description,
                tuple(request.position),
                request.enable_physics,
                request.physics_properties
            )
            
            active_sessions[session_id]['objects'][obj_id] = {
                'type': 'text',
                'description': request.description,
                'created_at': time.time()
            }
            
            # Notify WebSocket clients
            await manager.send_to_session(
                json.dumps({
                    'type': 'object_added',
                    'object_id': obj_id,
                    'description': request.description
                }),
                session_id
            )
            
            return {
                'success': True,
                'object_id': obj_id,
                'session_id': session_id,
                'description': request.description
            }
        else:
            # Generate mesh for download
            mesh = text_gen.generate_from_text(request.description)
            
            # Save in multiple formats
            output_paths = {}
            for format_type in ['obj', 'ply', 'stl']:
                path = f"assets/{request_id}.{format_type}"
                mesh.export(path)
                output_paths[format_type] = path
            
            return {
                'success': True,
                'request_id': request_id,
                'model_paths': output_paths,
                'vertices': len(mesh.vertices),
                'faces': len(mesh.faces),
                'description': request.description
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/image")
async def generate_from_image(file: UploadFile = File(...), 
                            request: ImageGenerationRequest = None,
                            session_id: str = None):
    """Generate 3D model from uploaded image"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        request_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = f"uploads/{request_id}_{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        if session_id and session_id in game_engines:
            # Add to game engine
            engine = game_engines[session_id]
            obj_id = engine.add_object_from_image(
                file_path,
                tuple(request.position) if request else (0, 0, 0),
                request.method if request else 'advanced',
                request.enable_physics if request else True,
                request.physics_properties if request else None
            )
            
            active_sessions[session_id]['objects'][obj_id] = {
                'type': 'image',
                'image_path': file_path,
                'created_at': time.time()
            }
            
            await manager.send_to_session(
                json.dumps({
                    'type': 'object_added',
                    'object_id': obj_id,
                    'image_path': file_path
                }),
                session_id
            )
            
            return {
                'success': True,
                'object_id': obj_id,
                'session_id': session_id,
                'image_path': file_path
            }
        else:
            # Generate mesh for download
            method = request.method if request else 'advanced'
            mesh = image_gen.generate_from_image(file_path, method)
            
            # Save in multiple formats
            output_paths = {}
            for format_type in ['obj', 'ply', 'stl']:
                path = f"assets/{request_id}.{format_type}"
                mesh.export(path)
                output_paths[format_type] = path
            
            return {
                'success': True,
                'request_id': request_id,
                'model_paths': output_paths,
                'vertices': len(mesh.vertices),
                'faces': len(mesh.faces),
                'original_image': file_path
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/session/{session_id}/object/{object_id}")
async def update_object(session_id: str, object_id: str, request: ObjectUpdateRequest):
    """Update object in session"""
    if session_id not in game_engines:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = game_engines[session_id]
    
    try:
        engine.update_object_transform(
            object_id,
            tuple(request.position) if request.position else None,
            tuple(request.rotation) if request.rotation else None,
            tuple(request.scale) if request.scale else None
        )
        
        await manager.send_to_session(
            json.dumps({
                'type': 'object_updated',
                'object_id': object_id,
                'position': request.position,
                'rotation': request.rotation,
                'scale': request.scale
            }),
            session_id
        )
        
        return {"success": True, "object_id": object_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/session/{session_id}/object/{object_id}/force")
async def apply_force(session_id: str, object_id: str, request: ForceRequest):
    """Apply force to object"""
    if session_id not in game_engines:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = game_engines[session_id]
    
    try:
        import numpy as np
        force = np.array(request.force)
        point = np.array(request.point) if request.point else None
        
        engine.apply_force(object_id, force, point)
        
        await manager.send_to_session(
            json.dumps({
                'type': 'force_applied',
                'object_id': object_id,
                'force': request.force,
                'point': request.point
            }),
            session_id
        )
        
        return {"success": True, "object_id": object_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/objects")
async def list_objects(session_id: str):
    """List all objects in session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "objects": active_sessions[session_id]['objects']
    }

@app.delete("/api/session/{session_id}/object/{object_id}")
async def remove_object(session_id: str, object_id: str):
    """Remove object from session"""
    if session_id not in game_engines:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = game_engines[session_id]
    engine.remove_object(object_id)
    
    if object_id in active_sessions[session_id]['objects']:
        del active_sessions[session_id]['objects'][object_id]
    
    await manager.send_to_session(
        json.dumps({
            'type': 'object_removed',
            'object_id': object_id
        }),
        session_id
    )
    
    return {"success": True, "object_id": object_id}

@app.get("/api/session/{session_id}/performance")
async def get_performance_stats(session_id: str):
    """Get performance statistics for session"""
    if session_id not in game_engines:
        raise HTTPException(status_code=404, detail="Session not found")
    
    engine = game_engines[session_id]
    stats = engine.get_performance_stats()
    
    return {
        "session_id": session_id,
        "performance": stats,
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
    }

@app.get("/download/{file_id}")
async def download_file(file_id: str, format: str = "obj"):
    """Download generated 3D model"""
    file_path = f"assets/{file_id}.{format}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=f"{file_id}.{format}"
    )

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'ping':
                await manager.send_personal_message(
                    json.dumps({'type': 'pong', 'timestamp': time.time()}),
                    websocket
                )
            elif message['type'] == 'generate_text':
                # Handle real-time text generation
                if session_id in game_engines:
                    engine = game_engines[session_id]
                    obj_id = engine.add_object_from_text(
                        message['description'],
                        tuple(message.get('position', [0, 0, 0]))
                    )
                    
                    await manager.send_to_session(
                        json.dumps({
                            'type': 'object_generated',
                            'object_id': obj_id,
                            'description': message['description']
                        }),
                        session_id
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

# Background task to cleanup inactive sessions
@app.on_event("startup")
async def startup_event():
    async def cleanup_sessions():
        while True:
            current_time = time.time()
            inactive_sessions = []
            
            for session_id, session_data in active_sessions.items():
                if current_time - session_data['last_activity'] > 3600:  # 1 hour timeout
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                if session_id in game_engines:
                    game_engines[session_id]._cleanup()
                    del game_engines[session_id]
                    del active_sessions[session_id]
            
            await asyncio.sleep(300)  # Check every 5 minutes
    
    asyncio.create_task(cleanup_sessions())

# Include conversion API extensions
from server.api_extensions import router as conversion_router
from server.advanced_api import router as advanced_router
from server.ultimate_api import router as giga_router
from server.giga_api_extensions import router as giga_ext_router
from server.customization_api import router as customization_router
from server.ultra_api import router as ultra_router
from server.mega_api import router as mega_router
from server.intelligence_api import router as intelligence_router
from server.mega_intelligence_api import router as mega_intelligence_router
from server.tera_engine_api import router as tera_router
from server.game_generation_api import router as game_router
from server.tera_training_api import router as training_router
from server.auth_api import router as auth_router
from server.download_api import router as download_router
app.include_router(conversion_router)
app.include_router(advanced_router)
app.include_router(giga_router)
app.include_router(giga_ext_router)
app.include_router(customization_router)
app.include_router(ultra_router)
app.include_router(mega_router)
app.include_router(intelligence_router)
app.include_router(mega_intelligence_router)
app.include_router(tera_router)
app.include_router(game_router)
app.include_router(training_router)
app.include_router(auth_router)
app.include_router(download_router)

if __name__ == '__main__':
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        workers=1
    )