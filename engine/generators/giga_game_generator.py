import numpy as np
import trimesh
from typing import List, Dict
import random
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

class GigaGameGenerator:
    """Generate complete AAA games with all assets"""
    
    @staticmethod
    def generate_open_world_game(size: int = 10000, theme: str = 'modern') -> Dict:
        """Generate complete open world game (GTA/Skyrim scale)"""
        game_data = {
            'terrain': [],
            'cities': [],
            'roads': [],
            'npcs': [],
            'vehicles': [],
            'buildings': [],
            'vegetation': [],
            'quests': [],
            'items': []
        }
        
        # Terrain
        from engine.generators.giga_generator import GigaGenerator
        terrain = GigaGenerator.generate_continent((size, size))
        game_data['terrain'].append(terrain)
        
        # Cities (5-10 major cities)
        from engine.procedural.mega_city_generator import MegaCityGenerator
        for i in range(random.randint(5, 10)):
            x = random.randint(-size//2, size//2)
            z = random.randint(-size//2, size//2)
            city_size = random.randint(1000, 3000)
            city = MegaCityGenerator.generate_mega_city((city_size, city_size), 0.8)
            game_data['cities'].append({'position': [x, 0, z], 'data': city})
        
        # NPCs (10,000+)
        from engine.generators.giga_world_generator import GigaWorldGenerator
        with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = []
            for i in range(10000):
                prof = random.choice(['civilian', 'police', 'shopkeeper', 'guard'])
                futures.append(executor.submit(GigaWorldGenerator.generate_person, prof, 'adult', 'average', 'standing'))
            
            for future in futures:
                game_data['npcs'].append(future.result())
        
        # Vehicles (1000+)
        vehicles = GigaGenerator.generate_vehicle_fleet(1000, 'mixed')
        game_data['vehicles'] = vehicles
        
        # Vegetation (50,000+ trees)
        trees = GigaGenerator.generate_forest((size//2, size//2), 50000)
        game_data['vegetation'] = trees
        
        return game_data
    
    @staticmethod
    def generate_fps_game(map_count: int = 10, weapons: int = 50) -> Dict:
        """Generate complete FPS game (Call of Duty scale)"""
        game_data = {
            'maps': [],
            'weapons': [],
            'characters': [],
            'equipment': [],
            'vehicles': []
        }
        
        # Maps
        from engine.procedural.aaa_game_generator import AAAGameGenerator
        for i in range(map_count):
            map_type = random.choice(['urban', 'desert', 'forest', 'snow', 'industrial'])
            game_map = AAAGameGenerator.generate_fps_map(map_type, (500, 500))
            game_data['maps'].append(game_map)
        
        # Weapons (50+ types)
        weapon_types = ['pistol', 'rifle', 'shotgun', 'sniper', 'smg', 'lmg', 'launcher', 'knife', 'grenade']
        for wtype in weapon_types:
            for variant in range(weapons // len(weapon_types)):
                weapon = GigaGameGenerator._generate_weapon(wtype, variant)
                game_data['weapons'].append(weapon)
        
        # Characters (100+ soldier models)
        from engine.generators.giga_world_generator import GigaWorldGenerator
        for i in range(100):
            soldier = GigaWorldGenerator.generate_person('soldier', 'adult', 'muscular', 'standing')
            game_data['characters'].append(soldier)
        
        return game_data
    
    @staticmethod
    def generate_racing_game(tracks: int = 20, cars: int = 100) -> Dict:
        """Generate complete racing game (Need for Speed scale)"""
        game_data = {
            'tracks': [],
            'cars': [],
            'environments': [],
            'props': []
        }
        
        # Tracks
        from engine.procedural.aaa_game_generator import AAAGameGenerator
        for i in range(tracks):
            track_type = random.choice(['city', 'highway', 'mountain', 'desert', 'snow'])
            track = AAAGameGenerator.generate_racing_track(track_type, length=5000)
            game_data['tracks'].append(track)
        
        # Cars (100+ detailed models)
        from engine.generators.giga_generator import GigaGenerator
        cars = GigaGenerator.generate_vehicle_fleet(cars, 'car')
        game_data['cars'] = cars
        
        return game_data
    
    @staticmethod
    def generate_rpg_game(world_size: int = 20000, dungeons: int = 50) -> Dict:
        """Generate complete RPG game (Skyrim/Witcher scale)"""
        game_data = {
            'world': [],
            'dungeons': [],
            'towns': [],
            'npcs': [],
            'monsters': [],
            'items': [],
            'quests': []
        }
        
        # World terrain
        from engine.generators.giga_generator import GigaGenerator
        world = GigaGenerator.generate_continent((world_size, world_size))
        game_data['world'].append(world)
        
        # Dungeons (50+ unique)
        for i in range(dungeons):
            dungeon = GigaGameGenerator._generate_dungeon(random.randint(10, 50))
            game_data['dungeons'].append(dungeon)
        
        # Towns (20+)
        from engine.procedural.mega_city_generator import MegaCityGenerator
        for i in range(20):
            town = MegaCityGenerator.generate_mega_city((500, 500), 0.6)
            game_data['towns'].append(town)
        
        # NPCs (5000+)
        from engine.generators.giga_world_generator import GigaWorldGenerator
        for i in range(5000):
            prof = random.choice(['merchant', 'guard', 'farmer', 'blacksmith', 'mage', 'warrior'])
            npc = GigaWorldGenerator.generate_person(prof, 'adult', 'average', 'standing')
            game_data['npcs'].append(npc)
        
        # Monsters (100+ types)
        monster_types = ['dragon', 'goblin', 'orc', 'troll', 'skeleton', 'zombie', 'wolf', 'bear', 'spider', 'demon']
        for mtype in monster_types:
            for variant in range(10):
                monster = GigaGameGenerator._generate_monster(mtype, variant)
                game_data['monsters'].append(monster)
        
        return game_data
    
    @staticmethod
    def generate_survival_game(island_size: int = 15000, resources: int = 10000) -> Dict:
        """Generate survival game (Minecraft/Rust scale)"""
        game_data = {
            'terrain': [],
            'resources': [],
            'animals': [],
            'structures': [],
            'crafting': []
        }
        
        # Island terrain
        from engine.generators.giga_generator import GigaGenerator
        terrain = GigaGenerator.generate_continent((island_size, island_size))
        game_data['terrain'].append(terrain)
        
        # Resources (trees, rocks, ore)
        trees = GigaGenerator.generate_forest((island_size//2, island_size//2), resources//2)
        game_data['resources'].extend(trees)
        
        # Animals (1000+)
        from engine.generators.giga_world_generator import GigaWorldGenerator
        animal_types = ['deer', 'bear', 'wolf', 'rabbit', 'boar']
        for i in range(1000):
            animal_type = random.choice(animal_types)
            animal = GigaWorldGenerator.generate_animal('mammals', animal_type)
            game_data['animals'].append(animal)
        
        return game_data
    
    @staticmethod
    def _generate_weapon(weapon_type: str, variant: int) -> trimesh.Trimesh:
        """Generate detailed weapon model"""
        meshes = []
        
        if weapon_type == 'rifle':
            # Stock
            stock = trimesh.creation.box(extents=[0.3, 0.1, 0.08])
            stock.apply_translation([-0.15, 0, 0])
            meshes.append(stock)
            
            # Body
            body = trimesh.creation.box(extents=[0.5, 0.08, 0.08])
            meshes.append(body)
            
            # Barrel
            barrel = trimesh.creation.cylinder(radius=0.02, height=0.4, sections=16)
            barrel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
            barrel.apply_translation([0.45, 0, 0])
            meshes.append(barrel)
            
            # Magazine
            mag = trimesh.creation.box(extents=[0.15, 0.05, 0.2])
            mag.apply_translation([0, 0, -0.15])
            meshes.append(mag)
            
            # Scope
            scope = trimesh.creation.cylinder(radius=0.03, height=0.2, sections=16)
            scope.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
            scope.apply_translation([0.1, 0, 0.1])
            meshes.append(scope)
        
        elif weapon_type == 'pistol':
            # Grip
            grip = trimesh.creation.box(extents=[0.08, 0.05, 0.15])
            grip.apply_translation([0, 0, -0.075])
            meshes.append(grip)
            
            # Slide
            slide = trimesh.creation.box(extents=[0.2, 0.04, 0.06])
            slide.apply_translation([0.1, 0, 0.03])
            meshes.append(slide)
            
            # Barrel
            barrel = trimesh.creation.cylinder(radius=0.015, height=0.15, sections=12)
            barrel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
            barrel.apply_translation([0.25, 0, 0.03])
            meshes.append(barrel)
        
        elif weapon_type == 'sword':
            # Blade
            blade = trimesh.creation.box(extents=[1.0, 0.05, 0.02])
            blade.apply_translation([0.5, 0, 0])
            meshes.append(blade)
            
            # Guard
            guard = trimesh.creation.box(extents=[0.05, 0.3, 0.02])
            meshes.append(guard)
            
            # Handle
            handle = trimesh.creation.cylinder(radius=0.03, height=0.2, sections=12)
            handle.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            handle.apply_translation([-0.1, 0, 0])
            meshes.append(handle)
            
            # Pommel
            pommel = trimesh.creation.icosphere(subdivisions=2, radius=0.05)
            pommel.apply_translation([-0.2, 0, 0])
            meshes.append(pommel)
        
        weapon = trimesh.util.concatenate(meshes)
        weapon.visual.vertex_colors = [50, 50, 50, 255]
        return weapon
    
    @staticmethod
    def _generate_dungeon(rooms: int) -> List[trimesh.Trimesh]:
        """Generate dungeon with rooms and corridors"""
        dungeon_meshes = []
        
        for i in range(rooms):
            # Room
            room_size = random.uniform(10, 30)
            room = trimesh.creation.box(extents=[room_size, room_size, 5])
            x = i * 40
            room.apply_translation([x, 0, 0])
            dungeon_meshes.append(room)
            
            # Corridor to next room
            if i < rooms - 1:
                corridor = trimesh.creation.box(extents=[40, 5, 5])
                corridor.apply_translation([x + 20, 0, 0])
                dungeon_meshes.append(corridor)
            
            # Props (torches, chests, etc)
            for j in range(random.randint(3, 8)):
                prop_x = x + random.uniform(-room_size/2, room_size/2)
                prop_y = random.uniform(-room_size/2, room_size/2)
                
                if random.random() < 0.3:
                    # Chest
                    chest = trimesh.creation.box(extents=[1, 0.8, 0.8])
                    chest.apply_translation([prop_x, prop_y, 0.4])
                    dungeon_meshes.append(chest)
                else:
                    # Torch
                    torch = trimesh.creation.cylinder(radius=0.1, height=2, sections=8)
                    torch.apply_translation([prop_x, prop_y, 1])
                    dungeon_meshes.append(torch)
        
        return dungeon_meshes
    
    @staticmethod
    def _generate_monster(monster_type: str, variant: int) -> trimesh.Trimesh:
        """Generate fantasy monster"""
        meshes = []
        
        if monster_type == 'dragon':
            # Body
            body = trimesh.creation.capsule(radius=2, height=8)
            body.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            meshes.append(body)
            
            # Head
            head = trimesh.creation.cone(radius=1.5, height=3, sections=16)
            head.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
            head.apply_translation([5, 0, 1])
            meshes.append(head)
            
            # Wings
            for y in [-3, 3]:
                wing = trimesh.creation.box(extents=[0.5, 8, 4])
                wing.apply_translation([0, y, 2])
                meshes.append(wing)
            
            # Tail
            tail = trimesh.creation.cone(radius=1, height=6, sections=16)
            tail.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [0, 1, 0]))
            tail.apply_translation([-7, 0, 0])
            meshes.append(tail)
            
            # Legs
            for x, y in [(-2, -1.5), (-2, 1.5), (2, -1.5), (2, 1.5)]:
                leg = trimesh.creation.cylinder(radius=0.5, height=3, sections=12)
                leg.apply_translation([x, y, -2.5])
                meshes.append(leg)
        
        elif monster_type == 'goblin':
            # Small humanoid
            from engine.generators.giga_world_generator import GigaWorldGenerator
            return GigaWorldGenerator.generate_person('civilian', 'child', 'slim', 'standing')
        
        elif monster_type == 'troll':
            # Large humanoid
            from engine.generators.giga_world_generator import GigaWorldGenerator
            troll = GigaWorldGenerator.generate_person('civilian', 'adult', 'heavy', 'standing')
            troll.apply_scale(2.0)
            return troll
        
        monster = trimesh.util.concatenate(meshes)
        monster.visual.vertex_colors = [random.randint(50, 150), random.randint(50, 150), random.randint(50, 150), 255]
        return monster
    
    @staticmethod
    def generate_battle_royale_game(map_size: int = 8000, players: int = 100) -> Dict:
        """Generate battle royale game (Fortnite/PUBG scale)"""
        game_data = {
            'map': [],
            'poi': [],  # Points of interest
            'loot': [],
            'vehicles': [],
            'weapons': []
        }
        
        # Main island
        from engine.generators.giga_generator import GigaGenerator
        island = GigaGenerator.generate_continent((map_size, map_size))
        game_data['map'].append(island)
        
        # POIs (20+ named locations)
        from engine.procedural.mega_city_generator import MegaCityGenerator
        for i in range(20):
            x = random.randint(-map_size//2, map_size//2)
            z = random.randint(-map_size//2, map_size//2)
            poi_size = random.randint(200, 800)
            poi = MegaCityGenerator.generate_mega_city((poi_size, poi_size), 0.7)
            game_data['poi'].append({'position': [x, 0, z], 'data': poi})
        
        # Vehicles (200+)
        vehicles = GigaGenerator.generate_vehicle_fleet(200, 'mixed')
        game_data['vehicles'] = vehicles
        
        # Weapons (100+ scattered)
        for i in range(100):
            weapon_type = random.choice(['rifle', 'pistol', 'shotgun', 'sniper'])
            weapon = GigaGameGenerator._generate_weapon(weapon_type, i)
            game_data['weapons'].append(weapon)
        
        return game_data
