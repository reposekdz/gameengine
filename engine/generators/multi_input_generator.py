import numpy as np
import trimesh
import cv2
from typing import List, Tuple, Union
from PIL import Image

class MultiInputGenerator:
    """Generate 3 advanced objects from any combination of inputs"""
    
    @staticmethod
    def generate_from_multi_input(
        text: str = None,
        images: List[str] = None,
        reference_3d: str = None,
        style: str = 'realistic'
    ) -> List[trimesh.Trimesh]:
        """Generate 3 unique advanced objects from combined inputs"""
        
        objects = []
        
        # Object 1: Primary from text
        if text:
            obj1 = MultiInputGenerator._generate_from_text_advanced(text, style)
            objects.append(obj1)
        
        # Object 2: From images
        if images and len(images) > 0:
            obj2 = MultiInputGenerator._generate_from_images_fusion(images, style)
            objects.append(obj2)
        
        # Object 3: Hybrid combination
        if text and images:
            obj3 = MultiInputGenerator._generate_hybrid(text, images, style)
            objects.append(obj3)
        elif reference_3d:
            obj3 = MultiInputGenerator._generate_variation(reference_3d, style)
            objects.append(obj3)
        
        # Ensure we have 3 objects
        while len(objects) < 3:
            objects.append(MultiInputGenerator._generate_procedural(style))
        
        return objects[:3]
    
    @staticmethod
    def _generate_from_text_advanced(text: str, style: str) -> trimesh.Trimesh:
        """Advanced text-to-3D with style"""
        from ..generators.text_to_3d import TextTo3DGenerator
        
        gen = TextTo3DGenerator()
        mesh = gen.generate_from_text(text)
        
        if style == 'cartoon':
            mesh = MultiInputGenerator._apply_cartoon_style(mesh)
        elif style == 'lowpoly':
            mesh = MultiInputGenerator._apply_lowpoly_style(mesh)
        elif style == 'detailed':
            mesh = MultiInputGenerator._apply_detail_enhancement(mesh)
        
        return mesh
    
    @staticmethod
    def _generate_from_images_fusion(images: List[str], style: str) -> trimesh.Trimesh:
        """Fuse multiple images into single 3D object"""
        from ..generators.image_to_3d import ImageTo3DGenerator
        
        gen = ImageTo3DGenerator()
        meshes = []
        
        for img_path in images[:3]:  # Use up to 3 images
            try:
                mesh = gen.generate_from_image(img_path, method='advanced')
                meshes.append(mesh)
            except:
                pass
        
        if not meshes:
            return MultiInputGenerator._generate_procedural(style)
        
        # Combine meshes
        if len(meshes) == 1:
            combined = meshes[0]
        else:
            # Position meshes in a composition
            for i, mesh in enumerate(meshes):
                offset = np.array([i * 2 - 2, 0, 0])
                mesh.apply_translation(offset)
            combined = trimesh.util.concatenate(meshes)
        
        return combined
    
    @staticmethod
    def _generate_hybrid(text: str, images: List[str], style: str) -> trimesh.Trimesh:
        """Generate hybrid object from text and images"""
        from ..generators.text_to_3d import TextTo3DGenerator
        from ..generators.image_to_3d import ImageTo3DGenerator
        
        text_gen = TextTo3DGenerator()
        image_gen = ImageTo3DGenerator()
        
        # Base from text
        base_mesh = text_gen.generate_from_text(text)
        
        # Texture/detail from image
        if images and len(images) > 0:
            try:
                detail_mesh = image_gen.generate_from_image(images[0], method='advanced')
                
                # Scale detail mesh to fit base
                detail_scale = base_mesh.extents.max() / detail_mesh.extents.max() * 0.5
                detail_mesh.apply_scale(detail_scale)
                
                # Position on top
                detail_mesh.apply_translation([0, base_mesh.extents[1], 0])
                
                combined = trimesh.util.concatenate([base_mesh, detail_mesh])
                return combined
            except:
                pass
        
        return base_mesh
    
    @staticmethod
    def _generate_variation(reference_path: str, style: str) -> trimesh.Trimesh:
        """Generate variation of reference 3D model"""
        try:
            ref_mesh = trimesh.load(reference_path)
            
            # Create variation
            varied = ref_mesh.copy()
            
            # Apply random transformations
            scale_factor = np.random.uniform(0.8, 1.2, 3)
            varied.apply_scale(scale_factor)
            
            # Add noise to vertices
            noise = np.random.normal(0, 0.02, varied.vertices.shape)
            varied.vertices += noise
            
            # Change colors
            if hasattr(varied.visual, 'vertex_colors'):
                color_shift = np.random.randint(-30, 30, 3)
                colors = varied.visual.vertex_colors[:, :3].astype(int)
                colors = np.clip(colors + color_shift, 0, 255).astype(np.uint8)
                varied.visual.vertex_colors[:, :3] = colors
            
            return varied
        except:
            return MultiInputGenerator._generate_procedural(style)
    
    @staticmethod
    def _generate_procedural(style: str) -> trimesh.Trimesh:
        """Generate procedural object"""
        shape_type = np.random.choice(['complex', 'organic', 'geometric'])
        
        if shape_type == 'complex':
            # Multi-part object
            parts = []
            for _ in range(np.random.randint(3, 7)):
                part = trimesh.creation.icosphere(radius=np.random.uniform(0.5, 2), subdivisions=2)
                offset = np.random.uniform(-3, 3, 3)
                part.apply_translation(offset)
                parts.append(part)
            mesh = trimesh.util.concatenate(parts)
        
        elif shape_type == 'organic':
            # Organic blob
            mesh = trimesh.creation.icosphere(radius=2, subdivisions=3)
            vertices = mesh.vertices.copy()
            for i in range(len(vertices)):
                noise_val = np.random.normal(0, 0.3)
                vertices[i] += mesh.vertex_normals[i] * noise_val
            mesh.vertices = vertices
        
        else:
            # Geometric
            mesh = trimesh.creation.box(extents=np.random.uniform(1, 3, 3))
        
        # Apply style
        if style == 'cartoon':
            mesh = MultiInputGenerator._apply_cartoon_style(mesh)
        
        return mesh
    
    @staticmethod
    def _apply_cartoon_style(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply cartoon styling"""
        # Simplify
        target_faces = max(len(mesh.faces) // 3, 100)
        try:
            mesh = mesh.simplify_quadric_decimation(target_faces)
        except:
            pass
        
        # Bright colors
        if hasattr(mesh.visual, 'vertex_colors'):
            colors = mesh.visual.vertex_colors[:, :3].astype(float)
            colors = np.clip(colors * 1.3, 0, 255).astype(np.uint8)
            mesh.visual.vertex_colors[:, :3] = colors
        else:
            color = np.random.randint(100, 255, 3)
            mesh.visual.vertex_colors = np.tile([*color, 255], (len(mesh.vertices), 1))
        
        return mesh
    
    @staticmethod
    def _apply_lowpoly_style(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply low-poly styling"""
        target_faces = max(len(mesh.faces) // 5, 50)
        try:
            mesh = mesh.simplify_quadric_decimation(target_faces)
        except:
            pass
        
        return mesh
    
    @staticmethod
    def _apply_detail_enhancement(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Enhance detail"""
        try:
            mesh = mesh.subdivide()
        except:
            pass
        
        return mesh
    
    @staticmethod
    def generate_batch(
        text_prompts: List[str] = None,
        image_paths: List[str] = None,
        count: int = 10,
        style: str = 'realistic'
    ) -> List[trimesh.Trimesh]:
        """Generate batch of objects"""
        
        objects = []
        
        for i in range(count):
            text = text_prompts[i % len(text_prompts)] if text_prompts else None
            images = [image_paths[i % len(image_paths)]] if image_paths else None
            
            batch_objects = MultiInputGenerator.generate_from_multi_input(
                text=text,
                images=images,
                style=style
            )
            
            objects.extend(batch_objects)
        
        return objects