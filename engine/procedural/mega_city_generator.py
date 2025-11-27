import numpy as np
import trimesh
from typing import List, Dict, Tuple
import random
from noise import pnoise2

class MegaCityGenerator:
    """Generate GTA 6 / Bad Guys style massive cities"""
    
    @staticmethod
    def generate_mega_city(size: Tuple[int, int], population_density: float = 0.9) -> Dict:
        """Generate complete city with everything"""
        
        # Districts
        districts = MegaCityGenerator._create_districts(size)
        
        # Infrastructure
        roads = MegaCityGenerator._generate_road_network(size, grid_size=20)
        highways = MegaCityGenerator._generate_highways(size)
        bridges = MegaCityGenerator._generate_bridges(size)
        
        # Buildings by district
        skyscrapers = MegaCityGenerator._generate_skyscrapers(districts['downtown'], 50)
        apartments = MegaCityGenerator._generate_apartments(districts['residential'], 200)
        houses = MegaCityGenerator._generate_houses(districts['suburban'], 500)
        shops = MegaCityGenerator._generate_shops(districts['commercial'], 100)
        factories = MegaCityGenerator._generate_industrial(districts['industrial'], 30)
        
        # Urban furniture
        streetlights = MegaCityGenerator._generate_streetlights(roads, spacing=10)
        traffic_lights = MegaCityGenerator._generate_traffic_lights(roads, spacing=50)
        signs = MegaCityGenerator._generate_signs(roads, 500)
        benches = MegaCityGenerator._generate_benches(1000)
        trash_cans = MegaCityGenerator._generate_trash_cans(800)
        
        # Vegetation
        trees = MegaCityGenerator._generate_urban_trees(size, 2000)
        parks = MegaCityGenerator._generate_parks(size, 10)
        
        # Vehicles
        cars = MegaCityGenerator._generate_traffic(roads, 500)
        buses = MegaCityGenerator._generate_buses(roads, 50)
        
        # People
        pedestrians = MegaCityGenerator._generate_pedestrians(roads, 1000)
        
        return {
            'roads': roads,
            'highways': highways,
            'bridges': bridges,
            'skyscrapers': skyscrapers,
            'apartments': apartments,
            'houses': houses,
            'shops': shops,
            'factories': factories,
            'streetlights': streetlights,
            'traffic_lights': traffic_lights,
            'signs': signs,
            'benches': benches,
            'trash_cans': trash_cans,
            'trees': trees,
            'parks': parks,
            'cars': cars,
            'buses': buses,
            'pedestrians': pedestrians
        }
    
    @staticmethod
    def _create_districts(size: Tuple[int, int]) -> Dict:
        center_x, center_z = size[0] / 2, size[1] / 2
        
        return {
            'downtown': (center_x - 100, center_z - 100, center_x + 100, center_z + 100),
            'residential': (center_x - 300, center_z - 300, center_x - 100, center_z + 300),
            'commercial': (center_x + 100, center_z - 200, center_x + 300, center_z + 200),
            'industrial': (center_x - 300, center_z + 100, center_x - 100, center_z + 300),
            'suburban': (center_x + 100, center_z + 100, center_x + 400, center_z + 400)
        }
    
    @staticmethod
    def _generate_road_network(size: Tuple[int, int], grid_size: int) -> List[trimesh.Trimesh]:
        roads = []
        road_width = 8
        
        for x in range(0, size[0], grid_size):
            road = trimesh.creation.box(extents=[size[0], 0.2, road_width])
            road.apply_translation([size[0]/2, 0, x])
            road.visual.vertex_colors = np.tile([40, 40, 40, 255], (len(road.vertices), 1))
            roads.append(road)
        
        for z in range(0, size[1], grid_size):
            road = trimesh.creation.box(extents=[road_width, 0.2, size[1]])
            road.apply_translation([z, 0, size[1]/2])
            road.visual.vertex_colors = np.tile([40, 40, 40, 255], (len(road.vertices), 1))
            roads.append(road)
        
        return roads
    
    @staticmethod
    def _generate_highways(size: Tuple[int, int]) -> List[trimesh.Trimesh]:
        highways = []
        
        # Main highway
        highway = trimesh.creation.box(extents=[size[0], 0.5, 15])
        highway.apply_translation([size[0]/2, 2, size[1]/2])
        highway.visual.vertex_colors = np.tile([60, 60, 60, 255], (len(highway.vertices), 1))
        highways.append(highway)
        
        # Support pillars
        for x in range(0, size[0], 30):
            pillar = trimesh.creation.cylinder(radius=1, height=2)
            pillar.apply_translation([x, 1, size[1]/2])
            pillar.visual.vertex_colors = np.tile([100, 100, 100, 255], (len(pillar.vertices), 1))
            highways.append(pillar)
        
        return highways
    
    @staticmethod
    def _generate_bridges(size: Tuple[int, int]) -> List[trimesh.Trimesh]:
        bridges = []
        
        bridge_deck = trimesh.creation.box(extents=[100, 1, 20])
        bridge_deck.apply_translation([size[0]/2, 5, size[1]/4])
        bridge_deck.visual.vertex_colors = np.tile([150, 150, 150, 255], (len(bridge_deck.vertices), 1))
        bridges.append(bridge_deck)
        
        # Cables
        for i in range(5):
            cable = trimesh.creation.cylinder(radius=0.2, height=10)
            cable.apply_translation([size[0]/2 - 40 + i*20, 10, size[1]/4])
            cable.visual.vertex_colors = np.tile([200, 200, 200, 255], (len(cable.vertices), 1))
            bridges.append(cable)
        
        return bridges
    
    @staticmethod
    def _generate_skyscrapers(district: Tuple, count: int) -> List[trimesh.Trimesh]:
        buildings = []
        x1, z1, x2, z2 = district
        
        for _ in range(count):
            x = random.uniform(x1, x2)
            z = random.uniform(z1, z2)
            
            width = random.uniform(15, 30)
            depth = random.uniform(15, 30)
            height = random.uniform(80, 200)
            
            building = trimesh.creation.box(extents=[width, height, depth])
            building.apply_translation([x, height/2, z])
            
            # Windows pattern
            color = [random.randint(100, 150), random.randint(100, 150), random.randint(100, 150), 255]
            building.visual.vertex_colors = np.tile(color, (len(building.vertices), 1))
            
            buildings.append(building)
        
        return buildings
    
    @staticmethod
    def _generate_apartments(district: Tuple, count: int) -> List[trimesh.Trimesh]:
        buildings = []
        x1, z1, x2, z2 = district
        
        for _ in range(count):
            x = random.uniform(x1, x2)
            z = random.uniform(z1, z2)
            
            width = random.uniform(10, 20)
            depth = random.uniform(10, 20)
            height = random.uniform(20, 50)
            
            building = trimesh.creation.box(extents=[width, height, depth])
            building.apply_translation([x, height/2, z])
            
            color = [random.randint(150, 200), random.randint(150, 200), random.randint(150, 200), 255]
            building.visual.vertex_colors = np.tile(color, (len(building.vertices), 1))
            
            buildings.append(building)
        
        return buildings
    
    @staticmethod
    def _generate_houses(district: Tuple, count: int) -> List[trimesh.Trimesh]:
        houses = []
        x1, z1, x2, z2 = district
        
        for _ in range(count):
            x = random.uniform(x1, x2)
            z = random.uniform(z1, z2)
            
            width = random.uniform(6, 12)
            depth = random.uniform(6, 12)
            height = random.uniform(5, 8)
            
            house = trimesh.creation.box(extents=[width, height, depth])
            house.apply_translation([x, height/2, z])
            
            # Roof
            roof_vertices = np.array([
                [-width/2, height/2, -depth/2],
                [width/2, height/2, -depth/2],
                [width/2, height/2, depth/2],
                [-width/2, height/2, depth/2],
                [0, height/2 + 2, 0]
            ])
            roof_vertices[:, 0] += x
            roof_vertices[:, 2] += z
            
            roof_faces = np.array([[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]])
            roof = trimesh.Trimesh(vertices=roof_vertices, faces=roof_faces)
            
            combined = trimesh.util.concatenate([house, roof])
            combined.visual.vertex_colors = np.tile([200, 180, 160, 255], (len(combined.vertices), 1))
            
            houses.append(combined)
        
        return houses
    
    @staticmethod
    def _generate_shops(district: Tuple, count: int) -> List[trimesh.Trimesh]:
        shops = []
        x1, z1, x2, z2 = district
        
        for _ in range(count):
            x = random.uniform(x1, x2)
            z = random.uniform(z1, z2)
            
            shop = trimesh.creation.box(extents=[8, 6, 10])
            shop.apply_translation([x, 3, z])
            shop.visual.vertex_colors = np.tile([220, 200, 180, 255], (len(shop.vertices), 1))
            
            shops.append(shop)
        
        return shops
    
    @staticmethod
    def _generate_industrial(district: Tuple, count: int) -> List[trimesh.Trimesh]:
        factories = []
        x1, z1, x2, z2 = district
        
        for _ in range(count):
            x = random.uniform(x1, x2)
            z = random.uniform(z1, z2)
            
            factory = trimesh.creation.box(extents=[30, 15, 40])
            factory.apply_translation([x, 7.5, z])
            factory.visual.vertex_colors = np.tile([120, 120, 120, 255], (len(factory.vertices), 1))
            
            # Chimney
            chimney = trimesh.creation.cylinder(radius=2, height=20)
            chimney.apply_translation([x, 25, z])
            chimney.visual.vertex_colors = np.tile([100, 100, 100, 255], (len(chimney.vertices), 1))
            
            combined = trimesh.util.concatenate([factory, chimney])
            factories.append(combined)
        
        return factories
    
    @staticmethod
    def _generate_streetlights(roads: List, spacing: int) -> List[trimesh.Trimesh]:
        lights = []
        
        for i in range(0, len(roads), spacing):
            pole = trimesh.creation.cylinder(radius=0.1, height=5)
            pole.apply_translation([i*10, 2.5, 0])
            
            lamp = trimesh.creation.icosphere(radius=0.3, subdivisions=1)
            lamp.apply_translation([i*10, 5, 0])
            
            light = trimesh.util.concatenate([pole, lamp])
            light.visual.vertex_colors = np.tile([200, 200, 200, 255], (len(light.vertices), 1))
            lights.append(light)
        
        return lights
    
    @staticmethod
    def _generate_traffic_lights(roads: List, spacing: int) -> List[trimesh.Trimesh]:
        lights = []
        
        for i in range(0, len(roads), spacing):
            pole = trimesh.creation.cylinder(radius=0.15, height=4)
            pole.apply_translation([i*10, 2, 0])
            
            box = trimesh.creation.box(extents=[0.3, 0.8, 0.3])
            box.apply_translation([i*10, 4.5, 0])
            
            traffic_light = trimesh.util.concatenate([pole, box])
            traffic_light.visual.vertex_colors = np.tile([50, 50, 50, 255], (len(traffic_light.vertices), 1))
            lights.append(traffic_light)
        
        return lights
    
    @staticmethod
    def _generate_signs(roads: List, count: int) -> List[trimesh.Trimesh]:
        signs = []
        
        for _ in range(count):
            pole = trimesh.creation.cylinder(radius=0.05, height=3)
            pole.apply_translation([random.uniform(0, 1000), 1.5, random.uniform(0, 1000)])
            
            sign_board = trimesh.creation.box(extents=[1, 0.8, 0.1])
            sign_board.apply_translation([random.uniform(0, 1000), 3, random.uniform(0, 1000)])
            
            sign = trimesh.util.concatenate([pole, sign_board])
            sign.visual.vertex_colors = np.tile([200, 200, 200, 255], (len(sign.vertices), 1))
            signs.append(sign)
        
        return signs
    
    @staticmethod
    def _generate_benches(count: int) -> List[trimesh.Trimesh]:
        benches = []
        
        for _ in range(count):
            bench = trimesh.creation.box(extents=[1.5, 0.5, 0.5])
            bench.apply_translation([random.uniform(0, 1000), 0.25, random.uniform(0, 1000)])
            bench.visual.vertex_colors = np.tile([139, 69, 19, 255], (len(bench.vertices), 1))
            benches.append(bench)
        
        return benches
    
    @staticmethod
    def _generate_trash_cans(count: int) -> List[trimesh.Trimesh]:
        cans = []
        
        for _ in range(count):
            can = trimesh.creation.cylinder(radius=0.3, height=0.8)
            can.apply_translation([random.uniform(0, 1000), 0.4, random.uniform(0, 1000)])
            can.visual.vertex_colors = np.tile([100, 100, 100, 255], (len(can.vertices), 1))
            cans.append(can)
        
        return cans
    
    @staticmethod
    def _generate_urban_trees(size: Tuple[int, int], count: int) -> List[trimesh.Trimesh]:
        trees = []
        
        for _ in range(count):
            trunk = trimesh.creation.cylinder(radius=0.3, height=5)
            trunk.apply_translation([random.uniform(0, size[0]), 2.5, random.uniform(0, size[1])])
            
            crown = trimesh.creation.icosphere(radius=2, subdivisions=1)
            crown.apply_translation([random.uniform(0, size[0]), 6, random.uniform(0, size[1])])
            
            tree = trimesh.util.concatenate([trunk, crown])
            tree.visual.vertex_colors = np.tile([34, 139, 34, 255], (len(tree.vertices), 1))
            trees.append(tree)
        
        return trees
    
    @staticmethod
    def _generate_parks(size: Tuple[int, int], count: int) -> List[trimesh.Trimesh]:
        parks = []
        
        for _ in range(count):
            park_size = random.uniform(30, 60)
            park = trimesh.creation.box(extents=[park_size, 0.1, park_size])
            park.apply_translation([random.uniform(0, size[0]), 0.05, random.uniform(0, size[1])])
            park.visual.vertex_colors = np.tile([50, 200, 50, 255], (len(park.vertices), 1))
            parks.append(park)
        
        return parks
    
    @staticmethod
    def _generate_traffic(roads: List, count: int) -> List[trimesh.Trimesh]:
        cars = []
        
        for _ in range(count):
            body = trimesh.creation.box(extents=[4, 1.5, 2])
            body.apply_translation([random.uniform(0, 1000), 0.75, random.uniform(0, 1000)])
            
            color = [random.randint(50, 255), random.randint(50, 255), random.randint(50, 255), 255]
            body.visual.vertex_colors = np.tile(color, (len(body.vertices), 1))
            cars.append(body)
        
        return cars
    
    @staticmethod
    def _generate_buses(roads: List, count: int) -> List[trimesh.Trimesh]:
        buses = []
        
        for _ in range(count):
            bus = trimesh.creation.box(extents=[10, 3, 2.5])
            bus.apply_translation([random.uniform(0, 1000), 1.5, random.uniform(0, 1000)])
            bus.visual.vertex_colors = np.tile([255, 200, 0, 255], (len(bus.vertices), 1))
            buses.append(bus)
        
        return buses
    
    @staticmethod
    def _generate_pedestrians(roads: List, count: int) -> List[trimesh.Trimesh]:
        people = []
        
        for _ in range(count):
            body = trimesh.creation.box(extents=[0.5, 1.7, 0.3])
            body.apply_translation([random.uniform(0, 1000), 0.85, random.uniform(0, 1000)])
            
            head = trimesh.creation.icosphere(radius=0.15, subdivisions=1)
            head.apply_translation([random.uniform(0, 1000), 1.85, random.uniform(0, 1000)])
            
            person = trimesh.util.concatenate([body, head])
            person.visual.vertex_colors = np.tile([random.randint(100, 200), random.randint(100, 200), random.randint(100, 200), 255], (len(person.vertices), 1))
            people.append(person)
        
        return people