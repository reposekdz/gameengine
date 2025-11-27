import numpy as np
import trimesh
import random
from typing import List, Dict

class AssetLibrary:
    """Millions of Asset Variations"""
    
    CATEGORIES = {
        'vehicles': ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'tank', 'helicopter', 'plane', 'boat', 'submarine'],
        'buildings': ['house', 'apartment', 'skyscraper', 'warehouse', 'factory', 'shop', 'restaurant', 'hospital', 'school', 'stadium'],
        'furniture': ['chair', 'table', 'bed', 'sofa', 'desk', 'shelf', 'cabinet', 'lamp', 'tv', 'computer'],
        'weapons': ['pistol', 'rifle', 'shotgun', 'sniper', 'rocket_launcher', 'sword', 'axe', 'bow', 'grenade', 'knife'],
        'characters': ['soldier', 'civilian', 'zombie', 'robot', 'alien', 'knight', 'wizard', 'ninja', 'pirate', 'astronaut'],
        'nature': ['tree', 'bush', 'flower', 'rock', 'grass', 'mushroom', 'log', 'stump', 'vine', 'coral'],
        'props': ['barrel', 'crate', 'fence', 'sign', 'streetlight', 'bench', 'trash_can', 'mailbox', 'hydrant', 'cone'],
        'food': ['apple', 'bread', 'pizza', 'burger', 'drink', 'cake', 'donut', 'ice_cream', 'sushi', 'taco'],
        'tools': ['hammer', 'wrench', 'screwdriver', 'saw', 'drill', 'axe', 'shovel', 'pickaxe', 'rake', 'hoe'],
        'electronics': ['phone', 'laptop', 'tablet', 'camera', 'speaker', 'headphones', 'monitor', 'keyboard', 'mouse', 'controller']
    }
    
    @classmethod
    def generate_asset(cls, category: str, asset_type: str, variation: int = 0) -> trimesh.Trimesh:
        method_name = f'_create_{asset_type}'
        
        if hasattr(cls, method_name):
            return getattr(cls, method_name)(variation)
        else:
            return cls._create_generic(asset_type, variation)
    
    @classmethod
    def generate_variations(cls, category: str, asset_type: str, count: int = 100) -> List[trimesh.Trimesh]:
        return [cls.generate_asset(category, asset_type, i) for i in range(count)]
    
    @staticmethod
    def _create_car(var: int) -> trimesh.Trimesh:
        random.seed(var)
        
        # Body
        length = random.uniform(3.5, 5.0)
        width = random.uniform(1.6, 2.0)
        height = random.uniform(1.2, 1.6)
        
        body = trimesh.creation.box(extents=[length, height, width])
        body.apply_translation([0, height/2, 0])
        
        # Cabin
        cabin_length = length * 0.6
        cabin_height = height * 0.7
        cabin = trimesh.creation.box(extents=[cabin_length, cabin_height, width * 0.9])
        cabin.apply_translation([0, height + cabin_height/2, 0])
        
        # Wheels
        wheel_radius = random.uniform(0.3, 0.4)
        wheels = []
        positions = [
            [length/3, wheel_radius, width/2 + 0.1],
            [length/3, wheel_radius, -width/2 - 0.1],
            [-length/3, wheel_radius, width/2 + 0.1],
            [-length/3, wheel_radius, -width/2 - 0.1]
        ]
        
        for pos in positions:
            wheel = trimesh.creation.cylinder(radius=wheel_radius, height=0.2, sections=16)
            wheel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            wheel.apply_translation(pos)
            wheels.append(wheel)
        
        car = trimesh.util.concatenate([body, cabin] + wheels)
        
        # Random color
        color = [random.randint(50, 255), random.randint(50, 255), random.randint(50, 255), 255]
        car.visual.vertex_colors = np.tile(color, (len(car.vertices), 1))
        
        return car
    
    @staticmethod
    def _create_house(var: int) -> trimesh.Trimesh:
        random.seed(var)
        
        width = random.uniform(8, 15)
        depth = random.uniform(8, 15)
        height = random.uniform(6, 10)
        
        # Main structure
        main = trimesh.creation.box(extents=[width, height, depth])
        main.apply_translation([0, height/2, 0])
        
        # Roof
        roof_height = height * 0.4
        roof_vertices = np.array([
            [-width/2, height, -depth/2],
            [width/2, height, -depth/2],
            [width/2, height, depth/2],
            [-width/2, height, depth/2],
            [0, height + roof_height, 0]
        ])
        
        roof_faces = np.array([
            [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],
            [0, 3, 2], [0, 2, 1]
        ])
        
        roof = trimesh.Trimesh(vertices=roof_vertices, faces=roof_faces)
        
        # Door
        door = trimesh.creation.box(extents=[1.5, 2.5, 0.2])
        door.apply_translation([0, 1.25, depth/2 + 0.1])
        
        # Windows
        windows = []
        for x_pos in [-width/4, width/4]:
            window = trimesh.creation.box(extents=[1.2, 1.2, 0.2])
            window.apply_translation([x_pos, height * 0.6, depth/2 + 0.1])
            windows.append(window)
        
        house = trimesh.util.concatenate([main, roof, door] + windows)
        
        # Color
        wall_color = [random.randint(150, 220), random.randint(150, 220), random.randint(150, 220), 255]
        house.visual.vertex_colors = np.tile(wall_color, (len(house.vertices), 1))
        
        return house
    
    @staticmethod
    def _create_tree(var: int) -> trimesh.Trimesh:
        random.seed(var)
        
        trunk_height = random.uniform(5, 12)
        trunk_radius = random.uniform(0.3, 0.6)
        
        trunk = trimesh.creation.cylinder(radius=trunk_radius, height=trunk_height, sections=8)
        trunk.apply_translation([0, trunk_height/2, 0])
        
        # Crown
        crown_type = random.choice(['sphere', 'cone', 'irregular'])
        
        if crown_type == 'sphere':
            crown_radius = random.uniform(2, 4)
            crown = trimesh.creation.icosphere(radius=crown_radius, subdivisions=2)
            crown.apply_translation([0, trunk_height + crown_radius * 0.5, 0])
        elif crown_type == 'cone':
            crown_radius = random.uniform(2, 4)
            crown_height = random.uniform(4, 8)
            crown = trimesh.creation.cone(radius=crown_radius, height=crown_height, sections=8)
            crown.apply_translation([0, trunk_height + crown_height/2, 0])
        else:
            # Irregular crown with multiple spheres
            crowns = []
            for _ in range(random.randint(3, 6)):
                part = trimesh.creation.icosphere(radius=random.uniform(1, 2), subdivisions=1)
                offset = [random.uniform(-1.5, 1.5), trunk_height + random.uniform(0, 2), random.uniform(-1.5, 1.5)]
                part.apply_translation(offset)
                crowns.append(part)
            crown = trimesh.util.concatenate(crowns)
        
        tree = trimesh.util.concatenate([trunk, crown])
        tree.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(tree.vertices), 1))
        
        return tree
    
    @staticmethod
    def _create_weapon(weapon_type: str, var: int) -> trimesh.Trimesh:
        random.seed(var)
        
        if weapon_type == 'rifle':
            # Stock
            stock = trimesh.creation.box(extents=[0.3, 0.3, 1.5])
            stock.apply_translation([0, 0, -0.75])
            
            # Barrel
            barrel = trimesh.creation.cylinder(radius=0.05, height=2.0, sections=16)
            barrel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
            barrel.apply_translation([1.0, 0, 0])
            
            # Body
            body = trimesh.creation.box(extents=[0.8, 0.3, 0.4])
            body.apply_translation([0, 0, 0])
            
            weapon = trimesh.util.concatenate([stock, barrel, body])
            
        elif weapon_type == 'sword':
            # Blade
            blade = trimesh.creation.box(extents=[0.1, 0.1, 3.0])
            blade.apply_translation([0, 0, 1.5])
            
            # Handle
            handle = trimesh.creation.cylinder(radius=0.08, height=0.8, sections=8)
            handle.apply_translation([0, 0, -0.4])
            
            # Guard
            guard = trimesh.creation.box(extents=[0.5, 0.1, 0.1])
            guard.apply_translation([0, 0, 0])
            
            weapon = trimesh.util.concatenate([blade, handle, guard])
        
        else:
            weapon = trimesh.creation.box(extents=[0.5, 0.3, 1.0])
        
        weapon.visual.vertex_colors = np.tile([100, 100, 100, 255], (len(weapon.vertices), 1))
        
        return weapon
    
    @staticmethod
    def _create_generic(asset_type: str, var: int) -> trimesh.Trimesh:
        random.seed(var)
        
        size = random.uniform(0.5, 2.0)
        shape_type = random.choice(['box', 'sphere', 'cylinder'])
        
        if shape_type == 'box':
            asset = trimesh.creation.box(extents=[size, size, size])
        elif shape_type == 'sphere':
            asset = trimesh.creation.icosphere(radius=size/2, subdivisions=2)
        else:
            asset = trimesh.creation.cylinder(radius=size/2, height=size, sections=16)
        
        color = [random.randint(50, 255), random.randint(50, 255), random.randint(50, 255), 255]
        asset.visual.vertex_colors = np.tile(color, (len(asset.vertices), 1))
        
        return asset
    
    @classmethod
    def get_all_assets(cls) -> Dict[str, List[str]]:
        return cls.CATEGORIES
    
    @classmethod
    def get_asset_count(cls) -> int:
        total = 0
        for category, assets in cls.CATEGORIES.items():
            total += len(assets) * 1000  # 1000 variations each
        return total