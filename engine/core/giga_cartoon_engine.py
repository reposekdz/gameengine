import numpy as np
import trimesh
from typing import List, Dict
import cv2
from concurrent.futures import ThreadPoolExecutor

class GigaCartoonEngine:
    """Advanced cartoon generation with Disney/Pixar quality"""
    
    CARTOON_STYLES = {
        'disney': {'saturation': 1.8, 'brightness': 1.2, 'outline': 0.08, 'levels': 5},
        'pixar': {'saturation': 1.6, 'brightness': 1.1, 'outline': 0.06, 'levels': 6},
        'anime': {'saturation': 2.0, 'brightness': 1.0, 'outline': 0.1, 'levels': 3},
        'cartoon_network': {'saturation': 2.2, 'brightness': 1.3, 'outline': 0.12, 'levels': 4},
        'studio_ghibli': {'saturation': 1.4, 'brightness': 1.0, 'outline': 0.05, 'levels': 7},
        'south_park': {'saturation': 2.5, 'brightness': 1.4, 'outline': 0.15, 'levels': 2},
        'simpsons': {'saturation': 2.0, 'brightness': 1.2, 'outline': 0.1, 'levels': 3},
        'family_guy': {'saturation': 1.8, 'brightness': 1.1, 'outline': 0.09, 'levels': 4}
    }
    
    @staticmethod
    def cartoonify_advanced(mesh: trimesh.Trimesh, style: str = 'disney') -> trimesh.Trimesh:
        """Apply advanced cartoon style"""
        style_params = GigaCartoonEngine.CARTOON_STYLES.get(style, GigaCartoonEngine.CARTOON_STYLES['disney'])
        
        result = mesh.copy()
        
        # Color quantization
        if hasattr(result.visual, 'vertex_colors'):
            colors = np.array(result.visual.vertex_colors, dtype=float)
            
            # Convert to HSV
            for i in range(len(colors)):
                rgb = colors[i, :3].reshape(1, 1, 3).astype(np.uint8)
                hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[0][0]
                
                # Boost saturation
                hsv[1] = min(255, hsv[1] * style_params['saturation'])
                
                # Adjust brightness
                hsv[2] = min(255, hsv[2] * style_params['brightness'])
                
                # Quantize
                hsv[2] = int(hsv[2] / (256 / style_params['levels'])) * (256 // style_params['levels'])
                
                # Convert back
                rgb_new = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2RGB)[0][0]
                colors[i, :3] = rgb_new
            
            result.visual.vertex_colors = colors.astype(np.uint8)
        
        # Add outline
        outline = GigaCartoonEngine._generate_advanced_outline(mesh, style_params['outline'])
        return trimesh.util.concatenate([result, outline])
    
    @staticmethod
    def _generate_advanced_outline(mesh: trimesh.Trimesh, thickness: float) -> trimesh.Trimesh:
        """Generate smooth outline"""
        outline = mesh.copy()
        
        if mesh.vertex_normals is not None:
            # Smooth normals for better outline
            smoothed_normals = mesh.vertex_normals.copy()
            for i in range(3):
                smoothed_normals = (smoothed_normals + np.roll(smoothed_normals, 1, axis=0)) / 2
            
            outline.vertices = mesh.vertices - smoothed_normals * thickness
        
        outline.faces = np.fliplr(outline.faces)
        outline.visual.vertex_colors = [0, 0, 0, 255]
        
        return outline
    
    @staticmethod
    def generate_cartoon_movie_scene(duration_seconds: int = 60, fps: int = 60, style: str = 'pixar') -> List[Dict]:
        """Generate complete animated movie scene"""
        frames = []
        total_frames = duration_seconds * fps
        
        # Scene setup
        from engine.generators.giga_world_generator import GigaWorldGenerator
        
        # Characters
        hero = GigaWorldGenerator.generate_person('civilian', 'adult', 'average', 'standing')
        hero = GigaCartoonEngine.cartoonify_advanced(hero, style)
        
        villain = GigaWorldGenerator.generate_person('civilian', 'adult', 'muscular', 'standing')
        villain = GigaCartoonEngine.cartoonify_advanced(villain, style)
        
        # Environment
        from engine.core.cartoon_engine import CartoonEngine
        environment = CartoonEngine.generate_cartoon_environment('city')
        
        # Animate
        for frame in range(total_frames):
            t = frame / total_frames
            
            # Hero movement
            hero_pos = [np.sin(t * 2 * np.pi) * 5, 0, 0]
            hero_frame = hero.copy()
            hero_frame.apply_translation(hero_pos)
            
            # Villain movement
            villain_pos = [-np.sin(t * 2 * np.pi) * 5, 0, 5]
            villain_frame = villain.copy()
            villain_frame.apply_translation(villain_pos)
            
            frames.append({
                'frame': frame,
                'time': frame / fps,
                'objects': [hero_frame, villain_frame] + environment
            })
        
        return frames
    
    @staticmethod
    def generate_cartoon_character_advanced(character_type: str = 'hero', style: str = 'disney') -> trimesh.Trimesh:
        """Generate advanced cartoon character"""
        meshes = []
        
        if character_type == 'hero':
            # Large expressive head (cartoon proportions 1:3)
            head = trimesh.creation.icosphere(subdivisions=4, radius=1.5)
            head.apply_translation([0, 0, 3.5])
            meshes.append(head)
            
            # Large eyes
            for x in [-0.5, 0.5]:
                eye_white = trimesh.creation.icosphere(subdivisions=3, radius=0.4)
                eye_white.apply_translation([x, 0.8, 3.7])
                eye_white.visual.vertex_colors = [255, 255, 255, 255]
                meshes.append(eye_white)
                
                pupil = trimesh.creation.icosphere(subdivisions=2, radius=0.2)
                pupil.apply_translation([x, 0.95, 3.8])
                pupil.visual.vertex_colors = [0, 0, 0, 255]
                meshes.append(pupil)
                
                # Highlight
                highlight = trimesh.creation.icosphere(subdivisions=1, radius=0.08)
                highlight.apply_translation([x + 0.1, 1.0, 3.9])
                highlight.visual.vertex_colors = [255, 255, 255, 255]
                meshes.append(highlight)
            
            # Smile
            smile = trimesh.creation.capsule(radius=0.1, height=0.8)
            smile.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            smile.apply_translation([0, 0.6, 3.0])
            smile.visual.vertex_colors = [255, 100, 100, 255]
            meshes.append(smile)
            
            # Body (simplified, stylized)
            body = trimesh.creation.capsule(radius=0.8, height=2.0)
            body.apply_translation([0, 0, 1.5])
            body.visual.vertex_colors = [0, 150, 255, 255]
            meshes.append(body)
            
            # Arms (noodle arms)
            for x in [-1.2, 1.2]:
                arm = trimesh.creation.capsule(radius=0.2, height=1.8)
                arm.apply_transform(trimesh.transformations.rotation_matrix(np.pi/6 * (-1 if x < 0 else 1), [0, 0, 1]))
                arm.apply_translation([x, 0, 1.5])
                arm.visual.vertex_colors = [255, 220, 177, 255]
                meshes.append(arm)
                
                # Hands (oversized)
                hand = trimesh.creation.icosphere(subdivisions=2, radius=0.35)
                hand.apply_translation([x * 1.3, 0, 0.5])
                hand.visual.vertex_colors = [255, 220, 177, 255]
                meshes.append(hand)
            
            # Legs (short, stubby)
            for x in [-0.4, 0.4]:
                leg = trimesh.creation.capsule(radius=0.3, height=1.0)
                leg.apply_translation([x, 0, 0.3])
                leg.visual.vertex_colors = [0, 100, 200, 255]
                meshes.append(leg)
                
                # Feet (oversized)
                foot = trimesh.creation.box(extents=[0.5, 0.3, 0.2])
                foot.apply_translation([x, 0.2, -0.2])
                foot.visual.vertex_colors = [50, 50, 50, 255]
                meshes.append(foot)
        
        elif character_type == 'animal_sidekick':
            # Cute animal companion
            # Body
            body = trimesh.creation.icosphere(subdivisions=3, radius=0.8)
            body.apply_translation([0, 0, 0.8])
            body.visual.vertex_colors = [255, 200, 100, 255]
            meshes.append(body)
            
            # Head (merged with body)
            head = trimesh.creation.icosphere(subdivisions=3, radius=0.6)
            head.apply_translation([0, 0, 1.5])
            head.visual.vertex_colors = [255, 200, 100, 255]
            meshes.append(head)
            
            # Huge eyes
            for x in [-0.25, 0.25]:
                eye = trimesh.creation.icosphere(subdivisions=3, radius=0.25)
                eye.apply_translation([x, 0.4, 1.6])
                eye.visual.vertex_colors = [255, 255, 255, 255]
                meshes.append(eye)
                
                pupil = trimesh.creation.icosphere(subdivisions=2, radius=0.15)
                pupil.apply_translation([x, 0.5, 1.65])
                pupil.visual.vertex_colors = [0, 0, 0, 255]
                meshes.append(pupil)
            
            # Tiny legs
            for x, y in [(-0.4, -0.3), (-0.4, 0.3), (0.4, -0.3), (0.4, 0.3)]:
                leg = trimesh.creation.cylinder(radius=0.08, height=0.3, sections=8)
                leg.apply_translation([x, y, 0.15])
                leg.visual.vertex_colors = [255, 200, 100, 255]
                meshes.append(leg)
        
        character = trimesh.util.concatenate(meshes)
        return GigaCartoonEngine.cartoonify_advanced(character, style)
    
    @staticmethod
    def generate_cartoon_world(world_type: str = 'fantasy', size: int = 5000, style: str = 'disney') -> List[trimesh.Trimesh]:
        """Generate complete cartoon world"""
        world_meshes = []
        
        if world_type == 'fantasy':
            # Stylized terrain
            terrain = trimesh.creation.box(extents=[size, size, 100])
            terrain.visual.vertex_colors = [100, 200, 100, 255]
            world_meshes.append(GigaCartoonEngine.cartoonify_advanced(terrain, style))
            
            # Candy trees
            for i in range(1000):
                x = np.random.uniform(-size/2, size/2)
                z = np.random.uniform(-size/2, size/2)
                
                trunk = trimesh.creation.cylinder(radius=0.5, height=8, sections=6)
                trunk.apply_translation([x, z, 4])
                trunk.visual.vertex_colors = [139, 69, 19, 255]
                
                crown = trimesh.creation.icosphere(subdivisions=2, radius=5)
                crown.apply_translation([x, z, 12])
                colors = [[255, 105, 180], [255, 192, 203], [255, 20, 147]]
                crown.visual.vertex_colors = random.choice(colors) + [255]
                
                tree = trimesh.util.concatenate([trunk, crown])
                world_meshes.append(GigaCartoonEngine.cartoonify_advanced(tree, style))
            
            # Castles
            for i in range(5):
                x = np.random.uniform(-size/3, size/3)
                z = np.random.uniform(-size/3, size/3)
                castle = GigaCartoonEngine._generate_cartoon_castle()
                castle.apply_translation([x, z, 0])
                world_meshes.append(GigaCartoonEngine.cartoonify_advanced(castle, style))
        
        elif world_type == 'underwater':
            # Ocean floor
            floor = trimesh.creation.box(extents=[size, size, 50])
            floor.apply_translation([0, 0, -25])
            floor.visual.vertex_colors = [194, 178, 128, 255]
            world_meshes.append(GigaCartoonEngine.cartoonify_advanced(floor, style))
            
            # Coral
            for i in range(500):
                x = np.random.uniform(-size/2, size/2)
                z = np.random.uniform(-size/2, size/2)
                
                coral = trimesh.creation.cone(radius=np.random.uniform(1, 3), height=np.random.uniform(5, 15), sections=8)
                coral.apply_translation([x, z, 0])
                colors = [[255, 127, 80], [255, 99, 71], [255, 20, 147], [138, 43, 226]]
                coral.visual.vertex_colors = random.choice(colors) + [255]
                world_meshes.append(GigaCartoonEngine.cartoonify_advanced(coral, style))
        
        return world_meshes
    
    @staticmethod
    def _generate_cartoon_castle() -> trimesh.Trimesh:
        """Generate stylized castle"""
        meshes = []
        
        # Main keep
        keep = trimesh.creation.cylinder(radius=20, height=80, sections=8)
        keep.apply_translation([0, 0, 40])
        keep.visual.vertex_colors = [200, 200, 220, 255]
        meshes.append(keep)
        
        # Towers
        for x, y in [(-30, -30), (-30, 30), (30, -30), (30, 30)]:
            tower = trimesh.creation.cylinder(radius=8, height=100, sections=8)
            tower.apply_translation([x, y, 50])
            tower.visual.vertex_colors = [180, 180, 200, 255]
            meshes.append(tower)
            
            # Cone roof
            roof = trimesh.creation.cone(radius=10, height=20, sections=8)
            roof.apply_translation([x, y, 105])
            roof.visual.vertex_colors = [200, 50, 50, 255]
            meshes.append(roof)
        
        # Walls
        for x, y, w, h in [(-30, 0, 60, 40), (30, 0, 60, 40), (0, -30, 40, 60), (0, 30, 40, 60)]:
            wall = trimesh.creation.box(extents=[w, h, 50])
            wall.apply_translation([x, y, 25])
            wall.visual.vertex_colors = [190, 190, 210, 255]
            meshes.append(wall)
        
        return trimesh.util.concatenate(meshes)
    
    @staticmethod
    def generate_cartoon_animation_sequence(character: trimesh.Trimesh, animation_type: str, frames: int = 60) -> List[trimesh.Trimesh]:
        """Generate animation sequence"""
        sequence = []
        
        for frame in range(frames):
            t = frame / frames
            char_frame = character.copy()
            
            if animation_type == 'walk':
                # Walking animation
                x = t * 10
                y = np.sin(t * 4 * np.pi) * 0.2
                char_frame.apply_translation([x, 0, y])
                
            elif animation_type == 'jump':
                # Jump animation
                y = -4 * (t - 0.5) ** 2 + 1
                char_frame.apply_translation([0, 0, y * 5])
                
            elif animation_type == 'spin':
                # Spin animation
                angle = t * 2 * np.pi
                char_frame.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
            
            sequence.append(char_frame)
        
        return sequence
    
    @staticmethod
    def batch_cartoonify(meshes: List[trimesh.Trimesh], style: str = 'disney', workers: int = 8) -> List[trimesh.Trimesh]:
        """Batch convert meshes to cartoon style"""
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(GigaCartoonEngine.cartoonify_advanced, mesh, style) for mesh in meshes]
            return [f.result() for f in futures]
