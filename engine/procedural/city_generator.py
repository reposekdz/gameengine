import numpy as np
import trimesh
from typing import List, Dict, Tuple
from noise import pnoise2
import random

class CityGenerator:
    def __init__(self, size: Tuple[int, int] = (100, 100)):
        self.size = size
        self.buildings = []
        self.roads = []
        self.landmarks = []
        
    def generate_city(self, density: float = 0.7, style: str = 'modern') -> List[trimesh.Trimesh]:
        grid_size = 10
        city_meshes = []
        
        # Generate road network
        roads = self._generate_roads(grid_size)
        city_meshes.extend(roads)
        
        # Generate buildings
        for x in range(0, self.size[0], grid_size):
            for z in range(0, self.size[1], grid_size):
                if random.random() < density:
                    if random.random() < 0.05:  # 5% landmarks
                        building = self._generate_landmark(x, z, style)
                    else:
                        building = self._generate_building(x, z, style)
                    city_meshes.append(building)
        
        # Generate parks
        for _ in range(int(self.size[0] * self.size[1] / 1000)):
            park = self._generate_park()
            city_meshes.append(park)
        
        return city_meshes
    
    def _generate_building(self, x: float, z: float, style: str) -> trimesh.Trimesh:
        width = random.uniform(5, 15)
        depth = random.uniform(5, 15)
        height = random.uniform(10, 100)
        
        if style == 'modern':
            building = trimesh.creation.box(extents=[width, height, depth])
        elif style == 'classic':
            building = self._create_classic_building(width, height, depth)
        else:
            building = trimesh.creation.box(extents=[width, height, depth])
        
        building.apply_translation([x, height/2, z])
        
        # Add color
        color = [random.randint(100, 200), random.randint(100, 200), random.randint(100, 200), 255]
        building.visual.vertex_colors = np.tile(color, (len(building.vertices), 1))
        
        return building
    
    def _generate_landmark(self, x: float, z: float, style: str) -> trimesh.Trimesh:
        height = random.uniform(150, 300)
        radius = random.uniform(10, 20)
        
        landmark = trimesh.creation.cylinder(radius=radius, height=height, sections=8)
        landmark.apply_translation([x, height/2, z])
        
        color = [255, 215, 0, 255]  # Gold
        landmark.visual.vertex_colors = np.tile(color, (len(landmark.vertices), 1))
        
        return landmark
    
    def _create_classic_building(self, width: float, height: float, depth: float) -> trimesh.Trimesh:
        base = trimesh.creation.box(extents=[width, height * 0.8, depth])
        
        roof_vertices = np.array([
            [-width/2, height*0.4, -depth/2],
            [width/2, height*0.4, -depth/2],
            [width/2, height*0.4, depth/2],
            [-width/2, height*0.4, depth/2],
            [0, height*0.6, 0]
        ])
        
        roof_faces = np.array([
            [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]
        ])
        
        roof = trimesh.Trimesh(vertices=roof_vertices, faces=roof_faces)
        
        return trimesh.util.concatenate([base, roof])
    
    def _generate_roads(self, grid_size: int) -> List[trimesh.Trimesh]:
        roads = []
        road_width = 3
        
        # Horizontal roads
        for z in range(0, self.size[1], grid_size):
            road = trimesh.creation.box(extents=[self.size[0], 0.1, road_width])
            road.apply_translation([self.size[0]/2, 0, z])
            road.visual.vertex_colors = np.tile([50, 50, 50, 255], (len(road.vertices), 1))
            roads.append(road)
        
        # Vertical roads
        for x in range(0, self.size[0], grid_size):
            road = trimesh.creation.box(extents=[road_width, 0.1, self.size[1]])
            road.apply_translation([x, 0, self.size[1]/2])
            road.visual.vertex_colors = np.tile([50, 50, 50, 255], (len(road.vertices), 1))
            roads.append(road)
        
        return roads
    
    def _generate_park(self) -> trimesh.Trimesh:
        x = random.uniform(0, self.size[0])
        z = random.uniform(0, self.size[1])
        size = random.uniform(10, 30)
        
        park = trimesh.creation.box(extents=[size, 0.2, size])
        park.apply_translation([x, 0.1, z])
        park.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(park.vertices), 1))
        
        return park

class TerrainGenerator:
    @staticmethod
    def generate_terrain(size: int = 200, resolution: int = 100, height_scale: float = 20) -> trimesh.Trimesh:
        vertices = []
        faces = []
        
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = (i / resolution - 0.5) * size
                z = (j / resolution - 0.5) * size
                
                y = pnoise2(x * 0.05, z * 0.05, octaves=6) * height_scale
                
                vertices.append([x, y, z])
        
        for i in range(resolution):
            for j in range(resolution):
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j
                v4 = v3 + 1
                
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        terrain = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
        
        # Color based on height
        heights = terrain.vertices[:, 1]
        colors = np.zeros((len(vertices), 4), dtype=np.uint8)
        
        for i, h in enumerate(heights):
            if h < 0:
                colors[i] = [70, 130, 180, 255]  # Water
            elif h < 5:
                colors[i] = [34, 139, 34, 255]  # Grass
            elif h < 10:
                colors[i] = [139, 69, 19, 255]  # Dirt
            else:
                colors[i] = [128, 128, 128, 255]  # Rock
        
        terrain.visual.vertex_colors = colors
        
        return terrain