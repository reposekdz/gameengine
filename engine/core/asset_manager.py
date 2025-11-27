import os
import json
import hashlib
import sqlite3
import threading
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import trimesh
import numpy as np
from pathlib import Path
import pickle
import gzip

@dataclass
class AssetMetadata:
    asset_id: str
    asset_type: str  # 'mesh', 'texture', 'material', 'scene'
    source_type: str  # 'text', 'image', 'file', 'procedural'
    source_data: str
    file_path: str
    file_size: int
    created_at: float
    last_accessed: float
    access_count: int
    tags: List[str]
    properties: Dict[str, Any]
    checksum: str

class AssetManager:
    def __init__(self, asset_directory: str = "assets", cache_size_mb: int = 500):
        self.asset_directory = Path(asset_directory)
        self.cache_directory = self.asset_directory / "cache"
        self.db_path = self.asset_directory / "assets.db"
        
        # Create directories
        self.asset_directory.mkdir(exist_ok=True)
        self.cache_directory.mkdir(exist_ok=True)
        
        # Cache settings
        self.max_cache_size = cache_size_mb * 1024 * 1024  # Convert to bytes
        self.memory_cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        
        # Initialize database
        self._init_database()
        
        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_running = True
        self.cleanup_thread.start()
    
    def _init_database(self):
        """Initialize SQLite database for asset metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_data TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    tags TEXT,
                    properties TEXT,
                    checksum TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_asset_type ON assets(asset_type)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_source_type ON assets(source_type)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON assets(last_accessed)
            ''')
    
    def store_mesh(self, mesh: trimesh.Trimesh, source_type: str, source_data: str, 
                   tags: List[str] = None, properties: Dict[str, Any] = None) -> str:
        """Store mesh asset and return asset ID"""
        
        # Generate asset ID from source data
        asset_id = self._generate_asset_id(source_type, source_data)
        
        # Check if asset already exists
        if self.asset_exists(asset_id):
            self._update_access_time(asset_id)
            return asset_id
        
        # Save mesh in multiple formats
        file_paths = {}
        formats = ['obj', 'ply', 'stl']
        
        for fmt in formats:
            file_path = self.asset_directory / f"{asset_id}.{fmt}"
            mesh.export(str(file_path))
            file_paths[fmt] = str(file_path)
        
        # Save compressed binary format for fast loading
        binary_path = self.cache_directory / f"{asset_id}.mesh"
        self._save_mesh_binary(mesh, binary_path)
        
        # Calculate file size and checksum
        primary_path = file_paths['obj']
        file_size = os.path.getsize(primary_path)
        checksum = self._calculate_checksum(primary_path)
        
        # Create metadata
        metadata = AssetMetadata(
            asset_id=asset_id,
            asset_type='mesh',
            source_type=source_type,
            source_data=source_data,
            file_path=primary_path,
            file_size=file_size,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            tags=tags or [],
            properties=properties or {},
            checksum=checksum
        )
        
        # Store metadata in database
        self._store_metadata(metadata)
        
        # Cache in memory
        with self.cache_lock:
            self.memory_cache[asset_id] = mesh
            self._enforce_cache_limit()
        
        return asset_id
    
    def load_mesh(self, asset_id: str) -> Optional[trimesh.Trimesh]:
        """Load mesh from asset ID"""
        
        # Check memory cache first
        with self.cache_lock:
            if asset_id in self.memory_cache:
                self._update_access_time(asset_id)
                return self.memory_cache[asset_id]
        
        # Load from disk
        metadata = self._get_metadata(asset_id)
        if not metadata:
            return None
        
        # Try binary format first (fastest)
        binary_path = self.cache_directory / f"{asset_id}.mesh"
        if binary_path.exists():
            try:
                mesh = self._load_mesh_binary(binary_path)
                
                # Cache in memory
                with self.cache_lock:
                    self.memory_cache[asset_id] = mesh
                    self._enforce_cache_limit()
                
                self._update_access_time(asset_id)
                return mesh
            except:
                pass
        
        # Fallback to standard format
        if os.path.exists(metadata.file_path):
            try:
                mesh = trimesh.load(metadata.file_path)
                
                # Cache in memory and binary format
                with self.cache_lock:
                    self.memory_cache[asset_id] = mesh
                    self._enforce_cache_limit()
                
                self._save_mesh_binary(mesh, binary_path)
                self._update_access_time(asset_id)
                return mesh
            except:
                pass
        
        return None
    
    def _save_mesh_binary(self, mesh: trimesh.Trimesh, file_path: Path):
        """Save mesh in compressed binary format"""
        try:
            data = {
                'vertices': mesh.vertices,
                'faces': mesh.faces,
                'vertex_normals': mesh.vertex_normals if hasattr(mesh, 'vertex_normals') else None,
                'visual': None
            }
            
            # Handle visual data
            if hasattr(mesh, 'visual') and mesh.visual is not None:
                if hasattr(mesh.visual, 'vertex_colors'):
                    data['visual'] = {
                        'vertex_colors': mesh.visual.vertex_colors
                    }
            
            # Compress and save
            with gzip.open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(f"Warning: Could not save binary mesh: {e}")
    
    def _load_mesh_binary(self, file_path: Path) -> trimesh.Trimesh:
        """Load mesh from compressed binary format"""
        with gzip.open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        mesh = trimesh.Trimesh(
            vertices=data['vertices'],
            faces=data['faces']
        )
        
        # Restore visual data
        if data['visual'] and 'vertex_colors' in data['visual']:
            mesh.visual.vertex_colors = data['visual']['vertex_colors']
        
        return mesh
    
    def asset_exists(self, asset_id: str) -> bool:
        """Check if asset exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM assets WHERE asset_id = ?",
                (asset_id,)
            )
            return cursor.fetchone() is not None
    
    def search_assets(self, asset_type: str = None, source_type: str = None, 
                     tags: List[str] = None, limit: int = 100) -> List[AssetMetadata]:
        """Search assets by criteria"""
        
        query = "SELECT * FROM assets WHERE 1=1"
        params = []
        
        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type)
        
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += " ORDER BY last_accessed DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            results = []
            
            for row in cursor.fetchall():
                metadata = AssetMetadata(
                    asset_id=row[0],
                    asset_type=row[1],
                    source_type=row[2],
                    source_data=row[3],
                    file_path=row[4],
                    file_size=row[5],
                    created_at=row[6],
                    last_accessed=row[7],
                    access_count=row[8],
                    tags=json.loads(row[9]) if row[9] else [],
                    properties=json.loads(row[10]) if row[10] else {},
                    checksum=row[11]
                )
                results.append(metadata)
            
            return results
    
    def get_similar_assets(self, source_data: str, source_type: str, 
                          similarity_threshold: float = 0.8) -> List[AssetMetadata]:
        """Find similar assets based on source data"""
        
        # Simple similarity based on string matching
        # Could be enhanced with semantic similarity for text descriptions
        
        assets = self.search_assets(source_type=source_type)
        similar = []
        
        for asset in assets:
            similarity = self._calculate_text_similarity(source_data, asset.source_data)
            if similarity >= similarity_threshold:
                similar.append(asset)
        
        return sorted(similar, key=lambda x: x.last_accessed, reverse=True)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def delete_asset(self, asset_id: str) -> bool:
        """Delete asset and its files"""
        metadata = self._get_metadata(asset_id)
        if not metadata:
            return False
        
        # Remove files
        try:
            # Remove main file
            if os.path.exists(metadata.file_path):
                os.remove(metadata.file_path)
            
            # Remove other formats
            base_path = Path(metadata.file_path).with_suffix('')
            for fmt in ['obj', 'ply', 'stl']:
                file_path = f"{base_path}.{fmt}"
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove binary cache
            binary_path = self.cache_directory / f"{asset_id}.mesh"
            if binary_path.exists():
                binary_path.unlink()
            
            # Remove from memory cache
            with self.cache_lock:
                self.memory_cache.pop(asset_id, None)
            
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM assets WHERE asset_id = ?", (asset_id,))
            
            return True
        
        except Exception as e:
            print(f"Error deleting asset {asset_id}: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.cache_lock:
            memory_size = sum(
                self._estimate_mesh_size(mesh) 
                for mesh in self.memory_cache.values()
            )
        
        # Disk usage
        disk_size = sum(
            f.stat().st_size 
            for f in self.asset_directory.rglob('*') 
            if f.is_file()
        )
        
        # Database stats
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*), asset_type FROM assets GROUP BY asset_type")
            type_counts = dict(cursor.fetchall())
            
            cursor = conn.execute("SELECT COUNT(*) FROM assets")
            total_assets = cursor.fetchone()[0]
        
        return {
            'memory_cache_size': memory_size,
            'memory_cache_items': len(self.memory_cache),
            'disk_size': disk_size,
            'total_assets': total_assets,
            'assets_by_type': type_counts,
            'cache_hit_ratio': self._calculate_cache_hit_ratio()
        }
    
    def _estimate_mesh_size(self, mesh: trimesh.Trimesh) -> int:
        """Estimate memory size of mesh"""
        size = mesh.vertices.nbytes + mesh.faces.nbytes
        
        if hasattr(mesh, 'vertex_normals'):
            size += mesh.vertex_normals.nbytes
        
        if hasattr(mesh, 'visual') and mesh.visual is not None:
            if hasattr(mesh.visual, 'vertex_colors'):
                size += mesh.visual.vertex_colors.nbytes
        
        return size
    
    def _enforce_cache_limit(self):
        """Enforce memory cache size limit"""
        current_size = sum(
            self._estimate_mesh_size(mesh) 
            for mesh in self.memory_cache.values()
        )
        
        if current_size <= self.max_cache_size:
            return
        
        # Remove least recently accessed items
        # This is simplified - could use proper LRU implementation
        assets_by_access = self.search_assets(limit=1000)
        
        for asset in reversed(assets_by_access):  # Oldest first
            if asset.asset_id in self.memory_cache:
                del self.memory_cache[asset.asset_id]
                current_size -= self._estimate_mesh_size(
                    self.memory_cache.get(asset.asset_id, trimesh.Trimesh())
                )
                
                if current_size <= self.max_cache_size * 0.8:  # Leave some headroom
                    break
    
    def _generate_asset_id(self, source_type: str, source_data: str) -> str:
        """Generate unique asset ID"""
        content = f"{source_type}:{source_data}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _store_metadata(self, metadata: AssetMetadata):
        """Store asset metadata in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO assets 
                (asset_id, asset_type, source_type, source_data, file_path, 
                 file_size, created_at, last_accessed, access_count, tags, properties, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.asset_id,
                metadata.asset_type,
                metadata.source_type,
                metadata.source_data,
                metadata.file_path,
                metadata.file_size,
                metadata.created_at,
                metadata.last_accessed,
                metadata.access_count,
                json.dumps(metadata.tags),
                json.dumps(metadata.properties),
                metadata.checksum
            ))
    
    def _get_metadata(self, asset_id: str) -> Optional[AssetMetadata]:
        """Get asset metadata from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM assets WHERE asset_id = ?",
                (asset_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return AssetMetadata(
                asset_id=row[0],
                asset_type=row[1],
                source_type=row[2],
                source_data=row[3],
                file_path=row[4],
                file_size=row[5],
                created_at=row[6],
                last_accessed=row[7],
                access_count=row[8],
                tags=json.loads(row[9]) if row[9] else [],
                properties=json.loads(row[10]) if row[10] else {},
                checksum=row[11]
            )
    
    def _update_access_time(self, asset_id: str):
        """Update last access time and increment access count"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE assets 
                SET last_accessed = ?, access_count = access_count + 1
                WHERE asset_id = ?
            ''', (time.time(), asset_id))
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio (simplified)"""
        # This would need proper tracking in a real implementation
        return 0.75  # Placeholder
    
    def _cleanup_loop(self):
        """Background cleanup of old assets"""
        while self.cleanup_running:
            try:
                # Clean up old unused assets (older than 30 days, accessed < 5 times)
                cutoff_time = time.time() - (30 * 24 * 3600)  # 30 days ago
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT asset_id FROM assets 
                        WHERE last_accessed < ? AND access_count < 5
                    ''', (cutoff_time,))
                    
                    old_assets = [row[0] for row in cursor.fetchall()]
                
                # Delete old assets
                for asset_id in old_assets[:10]:  # Limit to 10 per cleanup cycle
                    self.delete_asset(asset_id)
                
                # Clean up orphaned files
                self._cleanup_orphaned_files()
                
            except Exception as e:
                print(f"Cleanup error: {e}")
            
            # Sleep for 1 hour
            time.sleep(3600)
    
    def _cleanup_orphaned_files(self):
        """Remove files that don't have database entries"""
        try:
            # Get all asset IDs from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT asset_id FROM assets")
                valid_ids = {row[0] for row in cursor.fetchall()}
            
            # Check files in asset directory
            for file_path in self.asset_directory.glob("*"):
                if file_path.is_file():
                    # Extract asset ID from filename
                    asset_id = file_path.stem.split('.')[0]
                    if asset_id not in valid_ids and len(asset_id) == 16:  # Our asset ID length
                        try:
                            file_path.unlink()
                        except:
                            pass
        
        except Exception as e:
            print(f"Orphaned file cleanup error: {e}")
    
    def shutdown(self):
        """Shutdown asset manager"""
        self.cleanup_running = False
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)