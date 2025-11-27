import numpy as np
import trimesh
from typing import List, Dict, Tuple
import random

class AAAGameGenerator:
    """Generate AAA-quality game assets and environments"""
    
    @staticmethod
    def generate_racing_track(length: float = 1000, width: float = 20) -> Dict:
        segments = 50
        track_meshes = []
        
        for i in range(segments):
            t = i / segments
            
            # Curved track path
            x = t * length
            z = np.sin(t * 4 * np.pi) * 50
            y = np.cos(t * 2 * np.pi) * 10
            
            segment = trimesh.creation.box(extents=[length/segments, 0.5, width])
            segment.apply_translation([x, y, z])
            segment.visual.vertex_colors = np.tile([40, 40, 40, 255], (len(segment.vertices), 1))
            track_meshes.append(segment)
        
        # Barriers
        barriers = []
        for i in range(segments):
            t = i / segments
            x = t * length
            z_left = np.sin(t * 4 * np.pi) * 50 - width/2
            z_right = np.sin(t * 4 * np.pi) * 50 + width/2
            y = np.cos(t * 2 * np.pi) * 10
            
            barrier_l = trimesh.creation.box(extents=[length/segments, 2, 1])
            barrier_l.apply_translation([x, y+1, z_left])
            barrier_l.visual.vertex_colors = np.tile([255, 0, 0, 255], (len(barrier_l.vertices), 1))
            
            barrier_r = trimesh.creation.box(extents=[length/segments, 2, 1])
            barrier_r.apply_translation([x, y+1, z_right])
            barrier_r.visual.vertex_colors = np.tile([255, 0, 0, 255], (len(barrier_r.vertices), 1))
            
            barriers.extend([barrier_l, barrier_r])
        
        return {
            'track': track_meshes,
            'barriers': barriers,
            'checkpoints': AAAGameGenerator._generate_checkpoints(segments, length, width)
        }
    
    @staticmethod
    def generate_fps_map(size: Tuple[int, int] = (200, 200)) -> Dict:
        """Generate FPS map like Call of Duty"""
        buildings = []
        cover_objects = []
        spawn_points = []
        
        # Generate buildings
        for _ in range(20):
            x = random.uniform(-size[0]/2, size[0]/2)
            z = random.uniform(-size[1]/2, size[1]/2)
            width = random.uniform(10, 30)
            height = random.uniform(15, 50)
            depth = random.uniform(10, 30)
            
            building = trimesh.creation.box(extents=[width, height, depth])
            building.apply_translation([x, height/2, z])
            building.visual.vertex_colors = np.tile([100, 100, 100, 255], (len(building.vertices), 1))
            buildings.append(building)
        
        # Generate cover objects
        for _ in range(50):
            x = random.uniform(-size[0]/2, size[0]/2)
            z = random.uniform(-size[1]/2, size[1]/2)
            
            cover = trimesh.creation.box(extents=[2, 1.5, 3])
            cover.apply_translation([x, 0.75, z])
            cover.visual.vertex_colors = np.tile([139, 69, 19, 255], (len(cover.vertices), 1))
            cover_objects.append(cover)
        
        # Spawn points
        for _ in range(10):
            spawn_points.append([
                random.uniform(-size[0]/2, size[0]/2),
                1,
                random.uniform(-size[1]/2, size[1]/2)
            ])
        
        # Ground
        ground = trimesh.creation.box(extents=[size[0], 0.1, size[1]])
        ground.visual.vertex_colors = np.tile([50, 100, 50, 255], (len(ground.vertices), 1))
        
        return {
            'buildings': buildings,
            'cover': cover_objects,
            'ground': ground,
            'spawn_points': spawn_points
        }
    
    @staticmethod
    def generate_fighting_arena(size: float = 50) -> Dict:
        """Generate fighting arena like Mortal Kombat"""
        # Arena floor
        floor = trimesh.creation.box(extents=[size, 1, size])
        floor.visual.vertex_colors = np.tile([80, 80, 80, 255], (len(floor.vertices), 1))
        
        # Walls
        walls = []
        wall_height = 10
        
        # Four walls
        positions = [
            ([0, wall_height/2, size/2], [size, wall_height, 1]),
            ([0, wall_height/2, -size/2], [size, wall_height, 1]),
            ([size/2, wall_height/2, 0], [1, wall_height, size]),
            ([-size/2, wall_height/2, 0], [1, wall_height, size])
        ]
        
        for pos, extents in positions:
            wall = trimesh.creation.box(extents=extents)
            wall.apply_translation(pos)
            wall.visual.vertex_colors = np.tile([60, 60, 60, 255], (len(wall.vertices), 1))
            walls.append(wall)
        
        # Pillars
        pillars = []
        pillar_positions = [
            [size/3, 0, size/3],
            [-size/3, 0, size/3],
            [size/3, 0, -size/3],
            [-size/3, 0, -size/3]
        ]
        
        for pos in pillar_positions:
            pillar = trimesh.creation.cylinder(radius=2, height=15)
            pillar.apply_translation([pos[0], 7.5, pos[2]])
            pillar.visual.vertex_colors = np.tile([100, 50, 50, 255], (len(pillar.vertices), 1))
            pillars.append(pillar)
        
        return {
            'floor': floor,
            'walls': walls,
            'pillars': pillars,
            'spawn_points': [[0, 1, size/4], [0, 1, -size/4]]
        }
    
    @staticmethod
    def generate_vehicle(vehicle_type: str = 'car') -> trimesh.Trimesh:
        """Generate detailed vehicle"""
        if vehicle_type == 'car':
            # Body
            body = trimesh.creation.box(extents=[4, 1.5, 2])
            body.apply_translation([0, 1, 0])
            
            # Cabin
            cabin = trimesh.creation.box(extents=[2, 1, 1.8])
            cabin.apply_translation([0, 2, 0])
            
            # Wheels
            wheels = []
            wheel_positions = [[1.5, 0.5, 1], [1.5, 0.5, -1], [-1.5, 0.5, 1], [-1.5, 0.5, -1]]
            
            for pos in wheel_positions:
                wheel = trimesh.creation.cylinder(radius=0.5, height=0.3)
                wheel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
                wheel.apply_translation(pos)
                wheels.append(wheel)
            
            vehicle = trimesh.util.concatenate([body, cabin] + wheels)
            vehicle.visual.vertex_colors = np.tile([200, 0, 0, 255], (len(vehicle.vertices), 1))
            
            return vehicle
        
        elif vehicle_type == 'tank':
            # Tank body
            body = trimesh.creation.box(extents=[6, 2, 3])
            body.apply_translation([0, 1.5, 0])
            
            # Turret
            turret = trimesh.creation.cylinder(radius=1.5, height=1)
            turret.apply_translation([0, 3, 0])
            
            # Cannon
            cannon = trimesh.creation.cylinder(radius=0.3, height=4)
            cannon.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            cannon.apply_translation([2, 3, 0])
            
            # Tracks
            tracks = []
            for z in [-1.5, 1.5]:
                track = trimesh.creation.box(extents=[6, 1, 0.8])
                track.apply_translation([0, 0.5, z])
                tracks.append(track)
            
            tank = trimesh.util.concatenate([body, turret, cannon] + tracks)
            tank.visual.vertex_colors = np.tile([50, 100, 50, 255], (len(tank.vertices), 1))
            
            return tank
    
    @staticmethod
    def generate_character(character_type: str = 'soldier') -> trimesh.Trimesh:
        """Generate game character"""
        # Body
        body = trimesh.creation.box(extents=[1, 2, 0.5])
        body.apply_translation([0, 2, 0])
        
        # Head
        head = trimesh.creation.icosphere(radius=0.4)
        head.apply_translation([0, 3.5, 0])
        
        # Arms
        arm_l = trimesh.creation.box(extents=[0.3, 1.5, 0.3])
        arm_l.apply_translation([-0.8, 2, 0])
        
        arm_r = trimesh.creation.box(extents=[0.3, 1.5, 0.3])
        arm_r.apply_translation([0.8, 2, 0])
        
        # Legs
        leg_l = trimesh.creation.box(extents=[0.4, 1.8, 0.4])
        leg_l.apply_translation([-0.3, 0.9, 0])
        
        leg_r = trimesh.creation.box(extents=[0.4, 1.8, 0.4])
        leg_r.apply_translation([0.3, 0.9, 0])
        
        character = trimesh.util.concatenate([body, head, arm_l, arm_r, leg_l, leg_r])
        
        if character_type == 'soldier':
            character.visual.vertex_colors = np.tile([50, 100, 50, 255], (len(character.vertices), 1))
        else:
            character.visual.vertex_colors = np.tile([100, 100, 200, 255], (len(character.vertices), 1))
        
        return character
    
    @staticmethod
    def _generate_checkpoints(count: int, length: float, width: float) -> List[Dict]:
        checkpoints = []
        
        for i in range(count):
            t = i / count
            x = t * length
            z = np.sin(t * 4 * np.pi) * 50
            y = np.cos(t * 2 * np.pi) * 10
            
            checkpoints.append({
                'position': [x, y, z],
                'width': width,
                'index': i
            })
        
        return checkpoints