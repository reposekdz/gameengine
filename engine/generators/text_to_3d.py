import numpy as np
import trimesh
import noise
from perlin_noise import PerlinNoise
from typing import Dict, List, Tuple, Optional
from ..core.nlp_processor import NLPProcessor, ObjectDescription, ShapeType
import math
import random

class TextTo3DGenerator:
    def __init__(self):
        self.nlp = NLPProcessor()
        self.noise_gen = PerlinNoise(octaves=4, seed=42)
        
        self.generators = {
            ShapeType.CUBE: self._generate_cube,
            ShapeType.SPHERE: self._generate_sphere,
            ShapeType.CYLINDER: self._generate_cylinder,
            ShapeType.CONE: self._generate_cone,
            ShapeType.TORUS: self._generate_torus,
            ShapeType.PYRAMID: self._generate_pyramid,
            ShapeType.PLANE: self._generate_plane,
            ShapeType.COMPLEX: self._generate_complex
        }
    
    def generate_from_text(self, description: str) -> trimesh.Trimesh:
        """Generate advanced 3D model from text description"""
        obj_desc = self.nlp.parse_description(description)
        
        # Generate base mesh
        mesh = self.generators[obj_desc.shape](obj_desc)
        
        # Apply transformations
        mesh = self._apply_transformations(mesh, obj_desc)
        
        # Apply materials and textures
        mesh = self._apply_materials(mesh, obj_desc)
        
        # Add procedural details
        if obj_desc.texture:
            mesh = self._apply_procedural_texture(mesh, obj_desc.texture)
        
        return mesh
    
    def _generate_cube(self, desc: ObjectDescription) -> trimesh.Trimesh:
        extents = [desc.scale[0], desc.scale[1], desc.scale[2]]
        mesh = trimesh.creation.box(extents=extents)
        
        # Add beveled edges for realism
        if desc.material == 'metallic':
            mesh = mesh.smoothed()
        
        return mesh
    
    def _generate_sphere(self, desc: ObjectDescription) -> trimesh.Trimesh:
        radius = desc.size
        subdivisions = 3 if desc.material == 'smooth' else 2
        mesh = trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)
        
        # Add surface noise for organic feel
        if 'organic' in desc.properties:
            vertices = mesh.vertices.copy()
            for i, vertex in enumerate(vertices):
                noise_val = self.noise_gen(vertex[0]*2, vertex[1]*2, vertex[2]*2)
                vertices[i] += vertex * noise_val * 0.1
            mesh.vertices = vertices
        
        return mesh
    
    def _generate_cylinder(self, desc: ObjectDescription) -> trimesh.Trimesh:
        radius = desc.scale[0]
        height = desc.scale[1] * 2
        sections = 32 if desc.material == 'smooth' else 16
        
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        
        # Add caps based on description
        if 'open' not in desc.properties:
            mesh = mesh + trimesh.creation.cylinder(radius=radius*0.95, height=height*1.1, sections=sections)
        
        return mesh
    
    def _generate_cone(self, desc: ObjectDescription) -> trimesh.Trimesh:
        radius = desc.scale[0]
        height = desc.scale[1] * 2
        sections = 32 if desc.material == 'smooth' else 16
        
        mesh = trimesh.creation.cone(radius=radius, height=height, sections=sections)
        return mesh
    
    def _generate_torus(self, desc: ObjectDescription) -> trimesh.Trimesh:
        major_radius = desc.scale[0]
        minor_radius = desc.scale[0] * 0.3
        major_sections = 32
        minor_sections = 16
        
        mesh = trimesh.creation.torus(major_radius=major_radius, minor_radius=minor_radius,
                                    major_sections=major_sections, minor_sections=minor_sections)
        return mesh
    
    def _generate_pyramid(self, desc: ObjectDescription) -> trimesh.Trimesh:
        base_size = desc.scale[0]
        height = desc.scale[1] * 2
        
        # Create pyramid vertices
        vertices = np.array([
            [-base_size/2, 0, -base_size/2],  # Base corners
            [base_size/2, 0, -base_size/2],
            [base_size/2, 0, base_size/2],
            [-base_size/2, 0, base_size/2],
            [0, height, 0]  # Apex
        ])
        
        faces = np.array([
            [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],  # Triangular faces
            [0, 3, 2], [0, 2, 1]  # Base
        ])
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)
    
    def _generate_plane(self, desc: ObjectDescription) -> trimesh.Trimesh:
        size_x, size_z = desc.scale[0], desc.scale[2]
        resolution = 50 if 'detailed' in desc.properties else 10
        
        # Generate terrain-like plane
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = (i / resolution - 0.5) * size_x
                z = (j / resolution - 0.5) * size_z
                y = 0
                
                # Add height variation
                if 'terrain' in desc.properties:
                    y = self.noise_gen(x * 0.1, z * 0.1) * desc.scale[1]
                
                vertices.append([x, y, z])
        
        # Generate faces
        for i in range(resolution):
            for j in range(resolution):
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j
                v4 = v3 + 1
                
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    
    def _generate_complex(self, desc: ObjectDescription) -> trimesh.Trimesh:
        """Generate complex structures like buildings"""
        if 'building' in desc.properties or 'house' in desc.properties:
            return self._generate_building(desc)
        elif 'tower' in desc.properties:
            return self._generate_tower(desc)
        else:
            return self._generate_abstract_complex(desc)
    
    def _generate_building(self, desc: ObjectDescription) -> trimesh.Trimesh:
        base_width = desc.scale[0]
        base_depth = desc.scale[2]
        height = desc.scale[1] * 3
        
        # Main structure
        main_building = trimesh.creation.box(extents=[base_width, height, base_depth])
        
        # Add roof
        roof_vertices = np.array([
            [-base_width/2, height/2, -base_depth/2],
            [base_width/2, height/2, -base_depth/2],
            [base_width/2, height/2, base_depth/2],
            [-base_width/2, height/2, base_depth/2],
            [0, height/2 + base_width/4, 0]
        ])
        
        roof_faces = np.array([
            [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]
        ])
        
        roof = trimesh.Trimesh(vertices=roof_vertices, faces=roof_faces)
        
        return main_building + roof
    
    def _generate_tower(self, desc: ObjectDescription) -> trimesh.Trimesh:
        base_radius = desc.scale[0]
        height = desc.scale[1] * 5
        
        # Create tapered tower
        sections = []
        num_sections = 5
        
        for i in range(num_sections):
            section_height = height / num_sections
            section_radius = base_radius * (1 - i * 0.1)
            section_y = i * section_height - height/2 + section_height/2
            
            section = trimesh.creation.cylinder(radius=section_radius, height=section_height)
            section.apply_translation([0, section_y, 0])
            sections.append(section)
        
        return trimesh.util.concatenate(sections)
    
    def _generate_abstract_complex(self, desc: ObjectDescription) -> trimesh.Trimesh:
        """Generate abstract complex shapes"""
        components = []
        num_components = random.randint(3, 7)
        
        for i in range(num_components):
            # Random component
            comp_type = random.choice([ShapeType.CUBE, ShapeType.SPHERE, ShapeType.CYLINDER])
            comp_desc = ObjectDescription(
                shape=comp_type,
                size=desc.size * random.uniform(0.3, 0.8),
                color=desc.color,
                material=desc.material,
                texture=desc.texture,
                position=(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)),
                rotation=(0, 0, 0),
                scale=(random.uniform(0.5, 1.5), random.uniform(0.5, 1.5), random.uniform(0.5, 1.5)),
                properties=desc.properties
            )
            
            component = self.generators[comp_type](comp_desc)
            component.apply_translation(comp_desc.position)
            components.append(component)
        
        return trimesh.util.concatenate(components)
    
    def _apply_transformations(self, mesh: trimesh.Trimesh, desc: ObjectDescription) -> trimesh.Trimesh:
        """Apply position, rotation, and scale transformations"""
        # Apply rotation
        if any(desc.rotation):
            rx, ry, rz = np.radians(desc.rotation)
            if rx: mesh.apply_transform(trimesh.transformations.rotation_matrix(rx, [1, 0, 0]))
            if ry: mesh.apply_transform(trimesh.transformations.rotation_matrix(ry, [0, 1, 0]))
            if rz: mesh.apply_transform(trimesh.transformations.rotation_matrix(rz, [0, 0, 1]))
        
        # Apply position
        if any(desc.position):
            mesh.apply_translation(desc.position)
        
        return mesh
    
    def _apply_materials(self, mesh: trimesh.Trimesh, desc: ObjectDescription) -> trimesh.Trimesh:
        """Apply material properties to mesh"""
        # Set vertex colors based on material and color
        if hasattr(mesh.visual, 'vertex_colors'):
            color_rgba = (*desc.color, 1.0)
            mesh.visual.vertex_colors = np.tile(color_rgba, (len(mesh.vertices), 1))
        
        return mesh
    
    def _apply_procedural_texture(self, mesh: trimesh.Trimesh, texture_type: str) -> trimesh.Trimesh:
        """Apply procedural textures to mesh surface"""
        if texture_type == 'rough':
            # Add surface roughness
            vertices = mesh.vertices.copy()
            for i, vertex in enumerate(vertices):
                noise_val = self.noise_gen(vertex[0]*10, vertex[1]*10, vertex[2]*10)
                normal = mesh.vertex_normals[i]
                vertices[i] += normal * noise_val * 0.02
            mesh.vertices = vertices
        
        elif texture_type == 'bumpy':
            # Add bumps
            vertices = mesh.vertices.copy()
            for i, vertex in enumerate(vertices):
                noise_val = abs(self.noise_gen(vertex[0]*5, vertex[1]*5, vertex[2]*5))
                normal = mesh.vertex_normals[i]
                vertices[i] += normal * noise_val * 0.05
            mesh.vertices = vertices
        
        return mesh