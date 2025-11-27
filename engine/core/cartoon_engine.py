import numpy as np
import trimesh
from typing import List, Dict, Tuple
import cv2

class CartoonEngine:
    """Production cartoon rendering engine with NPR techniques"""
    
    @staticmethod
    def cartoonify_mesh(mesh: trimesh.Trimesh, style: str = 'toon', outline_thickness: float = 0.05) -> trimesh.Trimesh:
        """Convert mesh to cartoon style"""
        
        if style == 'toon':
            return CartoonEngine._apply_toon_shading(mesh, outline_thickness)
        elif style == 'cel_shaded':
            return CartoonEngine._apply_cel_shading(mesh, outline_thickness)
        elif style == 'anime':
            return CartoonEngine._apply_anime_style(mesh, outline_thickness)
        elif style == 'comic':
            return CartoonEngine._apply_comic_style(mesh, outline_thickness)
        else:
            return CartoonEngine._apply_toon_shading(mesh, outline_thickness)
    
    @staticmethod
    def _apply_toon_shading(mesh: trimesh.Trimesh, outline_thickness: float) -> trimesh.Trimesh:
        """Apply toon shading with quantized colors"""
        result_mesh = mesh.copy()
        
        # Quantize colors to 4 levels
        if hasattr(result_mesh.visual, 'vertex_colors'):
            colors = np.array(result_mesh.visual.vertex_colors)
            for i in range(3):
                colors[:, i] = np.digitize(colors[:, i], bins=[64, 128, 192]) * 64
            result_mesh.visual.vertex_colors = colors
        
        # Add outline
        outline = CartoonEngine._generate_outline(mesh, outline_thickness)
        return trimesh.util.concatenate([result_mesh, outline])
    
    @staticmethod
    def _apply_cel_shading(mesh: trimesh.Trimesh, outline_thickness: float) -> trimesh.Trimesh:
        """Apply cel shading with hard shadows"""
        result_mesh = mesh.copy()
        
        # Quantize to 3 levels (highlight, midtone, shadow)
        if hasattr(result_mesh.visual, 'vertex_colors'):
            colors = np.array(result_mesh.visual.vertex_colors)
            for i in range(3):
                colors[:, i] = np.digitize(colors[:, i], bins=[85, 170]) * 85
            result_mesh.visual.vertex_colors = colors
        
        outline = CartoonEngine._generate_outline(mesh, outline_thickness)
        return trimesh.util.concatenate([result_mesh, outline])
    
    @staticmethod
    def _apply_anime_style(mesh: trimesh.Trimesh, outline_thickness: float) -> trimesh.Trimesh:
        """Apply anime style with soft gradients"""
        result_mesh = mesh.copy()
        
        # Smooth color transitions
        if hasattr(result_mesh.visual, 'vertex_colors'):
            colors = np.array(result_mesh.visual.vertex_colors, dtype=float)
            
            # Increase saturation
            for i in range(len(colors)):
                hsv = cv2.cvtColor(np.uint8([[colors[i, :3]]]), cv2.COLOR_RGB2HSV)[0][0]
                hsv[1] = min(255, hsv[1] * 1.5)  # Boost saturation
                rgb = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2RGB)[0][0]
                colors[i, :3] = rgb
            
            result_mesh.visual.vertex_colors = colors.astype(np.uint8)
        
        outline = CartoonEngine._generate_outline(mesh, outline_thickness * 0.7)
        return trimesh.util.concatenate([result_mesh, outline])
    
    @staticmethod
    def _apply_comic_style(mesh: trimesh.Trimesh, outline_thickness: float) -> trimesh.Trimesh:
        """Apply comic book style with bold colors"""
        result_mesh = mesh.copy()
        
        # High contrast colors
        if hasattr(result_mesh.visual, 'vertex_colors'):
            colors = np.array(result_mesh.visual.vertex_colors, dtype=float)
            
            # Increase contrast
            for i in range(3):
                colors[:, i] = np.clip((colors[:, i] - 128) * 1.5 + 128, 0, 255)
            
            result_mesh.visual.vertex_colors = colors.astype(np.uint8)
        
        outline = CartoonEngine._generate_outline(mesh, outline_thickness * 1.2)
        return trimesh.util.concatenate([result_mesh, outline])
    
    @staticmethod
    def _generate_outline(mesh: trimesh.Trimesh, thickness: float) -> trimesh.Trimesh:
        """Generate outline using inverted hull method"""
        outline = mesh.copy()
        
        # Scale along normals
        if mesh.vertex_normals is not None:
            outline.vertices = mesh.vertices - mesh.vertex_normals * thickness
        
        # Invert faces for backface rendering
        outline.faces = np.fliplr(outline.faces)
        
        # Black color for outline
        outline.visual.vertex_colors = [0, 0, 0, 255]
        
        return outline
    
    @staticmethod
    def generate_cartoon_scene(objects: List[Dict], style: str = 'toon') -> trimesh.Trimesh:
        """Generate complete cartoon scene"""
        meshes = []
        
        for obj in objects:
            mesh = obj['mesh']
            position = obj.get('position', [0, 0, 0])
            rotation = obj.get('rotation', [0, 0, 0])
            scale = obj.get('scale', 1.0)
            
            # Apply transformations
            mesh = mesh.copy()
            mesh.apply_scale(scale)
            
            # Apply rotations
            for axis, angle in enumerate(rotation):
                if angle != 0:
                    axis_vec = [0, 0, 0]
                    axis_vec[axis] = 1
                    mesh.apply_transform(
                        trimesh.transformations.rotation_matrix(angle, axis_vec)
                    )
            
            mesh.apply_translation(position)
            
            # Cartoonify
            cartoon_mesh = CartoonEngine.cartoonify_mesh(mesh, style)
            meshes.append(cartoon_mesh)
        
        return trimesh.util.concatenate(meshes)
    
    @staticmethod
    def generate_cartoon_character(character_type: str = 'hero') -> trimesh.Trimesh:
        """Generate stylized cartoon character"""
        meshes = []
        
        if character_type == 'hero':
            # Large head (cartoon proportions)
            head = trimesh.creation.icosphere(subdivisions=3, radius=1.2)
            head.apply_translation([0, 2.5, 0])
            head.visual.vertex_colors = [255, 220, 177, 255]
            meshes.append(head)
            
            # Eyes
            for x in [-0.4, 0.4]:
                eye = trimesh.creation.icosphere(subdivisions=2, radius=0.25)
                eye.apply_translation([x, 2.7, 0.8])
                eye.visual.vertex_colors = [255, 255, 255, 255]
                meshes.append(eye)
                
                pupil = trimesh.creation.icosphere(subdivisions=1, radius=0.12)
                pupil.apply_translation([x, 2.7, 0.95])
                pupil.visual.vertex_colors = [0, 0, 0, 255]
                meshes.append(pupil)
            
            # Body (muscular)
            body = trimesh.creation.capsule(radius=0.6, height=1.5)
            body.apply_translation([0, 1.2, 0])
            body.visual.vertex_colors = [0, 100, 200, 255]
            meshes.append(body)
            
            # Arms
            for x in [-0.8, 0.8]:
                arm = trimesh.creation.capsule(radius=0.25, height=1.2)
                arm.apply_transform(trimesh.transformations.rotation_matrix(np.pi/6 * (-1 if x < 0 else 1), [0, 0, 1]))
                arm.apply_translation([x, 1.2, 0])
                arm.visual.vertex_colors = [255, 220, 177, 255]
                meshes.append(arm)
            
            # Legs
            for x in [-0.3, 0.3]:
                leg = trimesh.creation.capsule(radius=0.3, height=1.5)
                leg.apply_translation([x, 0.3, 0])
                leg.visual.vertex_colors = [0, 100, 200, 255]
                meshes.append(leg)
        
        elif character_type == 'villain':
            # Angular features
            head = trimesh.creation.box(extents=[1.5, 1.5, 1.5])
            head.apply_translation([0, 2.5, 0])
            head.visual.vertex_colors = [150, 150, 150, 255]
            meshes.append(head)
            
            # Red eyes
            for x in [-0.4, 0.4]:
                eye = trimesh.creation.icosphere(subdivisions=2, radius=0.2)
                eye.apply_translation([x, 2.6, 0.7])
                eye.visual.vertex_colors = [255, 0, 0, 255]
                meshes.append(eye)
            
            # Dark body
            body = trimesh.creation.box(extents=[1.2, 2, 0.8])
            body.apply_translation([0, 1, 0])
            body.visual.vertex_colors = [50, 0, 50, 255]
            meshes.append(body)
        
        character = trimesh.util.concatenate(meshes)
        return CartoonEngine.cartoonify_mesh(character, 'toon')
    
    @staticmethod
    def generate_cartoon_environment(env_type: str = 'city') -> List[trimesh.Trimesh]:
        """Generate cartoon environment"""
        meshes = []
        
        if env_type == 'city':
            # Stylized buildings
            for i in range(20):
                x = np.random.uniform(-50, 50)
                z = np.random.uniform(-50, 50)
                height = np.random.uniform(10, 40)
                width = np.random.uniform(5, 15)
                
                building = trimesh.creation.box(extents=[width, height, width])
                building.apply_translation([x, height/2, z])
                
                # Bright colors
                color = [
                    np.random.randint(100, 255),
                    np.random.randint(100, 255),
                    np.random.randint(100, 255),
                    255
                ]
                building.visual.vertex_colors = color
                
                cartoon_building = CartoonEngine.cartoonify_mesh(building, 'toon')
                meshes.append(cartoon_building)
        
        elif env_type == 'forest':
            # Stylized trees
            for i in range(50):
                x = np.random.uniform(-50, 50)
                z = np.random.uniform(-50, 50)
                
                trunk = trimesh.creation.cylinder(radius=0.5, height=8, sections=6)
                trunk.apply_translation([x, 4, z])
                trunk.visual.vertex_colors = [139, 69, 19, 255]
                
                crown = trimesh.creation.icosphere(subdivisions=2, radius=4)
                crown.apply_translation([x, 10, z])
                crown.visual.vertex_colors = [50, 205, 50, 255]
                
                tree = trimesh.util.concatenate([trunk, crown])
                cartoon_tree = CartoonEngine.cartoonify_mesh(tree, 'toon')
                meshes.append(cartoon_tree)
        
        return meshes
    
    @staticmethod
    def apply_motion_blur(mesh: trimesh.Trimesh, direction: np.ndarray, intensity: float = 0.5) -> List[trimesh.Trimesh]:
        """Create motion blur effect for animation"""
        blur_meshes = []
        steps = 5
        
        for i in range(steps):
            blur_mesh = mesh.copy()
            offset = direction * (i / steps) * intensity
            blur_mesh.apply_translation(offset)
            
            # Fade alpha
            alpha = int(255 * (1 - i / steps))
            if hasattr(blur_mesh.visual, 'vertex_colors'):
                colors = np.array(blur_mesh.visual.vertex_colors)
                colors[:, 3] = alpha
                blur_mesh.visual.vertex_colors = colors
            
            blur_meshes.append(blur_mesh)
        
        return blur_meshes
    
    @staticmethod
    def generate_cartoon_effects(effect_type: str, position: np.ndarray = np.array([0, 0, 0])) -> trimesh.Trimesh:
        """Generate cartoon effects (explosions, speed lines, etc)"""
        
        if effect_type == 'explosion':
            particles = []
            for i in range(50):
                angle_h = np.random.uniform(0, 2*np.pi)
                angle_v = np.random.uniform(-np.pi/4, np.pi/4)
                distance = np.random.uniform(1, 5)
                
                x = position[0] + distance * np.cos(angle_h) * np.cos(angle_v)
                y = position[1] + distance * np.sin(angle_v)
                z = position[2] + distance * np.sin(angle_h) * np.cos(angle_v)
                
                particle = trimesh.creation.icosphere(subdivisions=1, radius=0.3)
                particle.apply_translation([x, y, z])
                
                # Fire colors
                color = [255, np.random.randint(100, 200), 0, 255]
                particle.visual.vertex_colors = color
                particles.append(particle)
            
            return trimesh.util.concatenate(particles)
        
        elif effect_type == 'speed_lines':
            lines = []
            for i in range(20):
                angle = (i / 20) * 2 * np.pi
                length = 10
                
                line = trimesh.creation.cylinder(radius=0.1, height=length, sections=4)
                line.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
                
                x = position[0] + 5 * np.cos(angle)
                z = position[2] + 5 * np.sin(angle)
                line.apply_translation([x, position[1], z])
                
                line.visual.vertex_colors = [255, 255, 255, 200]
                lines.append(line)
            
            return trimesh.util.concatenate(lines)
        
        elif effect_type == 'impact':
            rings = []
            for i in range(5):
                ring = trimesh.creation.annulus(r_min=1+i, r_max=1.5+i, height=0.2, sections=32)
                ring.apply_translation(position)
                ring.visual.vertex_colors = [255, 255, 0, 255 - i*40]
                rings.append(ring)
            
            return trimesh.util.concatenate(rings)
        
        return trimesh.creation.icosphere(subdivisions=1, radius=0.5)
