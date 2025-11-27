import os
import json
import hashlib
import sqlite3
import threading
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import trimesh
import numpy as np
from pathlib import Path
import pickle
import gzip

@dataclass
class AssetMetadata:
    asset_id: str
    asset_type: str
    source_type: str
    source_data: str
    file_path: str
    file_size: int
    created_at: float
    last_accessed: float
    access_count: int
    tags: List[str]
    properties: Dict[str, Any]
    checksum: str

class AssetManagerComplete:
    """Complete Asset Manager - Full Production"""
    
    def __init__(self, asset_directory: str = "assets"):
        self.asset_directory = Path(asset_directory)
        self.db_path = self.asset_directory / "database" / "assets.db"
        self.memory_cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        self._init_directories()
        self._init_database()
    
    def _init_directories(self):
        dirs = [
            "models/characters", "models/vehicles", "models/buildings", "models/props", "models/nature", "models/weapons",
            "textures/diffuse", "textures/normal", "textures/roughness", "textures/metallic", "textures/ao", "textures/emissive", "textures/height",
            "materials/pbr", "materials/shaders", "materials/presets",
            "animations/characters", "animations/vehicles", "animations/objects",
            "audio/music", "audio/sfx", "audio/voice",
            "scenes/levels", "scenes/prefabs", "scenes/environments",
            "scripts/gameplay", "scripts/ai", "scripts/ui",
            "ui/icons", "ui/fonts", "ui/layouts",
            "particles/effects", "particles/textures",
            "cache/meshes", "cache/textures", "cache/scenes",
            "generated/text_to_3d", "generated/image_to_3d", "generated/giga", "generated/worlds", "generated/games", "generated/cartoons",
            "database"
        ]
        for d in dirs:
            (self.asset_directory / d).mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY, asset_type TEXT, source_type TEXT, source_data TEXT,
                file_path TEXT, file_size INTEGER, created_at REAL, last_accessed REAL,
                access_count INTEGER, tags TEXT, properties TEXT, checksum TEXT)''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_type ON assets(asset_type)')
    
    def store_mesh(self, mesh: trimesh.Trimesh, source_type: str, source_data: str, tags: List[str] = None) -> str:
        asset_id = hashlib.sha256(f"{source_type}:{source_data}".encode()).hexdigest()[:16]
        file_path = self.asset_directory / "models" / f"{asset_id}.obj"
        mesh.export(str(file_path))
        
        metadata = AssetMetadata(
            asset_id=asset_id, asset_type='mesh', source_type=source_type, source_data=source_data,
            file_path=str(file_path), file_size=os.path.getsize(file_path), created_at=time.time(),
            last_accessed=time.time(), access_count=1, tags=tags or [], properties={},
            checksum=hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''INSERT OR REPLACE INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                (metadata.asset_id, metadata.asset_type, metadata.source_type, metadata.source_data,
                 metadata.file_path, metadata.file_size, metadata.created_at, metadata.last_accessed,
                 metadata.access_count, json.dumps(metadata.tags), json.dumps(metadata.properties), metadata.checksum))
        
        self.memory_cache[asset_id] = mesh
        return asset_id
    
    def load_mesh(self, asset_id: str) -> Optional[trimesh.Trimesh]:
        if asset_id in self.memory_cache:
            return self.memory_cache[asset_id]
        
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute('SELECT file_path FROM assets WHERE asset_id = ?', (asset_id,)).fetchone()
            if row and os.path.exists(row[0]):
                mesh = trimesh.load(row[0])
                self.memory_cache[asset_id] = mesh
                return mesh
        return None
    
    def get_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute('SELECT COUNT(*) FROM assets').fetchone()[0]
            by_type = {}
            for row in conn.execute('SELECT asset_type, COUNT(*) FROM assets GROUP BY asset_type'):
                by_type[row[0]] = row[1]
        
        return {
            'total_assets': total,
            'by_type': by_type,
            'cache_size': len(self.memory_cache),
            'storage_path': str(self.asset_directory)
        }
