import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional, Any
import json
from dataclasses import dataclass, asdict
from enum import Enum

class GameObjectType(Enum):
    STATIC_MESH = "static_mesh"
    DYNAMIC_OBJECT = "dynamic_object"
    CHARACTER = "character"
    VEHICLE = "vehicle"
    PROP = "prop"
    COLLECTIBLE = "collectible"
    OBSTACLE = "obstacle"
    PLATFORM = "platform"

@dataclass
class GameObjectProperties:
    object_type: GameObjectType
    collision_type: str  # 'box', 'sphere', 'mesh', 'convex'
    physics_enabled: bool
    mass: float
    friction: float
    restitution: float
    is_trigger: bool
    health: Optional[float]
    damage: Optional[float]
    interactable: bool
    ai_enabled: bool
    animation_data: Optional[Dict]
    script_hooks: List[str]
    tags: List[str]
    metadata: Dict[str, Any]

class ModelToGameConverter:
    """Convert 3D models to game-ready assets with full functionality"""
    
    def __init__(self):
        self.lod_levels = [1.0, 0.5, 0.25, 0.1]  # LOD detail levels
        self.collision_simplification = 0.1
        
    def convert_to_game_asset(self, mesh: trimesh.Trimesh, 
                             object_type: GameObjectType = GameObjectType.PROP,
                             properties: Dict = None) -> Dict[str, Any]:
        """Convert mesh to complete game asset"""
        
        # Generate LODs
        lods = self._generate_lods(mesh)
        
        # Generate collision meshes
        collision_meshes = self._generate_collision_meshes(mesh, object_type)
        
        # Generate navmesh if needed
        navmesh = self._generate_navmesh(mesh) if object_type in [GameObjectType.PLATFORM, GameObjectType.STATIC_MESH] else None
        
        # Optimize for game engine
        optimized_mesh = self._optimize_for_game(mesh)
        
        # Generate UV maps if missing
        if not hasattr(optimized_mesh.visual, 'uv') or optimized_mesh.visual.uv is None:
            optimized_mesh = self._generate_uv_map(optimized_mesh)
        
        # Calculate bounds and center
        bounds = self._calculate_bounds(optimized_mesh)
        
        # Generate game properties
        game_props = self._generate_game_properties(optimized_mesh, object_type, properties)
        
        # Create material data
        materials = self._extract_materials(optimized_mesh)
        
        # Generate metadata
        metadata = self._generate_metadata(optimized_mesh, object_type)
        
        return {
            'main_mesh': optimized_mesh,
            'lods': lods,
            'collision_meshes': collision_meshes,
            'navmesh': navmesh,
            'bounds': bounds,
            'properties': game_props,
            'materials': materials,
            'metadata': metadata
        }
    
    def _generate_lods(self, mesh: trimesh.Trimesh) -> List[trimesh.Trimesh]:
        """Generate Level of Detail meshes"""
        lods = []
        
        for level in self.lod_levels:
            if level == 1.0:
                lods.append(mesh.copy())
            else:
                target_faces = int(len(mesh.faces) * level)
                target_faces = max(target_faces, 4)  # Minimum faces
                
                try:
                    lod_mesh = mesh.simplify_quadric_decimation(target_faces)
                    lods.append(lod_mesh)
                except:
                    lods.append(mesh.copy())
        
        return lods
    
    def _generate_collision_meshes(self, mesh: trimesh.Trimesh, 
                                   object_type: GameObjectType) -> Dict[str, trimesh.Trimesh]:
        """Generate collision meshes for different collision types"""
        collision_meshes = {}
        
        # Box collision
        collision_meshes['box'] = self._create_box_collision(mesh)
        
        # Sphere collision
        collision_meshes['sphere'] = self._create_sphere_collision(mesh)
        
        # Convex hull collision
        try:
            collision_meshes['convex'] = mesh.convex_hull
        except:
            collision_meshes['convex'] = collision_meshes['box']
        
        # Simplified mesh collision
        target_faces = max(int(len(mesh.faces) * self.collision_simplification), 8)
        try:
            collision_meshes['mesh'] = mesh.simplify_quadric_decimation(target_faces)
        except:
            collision_meshes['mesh'] = collision_meshes['convex']
        
        # Capsule collision for characters
        if object_type == GameObjectType.CHARACTER:
            collision_meshes['capsule'] = self._create_capsule_collision(mesh)
        
        return collision_meshes
    
    def _create_box_collision(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Create oriented bounding box collision"""
        bounds = mesh.bounds
        extents = bounds[1] - bounds[0]
        center = (bounds[1] + bounds[0]) / 2
        
        box = trimesh.creation.box(extents=extents)
        box.apply_translation(center)
        
        return box
    
    def _create_sphere_collision(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Create bounding sphere collision"""
        center = mesh.centroid
        radius = np.max(np.linalg.norm(mesh.vertices - center, axis=1))
        
        sphere = trimesh.creation.icosphere(radius=radius, subdivisions=2)
        sphere.apply_translation(center)
        
        return sphere
    
    def _create_capsule_collision(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Create capsule collision for characters"""
        bounds = mesh.bounds
        height = bounds[1][1] - bounds[0][1]
        radius = max(bounds[1][0] - bounds[0][0], bounds[1][2] - bounds[0][2]) / 2
        
        # Create capsule as cylinder + 2 hemispheres
        cylinder = trimesh.creation.cylinder(radius=radius, height=height * 0.6)
        
        top_sphere = trimesh.creation.icosphere(radius=radius, subdivisions=2)
        top_sphere.apply_translation([0, height * 0.3, 0])
        
        bottom_sphere = trimesh.creation.icosphere(radius=radius, subdivisions=2)
        bottom_sphere.apply_translation([0, -height * 0.3, 0])
        
        capsule = trimesh.util.concatenate([cylinder, top_sphere, bottom_sphere])
        capsule.apply_translation(mesh.centroid)
        
        return capsule
    
    def _generate_navmesh(self, mesh: trimesh.Trimesh) -> Optional[trimesh.Trimesh]:
        """Generate navigation mesh for AI pathfinding"""
        try:
            # Project to XZ plane and simplify
            vertices = mesh.vertices.copy()
            vertices[:, 1] = np.mean(vertices[:, 1])  # Flatten Y
            
            # Create simplified top surface
            navmesh = trimesh.Trimesh(vertices=vertices, faces=mesh.faces)
            
            # Simplify heavily for pathfinding
            target_faces = max(len(mesh.faces) // 10, 10)
            navmesh = navmesh.simplify_quadric_decimation(target_faces)
            
            return navmesh
        except:
            return None
    
    def _optimize_for_game(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Optimize mesh for game engine performance"""
        optimized = mesh.copy()
        
        # Merge duplicate vertices
        optimized.merge_vertices()
        
        # Remove degenerate faces
        optimized.remove_degenerate_faces()
        
        # Remove duplicate faces
        optimized.remove_duplicate_faces()
        
        # Fix normals
        optimized.fix_normals()
        
        # Ensure manifold if possible
        if not optimized.is_watertight:
            try:
                optimized.fill_holes()
            except:
                pass
        
        return optimized
    
    def _generate_uv_map(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Generate UV texture coordinates"""
        vertices = mesh.vertices
        
        # Smart UV projection based on mesh shape
        bounds = mesh.bounds
        extents = bounds[1] - bounds[0]
        
        # Determine dominant axis
        dominant_axis = np.argmax(extents)
        
        if dominant_axis == 1:  # Vertical object
            # Cylindrical projection
            uv = self._cylindrical_projection(vertices)
        elif extents[1] < extents[0] * 0.3:  # Flat object
            # Planar projection
            uv = self._planar_projection(vertices)
        else:
            # Spherical projection
            uv = self._spherical_projection(vertices)
        
        mesh.visual.uv = uv
        return mesh
    
    def _cylindrical_projection(self, vertices: np.ndarray) -> np.ndarray:
        """Cylindrical UV projection"""
        centered = vertices - np.mean(vertices, axis=0)
        
        u = 0.5 + np.arctan2(centered[:, 2], centered[:, 0]) / (2 * np.pi)
        v = (centered[:, 1] - centered[:, 1].min()) / (centered[:, 1].max() - centered[:, 1].min() + 1e-8)
        
        return np.column_stack([u, v])
    
    def _planar_projection(self, vertices: np.ndarray) -> np.ndarray:
        """Planar UV projection"""
        centered = vertices - np.mean(vertices, axis=0)
        
        u = (centered[:, 0] - centered[:, 0].min()) / (centered[:, 0].max() - centered[:, 0].min() + 1e-8)
        v = (centered[:, 2] - centered[:, 2].min()) / (centered[:, 2].max() - centered[:, 2].min() + 1e-8)
        
        return np.column_stack([u, v])
    
    def _spherical_projection(self, vertices: np.ndarray) -> np.ndarray:
        """Spherical UV projection"""
        centered = vertices - np.mean(vertices, axis=0)
        normalized = centered / (np.linalg.norm(centered, axis=1, keepdims=True) + 1e-8)
        
        u = 0.5 + np.arctan2(normalized[:, 2], normalized[:, 0]) / (2 * np.pi)
        v = 0.5 - np.arcsin(np.clip(normalized[:, 1], -1, 1)) / np.pi
        
        return np.column_stack([u, v])
    
    def _calculate_bounds(self, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """Calculate bounding information"""
        bounds = mesh.bounds
        center = mesh.centroid
        extents = bounds[1] - bounds[0]
        
        return {
            'min': bounds[0].tolist(),
            'max': bounds[1].tolist(),
            'center': center.tolist(),
            'extents': extents.tolist(),
            'radius': float(np.max(np.linalg.norm(mesh.vertices - center, axis=1)))
        }
    
    def _generate_game_properties(self, mesh: trimesh.Trimesh, 
                                  object_type: GameObjectType,
                                  custom_props: Dict = None) -> GameObjectProperties:
        """Generate game object properties"""
        
        # Default properties based on type
        defaults = {
            GameObjectType.STATIC_MESH: {
                'collision_type': 'mesh',
                'physics_enabled': False,
                'mass': 0,
                'is_trigger': False,
                'interactable': False,
                'ai_enabled': False
            },
            GameObjectType.DYNAMIC_OBJECT: {
                'collision_type': 'convex',
                'physics_enabled': True,
                'mass': 1.0,
                'is_trigger': False,
                'interactable': True,
                'ai_enabled': False
            },
            GameObjectType.CHARACTER: {
                'collision_type': 'capsule',
                'physics_enabled': True,
                'mass': 70.0,
                'is_trigger': False,
                'interactable': True,
                'ai_enabled': True,
                'health': 100.0
            },
            GameObjectType.COLLECTIBLE: {
                'collision_type': 'sphere',
                'physics_enabled': False,
                'mass': 0.1,
                'is_trigger': True,
                'interactable': True,
                'ai_enabled': False
            },
            GameObjectType.VEHICLE: {
                'collision_type': 'convex',
                'physics_enabled': True,
                'mass': 1000.0,
                'is_trigger': False,
                'interactable': True,
                'ai_enabled': True
            }
        }
        
        props = defaults.get(object_type, defaults[GameObjectType.PROP])
        
        # Merge custom properties
        if custom_props:
            props.update(custom_props)
        
        return GameObjectProperties(
            object_type=object_type,
            collision_type=props.get('collision_type', 'box'),
            physics_enabled=props.get('physics_enabled', True),
            mass=props.get('mass', 1.0),
            friction=props.get('friction', 0.5),
            restitution=props.get('restitution', 0.3),
            is_trigger=props.get('is_trigger', False),
            health=props.get('health'),
            damage=props.get('damage'),
            interactable=props.get('interactable', False),
            ai_enabled=props.get('ai_enabled', False),
            animation_data=props.get('animation_data'),
            script_hooks=props.get('script_hooks', []),
            tags=props.get('tags', []),
            metadata=props.get('metadata', {})
        )
    
    def _extract_materials(self, mesh: trimesh.Trimesh) -> List[Dict[str, Any]]:
        """Extract material information"""
        materials = []
        
        if hasattr(mesh.visual, 'material'):
            mat = mesh.visual.material
            materials.append({
                'name': getattr(mat, 'name', 'default'),
                'diffuse': getattr(mat, 'diffuse', [1.0, 1.0, 1.0, 1.0]),
                'ambient': getattr(mat, 'ambient', [0.2, 0.2, 0.2, 1.0]),
                'specular': getattr(mat, 'specular', [0.5, 0.5, 0.5, 1.0]),
                'shininess': getattr(mat, 'shininess', 32.0)
            })
        elif hasattr(mesh.visual, 'vertex_colors'):
            # Extract dominant colors
            colors = mesh.visual.vertex_colors[:, :3].astype(float) / 255.0
            avg_color = np.mean(colors, axis=0)
            
            materials.append({
                'name': 'vertex_color',
                'diffuse': avg_color.tolist() + [1.0],
                'ambient': (avg_color * 0.2).tolist() + [1.0],
                'specular': [0.5, 0.5, 0.5, 1.0],
                'shininess': 32.0
            })
        else:
            materials.append({
                'name': 'default',
                'diffuse': [0.8, 0.8, 0.8, 1.0],
                'ambient': [0.2, 0.2, 0.2, 1.0],
                'specular': [0.5, 0.5, 0.5, 1.0],
                'shininess': 32.0
            })
        
        return materials
    
    def _generate_metadata(self, mesh: trimesh.Trimesh, object_type: GameObjectType) -> Dict[str, Any]:
        """Generate asset metadata"""
        return {
            'vertex_count': len(mesh.vertices),
            'face_count': len(mesh.faces),
            'is_watertight': mesh.is_watertight,
            'is_convex': mesh.is_convex,
            'volume': float(mesh.volume) if mesh.is_watertight else 0,
            'surface_area': float(mesh.area),
            'object_type': object_type.value,
            'has_uv': hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None,
            'has_normals': hasattr(mesh, 'vertex_normals'),
            'has_colors': hasattr(mesh.visual, 'vertex_colors')
        }
    
    def export_game_asset(self, game_asset: Dict[str, Any], output_dir: str, asset_name: str):
        """Export game asset to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Export main mesh
        game_asset['main_mesh'].export(f"{output_dir}/{asset_name}.obj")
        game_asset['main_mesh'].export(f"{output_dir}/{asset_name}.glb")
        
        # Export LODs
        for i, lod in enumerate(game_asset['lods']):
            lod.export(f"{output_dir}/{asset_name}_LOD{i}.obj")
        
        # Export collision meshes
        for coll_type, coll_mesh in game_asset['collision_meshes'].items():
            coll_mesh.export(f"{output_dir}/{asset_name}_collision_{coll_type}.obj")
        
        # Export navmesh if exists
        if game_asset['navmesh']:
            game_asset['navmesh'].export(f"{output_dir}/{asset_name}_navmesh.obj")
        
        # Export metadata as JSON
        metadata = {
            'bounds': game_asset['bounds'],
            'properties': asdict(game_asset['properties']),
            'materials': game_asset['materials'],
            'metadata': game_asset['metadata']
        }
        
        with open(f"{output_dir}/{asset_name}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2, default=str)