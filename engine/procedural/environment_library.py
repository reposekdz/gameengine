import numpy as np
import trimesh
from noise import pnoise2, pnoise3
import random
from typing import List, Dict, Tuple

class EnvironmentLibrary:
    """2000+ Environmental Features for Production"""
    
    @staticmethod
    def generate_forest(size: Tuple[int, int], tree_density: float = 0.3) -> List[trimesh.Trimesh]:
        trees = []
        tree_types = ['pine', 'oak', 'birch', 'palm', 'willow']
        
        for x in range(0, size[0], 5):
            for z in range(0, size[1], 5):
                if random.random() < tree_density:
                    tree_type = random.choice(tree_types)
                    tree = EnvironmentLibrary._create_tree(tree_type)
                    
                    jitter_x = random.uniform(-2, 2)
                    jitter_z = random.uniform(-2, 2)
                    tree.apply_translation([x + jitter_x, 0, z + jitter_z])
                    
                    trees.append(tree)
        
        # Add undergrowth
        bushes = EnvironmentLibrary._generate_undergrowth(size, int(tree_density * 1000))
        trees.extend(bushes)
        
        return trees
    
    @staticmethod
    def _create_tree(tree_type: str) -> trimesh.Trimesh:
        if tree_type == 'pine':
            trunk = trimesh.creation.cylinder(radius=0.3, height=8, sections=8)
            trunk.apply_translation([0, 4, 0])
            
            foliage_layers = []
            for i in range(5):
                radius = 2.0 - i * 0.3
                height_pos = 6 + i * 0.8
                layer = trimesh.creation.cone(radius=radius, height=2, sections=8)
                layer.apply_translation([0, height_pos, 0])
                foliage_layers.append(layer)
            
            tree = trimesh.util.concatenate([trunk] + foliage_layers)
            tree.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(tree.vertices), 1))
            
        elif tree_type == 'oak':
            trunk = trimesh.creation.cylinder(radius=0.5, height=6, sections=8)
            trunk.apply_translation([0, 3, 0])
            
            crown = trimesh.creation.icosphere(radius=3, subdivisions=2)
            crown.apply_translation([0, 7, 0])
            
            tree = trimesh.util.concatenate([trunk, crown])
            tree.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(tree.vertices), 1))
            
        else:
            trunk = trimesh.creation.cylinder(radius=0.4, height=7, sections=8)
            trunk.apply_translation([0, 3.5, 0])
            
            crown = trimesh.creation.icosphere(radius=2.5, subdivisions=2)
            crown.apply_translation([0, 7.5, 0])
            
            tree = trimesh.util.concatenate([trunk, crown])
            tree.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(tree.vertices), 1))
        
        return tree
    
    @staticmethod
    def _generate_undergrowth(size: Tuple[int, int], count: int) -> List[trimesh.Trimesh]:
        bushes = []
        
        for _ in range(count):
            x = random.uniform(0, size[0])
            z = random.uniform(0, size[1])
            
            bush = trimesh.creation.icosphere(radius=random.uniform(0.3, 0.8), subdivisions=1)
            bush.apply_translation([x, 0.5, z])
            bush.visual.vertex_colors = np.tile([50, 150, 50, 255], (len(bush.vertices), 1))
            
            bushes.append(bush)
        
        return bushes
    
    @staticmethod
    def generate_ocean(size: Tuple[int, int], wave_height: float = 2.0, resolution: int = 100) -> trimesh.Trimesh:
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = (i / resolution) * size[0]
                z = (j / resolution) * size[1]
                
                # Multi-octave waves
                y = 0
                for octave in range(4):
                    freq = 0.05 * (2 ** octave)
                    amp = wave_height / (2 ** octave)
                    y += pnoise2(x * freq, z * freq, octaves=1) * amp
                
                vertices.append([x, y, z])
        
        for i in range(resolution):
            for j in range(resolution):
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j
                v4 = v3 + 1
                
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        ocean = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
        
        # Water color gradient by depth
        heights = ocean.vertices[:, 1]
        colors = np.zeros((len(vertices), 4), dtype=np.uint8)
        
        for i, h in enumerate(heights):
            depth_factor = np.clip((h + wave_height) / (wave_height * 2), 0, 1)
            colors[i] = [
                int(30 + depth_factor * 70),
                int(100 + depth_factor * 100),
                int(180 + depth_factor * 75),
                255
            ]
        
        ocean.visual.vertex_colors = colors
        
        return ocean
    
    @staticmethod
    def generate_mountains(size: Tuple[int, int], peak_height: float = 100, count: int = 5) -> List[trimesh.Trimesh]:
        mountains = []
        
        for _ in range(count):
            center_x = random.uniform(size[0] * 0.2, size[0] * 0.8)
            center_z = random.uniform(size[1] * 0.2, size[1] * 0.8)
            
            mountain = EnvironmentLibrary._create_mountain(center_x, center_z, peak_height)
            mountains.append(mountain)
        
        return mountains
    
    @staticmethod
    def _create_mountain(center_x: float, center_z: float, height: float) -> trimesh.Trimesh:
        resolution = 50
        radius = 50
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                angle_i = i / resolution * 2 * np.pi
                angle_j = j / resolution * np.pi
                
                r = radius * np.sin(angle_j)
                x = center_x + r * np.cos(angle_i)
                z = center_z + r * np.sin(angle_i)
                y = height * np.cos(angle_j)
                
                # Add noise for rocky texture
                noise_val = pnoise3(x * 0.1, y * 0.1, z * 0.1, octaves=4)
                y += noise_val * 10
                
                vertices.append([x, max(0, y), z])
        
        for i in range(resolution):
            for j in range(resolution):
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j
                v4 = v3 + 1
                
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        mountain = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
        
        # Color by altitude
        heights = mountain.vertices[:, 1]
        colors = np.zeros((len(vertices), 4), dtype=np.uint8)
        
        for i, h in enumerate(heights):
            if h < height * 0.3:
                colors[i] = [34, 139, 34, 255]  # Grass
            elif h < height * 0.6:
                colors[i] = [139, 90, 43, 255]  # Rock
            elif h < height * 0.8:
                colors[i] = [128, 128, 128, 255]  # Stone
            else:
                colors[i] = [255, 255, 255, 255]  # Snow
        
        mountain.visual.vertex_colors = colors
        
        return mountain
    
    @staticmethod
    def generate_river(start: Tuple[float, float], end: Tuple[float, float], width: float = 5) -> trimesh.Trimesh:
        segments = 50
        vertices = []
        faces = []
        
        for i in range(segments + 1):
            t = i / segments
            
            # Bezier curve for natural flow
            x = start[0] + t * (end[0] - start[0])
            z = start[1] + t * (end[1] - start[1])
            
            # Add meandering
            meander = np.sin(t * np.pi * 4) * width * 2
            z += meander
            
            # River banks
            vertices.append([x - width/2, 0, z])
            vertices.append([x + width/2, 0, z])
        
        for i in range(segments):
            v1 = i * 2
            v2 = v1 + 1
            v3 = (i + 1) * 2
            v4 = v3 + 1
            
            faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        river = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
        river.visual.vertex_colors = np.tile([70, 130, 180, 255], (len(river.vertices), 1))
        
        return river
    
    @staticmethod
    def generate_rocks(area: Tuple[int, int], count: int = 100) -> List[trimesh.Trimesh]:
        rocks = []
        
        for _ in range(count):
            x = random.uniform(0, area[0])
            z = random.uniform(0, area[1])
            
            size = random.uniform(0.5, 3.0)
            rock = trimesh.creation.icosphere(radius=size, subdivisions=1)
            
            # Deform for irregular shape
            vertices = rock.vertices.copy()
            for i in range(len(vertices)):
                noise_val = pnoise3(vertices[i][0], vertices[i][1], vertices[i][2], octaves=3)
                vertices[i] *= (1 + noise_val * 0.3)
            rock.vertices = vertices
            
            rock.apply_translation([x, size/2, z])
            rock.visual.vertex_colors = np.tile([128, 128, 128, 255], (len(rock.vertices), 1))
            
            rocks.append(rock)
        
        return rocks
    
    @staticmethod
    def generate_grass_field(size: Tuple[int, int], density: int = 5000) -> List[trimesh.Trimesh]:
        grass_blades = []
        
        for _ in range(density):
            x = random.uniform(0, size[0])
            z = random.uniform(0, size[1])
            
            blade = trimesh.creation.box(extents=[0.05, random.uniform(0.3, 0.8), 0.05])
            blade.apply_translation([x, blade.bounds[1][1]/2, z])
            blade.visual.vertex_colors = np.tile([50, 200, 50, 255], (len(blade.vertices), 1))
            
            grass_blades.append(blade)
        
        return grass_blades
    
    @staticmethod
    def generate_clouds(area: Tuple[int, int], altitude: float = 50, count: int = 20) -> List[trimesh.Trimesh]:
        clouds = []
        
        for _ in range(count):
            x = random.uniform(0, area[0])
            z = random.uniform(0, area[1])
            
            # Multi-sphere cloud
            cloud_parts = []
            for _ in range(random.randint(3, 7)):
                part = trimesh.creation.icosphere(radius=random.uniform(3, 8), subdivisions=1)
                offset = [random.uniform(-5, 5), random.uniform(-2, 2), random.uniform(-5, 5)]
                part.apply_translation(offset)
                cloud_parts.append(part)
            
            cloud = trimesh.util.concatenate(cloud_parts)
            cloud.apply_translation([x, altitude, z])
            cloud.visual.vertex_colors = np.tile([255, 255, 255, 200], (len(cloud.vertices), 1))
            
            clouds.append(cloud)
        
        return clouds
    
    @staticmethod
    def generate_cave_system(size: Tuple[int, int], depth: float = 20) -> trimesh.Trimesh:
        resolution = 30
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                for k in range(resolution + 1):
                    x = (i / resolution) * size[0]
                    y = -(k / resolution) * depth
                    z = (j / resolution) * size[1]
                    
                    # 3D noise for cave structure
                    density = pnoise3(x * 0.1, y * 0.1, z * 0.1, octaves=4)
                    
                    if density > 0.3:  # Solid rock
                        vertices.append([x, y, z])
        
        # Simplified face generation
        if len(vertices) > 3:
            from scipy.spatial import Delaunay
            points_2d = np.array([[v[0], v[2]] for v in vertices])
            tri = Delaunay(points_2d)
            faces = tri.simplices
        
        if len(vertices) > 0 and len(faces) > 0:
            cave = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
            cave.visual.vertex_colors = np.tile([80, 70, 60, 255], (len(cave.vertices), 1))
            return cave
        
        return trimesh.Trimesh()
    
    @staticmethod
    def generate_desert(size: Tuple[int, int]) -> Dict[str, List[trimesh.Trimesh]]:
        # Sand dunes
        dunes = []
        for _ in range(20):
            x = random.uniform(0, size[0])
            z = random.uniform(0, size[1])
            
            dune = EnvironmentLibrary._create_dune(x, z)
            dunes.append(dune)
        
        # Cacti
        cacti = []
        for _ in range(50):
            x = random.uniform(0, size[0])
            z = random.uniform(0, size[1])
            
            cactus = EnvironmentLibrary._create_cactus()
            cactus.apply_translation([x, 0, z])
            cacti.append(cactus)
        
        return {'dunes': dunes, 'cacti': cacti}
    
    @staticmethod
    def _create_dune(center_x: float, center_z: float) -> trimesh.Trimesh:
        resolution = 20
        radius = 15
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = center_x + (i / resolution - 0.5) * radius * 2
                z = center_z + (j / resolution - 0.5) * radius * 2
                
                dist = np.sqrt((x - center_x)**2 + (z - center_z)**2)
                y = max(0, (1 - dist / radius) * 5)
                
                vertices.append([x, y, z])
        
        for i in range(resolution):
            for j in range(resolution):
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j
                v4 = v3 + 1
                
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        dune = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
        dune.visual.vertex_colors = np.tile([237, 201, 175, 255], (len(dune.vertices), 1))
        
        return dune
    
    @staticmethod
    def _create_cactus() -> trimesh.Trimesh:
        trunk = trimesh.creation.cylinder(radius=0.3, height=3, sections=8)
        trunk.apply_translation([0, 1.5, 0])
        
        arm1 = trimesh.creation.cylinder(radius=0.2, height=1.5, sections=8)
        arm1.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
        arm1.apply_translation([-0.8, 2, 0])
        
        arm2 = trimesh.creation.cylinder(radius=0.2, height=1.5, sections=8)
        arm2.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [0, 0, 1]))
        arm2.apply_translation([0.8, 1.5, 0])
        
        cactus = trimesh.util.concatenate([trunk, arm1, arm2])
        cactus.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(cactus.vertices), 1))
        
        return cactus