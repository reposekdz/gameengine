import numpy as np
import trimesh
from typing import Dict, List, Any
import cv2
import json

class CustomizationEngine:
    """Production-ready customization system for all generated objects"""
    
    @staticmethod
    def customize_city(city_meshes: List[trimesh.Trimesh], params: Dict) -> List[trimesh.Trimesh]:
        """Customize generated city with advanced parameters"""
        customized = []
        
        for mesh in city_meshes:
            modified = mesh.copy()
            
            # Building height adjustment
            if params.get('building_height_multiplier'):
                scale_z = params['building_height_multiplier']
                modified.apply_scale([1, 1, scale_z])
            
            # Color scheme
            if params.get('color_scheme'):
                modified = CustomizationEngine._apply_color_scheme(modified, params['color_scheme'])
            
            # Density adjustment
            if params.get('density') and np.random.random() > params['density']:
                continue
            
            # Style transformation
            if params.get('architectural_style'):
                modified = CustomizationEngine._apply_architectural_style(modified, params['architectural_style'])
            
            # Weather effects
            if params.get('weather'):
                modified = CustomizationEngine._apply_weather(modified, params['weather'])
            
            # Time of day lighting
            if params.get('time_of_day'):
                modified = CustomizationEngine._apply_lighting(modified, params['time_of_day'])
            
            # Detail level
            if params.get('detail_level'):
                modified = CustomizationEngine._adjust_detail(modified, params['detail_level'])
            
            customized.append(modified)
        
        return customized
    
    @staticmethod
    def customize_person(person_mesh: trimesh.Trimesh, params: Dict) -> trimesh.Trimesh:
        """Customize person with photorealistic parameters"""
        modified = person_mesh.copy()
        
        # Skin tone
        if params.get('skin_tone'):
            skin_colors = {
                'very_light': [255, 235, 205],
                'light': [255, 220, 177],
                'medium': [210, 180, 140],
                'tan': [198, 134, 66],
                'brown': [141, 85, 36],
                'dark': [101, 67, 33]
            }
            color = skin_colors.get(params['skin_tone'], [255, 220, 177])
            modified.visual.vertex_colors = color + [255]
        
        # Body proportions
        if params.get('height'):
            modified.apply_scale([1, 1, params['height']])
        
        if params.get('width'):
            modified.apply_scale([params['width'], params['width'], 1])
        
        # Muscle definition
        if params.get('muscle_definition'):
            modified = CustomizationEngine._add_muscle_definition(modified, params['muscle_definition'])
        
        # Clothing color
        if params.get('clothing_color'):
            modified = CustomizationEngine._apply_clothing_color(modified, params['clothing_color'])
        
        # Facial features
        if params.get('facial_features'):
            modified = CustomizationEngine._customize_face(modified, params['facial_features'])
        
        # Hair style
        if params.get('hair_style'):
            hair = CustomizationEngine._generate_hair(params['hair_style'], params.get('hair_color', [50, 30, 20]))
            modified = trimesh.util.concatenate([modified, hair])
        
        # Accessories
        if params.get('accessories'):
            for accessory in params['accessories']:
                acc_mesh = CustomizationEngine._generate_accessory(accessory)
                modified = trimesh.util.concatenate([modified, acc_mesh])
        
        return modified
    
    @staticmethod
    def customize_cartoon(cartoon_mesh: trimesh.Trimesh, params: Dict) -> trimesh.Trimesh:
        """Customize cartoon with studio-quality parameters"""
        modified = cartoon_mesh.copy()
        
        # Exaggeration level
        if params.get('exaggeration'):
            modified = CustomizationEngine._apply_exaggeration(modified, params['exaggeration'])
        
        # Color saturation
        if params.get('saturation'):
            modified = CustomizationEngine._adjust_saturation(modified, params['saturation'])
        
        # Outline thickness
        if params.get('outline_thickness'):
            modified = CustomizationEngine._adjust_outline(modified, params['outline_thickness'])
        
        # Expression
        if params.get('expression'):
            modified = CustomizationEngine._apply_expression(modified, params['expression'])
        
        # Animation style
        if params.get('animation_style'):
            modified = CustomizationEngine._apply_animation_style(modified, params['animation_style'])
        
        return modified
    
    @staticmethod
    def customize_vehicle(vehicle_mesh: trimesh.Trimesh, params: Dict) -> trimesh.Trimesh:
        """Customize vehicle with realistic parameters"""
        modified = vehicle_mesh.copy()
        
        # Paint color
        if params.get('paint_color'):
            modified.visual.vertex_colors = params['paint_color'] + [255]
        
        # Metallic finish
        if params.get('metallic'):
            modified = CustomizationEngine._apply_metallic(modified, params['metallic'])
        
        # Damage/wear
        if params.get('wear_level'):
            modified = CustomizationEngine._apply_wear(modified, params['wear_level'])
        
        # Custom parts
        if params.get('custom_parts'):
            for part in params['custom_parts']:
                part_mesh = CustomizationEngine._generate_vehicle_part(part)
                modified = trimesh.util.concatenate([modified, part_mesh])
        
        # Decals/livery
        if params.get('decals'):
            modified = CustomizationEngine._apply_decals(modified, params['decals'])
        
        return modified
    
    @staticmethod
    def customize_animal(animal_mesh: trimesh.Trimesh, params: Dict) -> trimesh.Trimesh:
        """Customize animal with realistic variations"""
        modified = animal_mesh.copy()
        
        # Fur/scale pattern
        if params.get('pattern'):
            modified = CustomizationEngine._apply_pattern(modified, params['pattern'])
        
        # Color variation
        if params.get('color_variation'):
            modified = CustomizationEngine._apply_color_variation(modified, params['color_variation'])
        
        # Size variation
        if params.get('size_multiplier'):
            modified.apply_scale(params['size_multiplier'])
        
        # Age effects
        if params.get('age'):
            modified = CustomizationEngine._apply_age_effects(modified, params['age'])
        
        return modified
    
    @staticmethod
    def _apply_color_scheme(mesh: trimesh.Trimesh, scheme: str) -> trimesh.Trimesh:
        """Apply color scheme to mesh"""
        schemes = {
            'modern': [[200, 200, 200], [100, 100, 100], [50, 50, 50]],
            'vibrant': [[255, 100, 100], [100, 255, 100], [100, 100, 255]],
            'pastel': [[255, 200, 200], [200, 255, 200], [200, 200, 255]],
            'monochrome': [[200, 200, 200], [150, 150, 150], [100, 100, 100]],
            'neon': [[255, 0, 255], [0, 255, 255], [255, 255, 0]]
        }
        
        colors = schemes.get(scheme, schemes['modern'])
        mesh.visual.vertex_colors = np.random.choice(colors) + [255]
        return mesh
    
    @staticmethod
    def _apply_architectural_style(mesh: trimesh.Trimesh, style: str) -> trimesh.Trimesh:
        """Apply architectural style transformations"""
        if style == 'gothic':
            mesh.apply_scale([1, 1, 1.5])
        elif style == 'modern':
            mesh.apply_scale([1.2, 1.2, 1])
        elif style == 'art_deco':
            mesh.apply_scale([0.9, 0.9, 1.3])
        return mesh
    
    @staticmethod
    def _apply_weather(mesh: trimesh.Trimesh, weather: str) -> trimesh.Trimesh:
        """Apply weather effects"""
        if weather == 'rain':
            colors = np.array(mesh.visual.vertex_colors, dtype=float)
            colors[:, :3] *= 0.7
            mesh.visual.vertex_colors = colors.astype(np.uint8)
        elif weather == 'snow':
            colors = np.array(mesh.visual.vertex_colors, dtype=float)
            colors[:, :3] = (colors[:, :3] + [255, 255, 255]) / 2
            mesh.visual.vertex_colors = colors.astype(np.uint8)
        elif weather == 'fog':
            colors = np.array(mesh.visual.vertex_colors, dtype=float)
            colors[:, :3] = (colors[:, :3] + [200, 200, 200]) / 2
            mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _apply_lighting(mesh: trimesh.Trimesh, time: str) -> trimesh.Trimesh:
        """Apply time-of-day lighting"""
        lighting = {
            'dawn': [255, 200, 150],
            'day': [255, 255, 255],
            'dusk': [255, 150, 100],
            'night': [50, 50, 100]
        }
        
        light_color = lighting.get(time, [255, 255, 255])
        colors = np.array(mesh.visual.vertex_colors, dtype=float)
        colors[:, :3] = (colors[:, :3] * np.array(light_color)) / 255
        mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _adjust_detail(mesh: trimesh.Trimesh, level: str) -> trimesh.Trimesh:
        """Adjust mesh detail level"""
        if level == 'low':
            mesh = mesh.simplify_quadric_decimation(len(mesh.faces) // 4)
        elif level == 'medium':
            mesh = mesh.simplify_quadric_decimation(len(mesh.faces) // 2)
        return mesh
    
    @staticmethod
    def _add_muscle_definition(mesh: trimesh.Trimesh, level: float) -> trimesh.Trimesh:
        """Add muscle definition to character"""
        vertices = mesh.vertices.copy()
        normals = mesh.vertex_normals
        
        for i in range(len(vertices)):
            noise = np.sin(vertices[i][0] * 10) * np.cos(vertices[i][2] * 10)
            vertices[i] += normals[i] * noise * level * 0.02
        
        mesh.vertices = vertices
        return mesh
    
    @staticmethod
    def _apply_clothing_color(mesh: trimesh.Trimesh, color: List[int]) -> trimesh.Trimesh:
        """Apply clothing color to lower body"""
        vertices = mesh.vertices
        colors = np.array(mesh.visual.vertex_colors)
        
        for i, v in enumerate(vertices):
            if v[2] < 1.0:
                colors[i, :3] = color
        
        mesh.visual.vertex_colors = colors
        return mesh
    
    @staticmethod
    def _customize_face(mesh: trimesh.Trimesh, features: Dict) -> trimesh.Trimesh:
        """Customize facial features"""
        vertices = mesh.vertices.copy()
        
        if features.get('nose_size'):
            for i, v in enumerate(vertices):
                if v[2] > 1.5 and v[1] > 0.5:
                    vertices[i][1] += features['nose_size'] * 0.1
        
        if features.get('eye_size'):
            for i, v in enumerate(vertices):
                if v[2] > 1.6 and abs(v[0]) > 0.3:
                    vertices[i] *= (1 + features['eye_size'] * 0.2)
        
        mesh.vertices = vertices
        return mesh
    
    @staticmethod
    def _generate_hair(style: str, color: List[int]) -> trimesh.Trimesh:
        """Generate hair mesh"""
        if style == 'short':
            hair = trimesh.creation.icosphere(subdivisions=2, radius=0.15)
            hair.apply_translation([0, 0, 1.8])
        elif style == 'long':
            hair = trimesh.creation.capsule(radius=0.15, height=0.5)
            hair.apply_translation([0, 0, 1.9])
        else:
            hair = trimesh.creation.icosphere(subdivisions=2, radius=0.12)
            hair.apply_translation([0, 0, 1.8])
        
        hair.visual.vertex_colors = color + [255]
        return hair
    
    @staticmethod
    def _generate_accessory(accessory_type: str) -> trimesh.Trimesh:
        """Generate accessory mesh"""
        if accessory_type == 'glasses':
            frame = trimesh.creation.box(extents=[0.3, 0.05, 0.1])
            frame.apply_translation([0, 0.7, 1.7])
            return frame
        elif accessory_type == 'hat':
            hat = trimesh.creation.cylinder(radius=0.2, height=0.15, sections=16)
            hat.apply_translation([0, 0, 1.9])
            return hat
        else:
            return trimesh.creation.icosphere(subdivisions=1, radius=0.05)
    
    @staticmethod
    def _apply_exaggeration(mesh: trimesh.Trimesh, level: float) -> trimesh.Trimesh:
        """Apply cartoon exaggeration"""
        vertices = mesh.vertices.copy()
        center = vertices.mean(axis=0)
        
        for i in range(len(vertices)):
            direction = vertices[i] - center
            vertices[i] += direction * level * 0.1
        
        mesh.vertices = vertices
        return mesh
    
    @staticmethod
    def _adjust_saturation(mesh: trimesh.Trimesh, saturation: float) -> trimesh.Trimesh:
        """Adjust color saturation"""
        colors = np.array(mesh.visual.vertex_colors, dtype=float)
        
        for i in range(len(colors)):
            rgb = colors[i, :3].reshape(1, 1, 3).astype(np.uint8)
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[0][0]
            hsv[1] = min(255, hsv[1] * saturation)
            rgb_new = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2RGB)[0][0]
            colors[i, :3] = rgb_new
        
        mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _adjust_outline(mesh: trimesh.Trimesh, thickness: float) -> trimesh.Trimesh:
        """Adjust outline thickness"""
        outline = mesh.copy()
        if mesh.vertex_normals is not None:
            outline.vertices = mesh.vertices - mesh.vertex_normals * thickness
        outline.faces = np.fliplr(outline.faces)
        outline.visual.vertex_colors = [0, 0, 0, 255]
        return trimesh.util.concatenate([mesh, outline])
    
    @staticmethod
    def _apply_expression(mesh: trimesh.Trimesh, expression: str) -> trimesh.Trimesh:
        """Apply facial expression"""
        vertices = mesh.vertices.copy()
        
        if expression == 'happy':
            for i, v in enumerate(vertices):
                if v[2] > 1.5 and v[1] > 0.5:
                    vertices[i][2] += 0.05
        elif expression == 'sad':
            for i, v in enumerate(vertices):
                if v[2] > 1.5 and v[1] > 0.5:
                    vertices[i][2] -= 0.05
        elif expression == 'angry':
            for i, v in enumerate(vertices):
                if v[2] > 1.6 and abs(v[0]) > 0.3:
                    vertices[i][2] -= 0.03
        
        mesh.vertices = vertices
        return mesh
    
    @staticmethod
    def _apply_animation_style(mesh: trimesh.Trimesh, style: str) -> trimesh.Trimesh:
        """Apply animation style characteristics"""
        if style == 'bouncy':
            mesh.apply_scale([1, 1, 1.1])
        elif style == 'squash_stretch':
            mesh.apply_scale([1.1, 1.1, 0.9])
        return mesh
    
    @staticmethod
    def _apply_metallic(mesh: trimesh.Trimesh, level: float) -> trimesh.Trimesh:
        """Apply metallic finish"""
        colors = np.array(mesh.visual.vertex_colors, dtype=float)
        colors[:, :3] = colors[:, :3] * (1 - level) + np.array([200, 200, 200]) * level
        mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _apply_wear(mesh: trimesh.Trimesh, level: float) -> trimesh.Trimesh:
        """Apply wear and tear"""
        colors = np.array(mesh.visual.vertex_colors, dtype=float)
        noise = np.random.random(len(colors)) * level
        colors[:, :3] *= (1 - noise[:, np.newaxis])
        mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _generate_vehicle_part(part_type: str) -> trimesh.Trimesh:
        """Generate custom vehicle part"""
        if part_type == 'spoiler':
            spoiler = trimesh.creation.box(extents=[1.5, 0.1, 0.3])
            spoiler.apply_translation([0, 0, 0.8])
            return spoiler
        elif part_type == 'hood_scoop':
            scoop = trimesh.creation.box(extents=[0.5, 0.3, 0.2])
            scoop.apply_translation([0, 0, 0.7])
            return scoop
        else:
            return trimesh.creation.box(extents=[0.2, 0.2, 0.2])
    
    @staticmethod
    def _apply_decals(mesh: trimesh.Trimesh, decals: List[str]) -> trimesh.Trimesh:
        """Apply decals to vehicle"""
        return mesh
    
    @staticmethod
    def _apply_pattern(mesh: trimesh.Trimesh, pattern: str) -> trimesh.Trimesh:
        """Apply fur/scale pattern"""
        colors = np.array(mesh.visual.vertex_colors, dtype=float)
        vertices = mesh.vertices
        
        if pattern == 'stripes':
            for i, v in enumerate(vertices):
                if int(v[0] * 5) % 2 == 0:
                    colors[i, :3] *= 0.7
        elif pattern == 'spots':
            for i, v in enumerate(vertices):
                noise = np.sin(v[0] * 10) * np.cos(v[2] * 10)
                if noise > 0.5:
                    colors[i, :3] *= 0.6
        
        mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _apply_color_variation(mesh: trimesh.Trimesh, variation: float) -> trimesh.Trimesh:
        """Apply color variation"""
        colors = np.array(mesh.visual.vertex_colors, dtype=float)
        noise = np.random.random(len(colors)) * variation
        colors[:, :3] *= (1 + noise[:, np.newaxis] - variation/2)
        colors = np.clip(colors, 0, 255)
        mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def _apply_age_effects(mesh: trimesh.Trimesh, age: str) -> trimesh.Trimesh:
        """Apply age-related effects"""
        if age == 'old':
            colors = np.array(mesh.visual.vertex_colors, dtype=float)
            colors[:, :3] *= 0.8
            mesh.visual.vertex_colors = colors.astype(np.uint8)
        return mesh
    
    @staticmethod
    def save_customization_preset(preset_name: str, params: Dict):
        """Save customization preset"""
        os.makedirs('presets', exist_ok=True)
        with open(f'presets/{preset_name}.json', 'w') as f:
            json.dump(params, f, indent=2)
    
    @staticmethod
    def load_customization_preset(preset_name: str) -> Dict:
        """Load customization preset"""
        with open(f'presets/{preset_name}.json', 'r') as f:
            return json.load(f)
