import pygame
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from ..generators.text_to_3d import TextTo3DGenerator
from ..generators.image_to_3d import ImageTo3DGenerator
from ..rendering.renderer import AdvancedRenderer
from ..core.physics_engine import PhysicsEngine, Collision
from ..core.nlp_processor import ObjectDescription
import trimesh
import time
import threading
import json
import os

class GameObject:
    def __init__(self, obj_id: str, mesh: trimesh.Trimesh, description: ObjectDescription = None):
        self.id = obj_id
        self.mesh = mesh
        self.description = description
        self.transform = np.eye(4)
        self.physics_body_id = None
        self.components = {}
        self.active = True
        self.tags = set()
        
    def add_component(self, component_name: str, component: Any):
        self.components[component_name] = component
    
    def get_component(self, component_name: str) -> Any:
        return self.components.get(component_name)
    
    def has_component(self, component_name: str) -> bool:
        return component_name in self.components
    
    def add_tag(self, tag: str):
        self.tags.add(tag)
    
    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

class GameEngine:
    def __init__(self, width: int = 1024, height: int = 768, enable_physics: bool = True):
        # Initialize display
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Advanced 3D Game Engine")
        
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        
        # Core systems
        self.renderer = AdvancedRenderer(width, height)
        self.physics = PhysicsEngine() if enable_physics else None
        
        # Generators
        self.text_generator = TextTo3DGenerator()
        self.image_generator = ImageTo3DGenerator()
        
        # Game objects and management
        self.objects: Dict[str, GameObject] = {}
        self.object_counter = 0
        
        # Scene management
        self.scenes = {}
        self.current_scene = "default"
        self.scenes[self.current_scene] = set()
        
        # Input handling
        self.input_handlers = {}
        self.mouse_pos = (0, 0)
        self.keys_pressed = set()
        
        # Camera control
        self.camera_controller = self._init_camera_controller()
        
        # Asset management
        self.asset_cache = {}
        self.asset_directory = "assets"
        os.makedirs(self.asset_directory, exist_ok=True)
        
        # Performance monitoring
        self.performance_stats = {
            'fps': 0,
            'frame_time': 0,
            'objects_rendered': 0,
            'physics_bodies': 0
        }
        
        # Event system
        self.event_listeners = {}
        
        # Threading
        self.update_thread = None
        self.thread_running = False
        
        # Setup physics callbacks
        if self.physics:
            self.physics.add_collision_callback(self._on_collision)
    
    def _init_camera_controller(self) -> Dict:
        return {
            'position': np.array([0.0, 2.0, 8.0]),
            'target': np.array([0.0, 0.0, 0.0]),
            'up': np.array([0.0, 1.0, 0.0]),
            'speed': 5.0,
            'sensitivity': 0.002,
            'yaw': 0.0,
            'pitch': 0.0
        }
    
    def add_object_from_text(self, description: str, 
                           position: tuple = (0, 0, 0),
                           enable_physics: bool = True,
                           physics_properties: Dict = None) -> str:
        """Add 3D object generated from text with full functionality"""
        mesh = self.text_generator.generate_from_text(description)
        obj_desc = self.text_generator.nlp.parse_description(description)
        
        obj_id = f"text_object_{self.object_counter}"
        self.object_counter += 1
        
        # Create game object
        game_obj = GameObject(obj_id, mesh, obj_desc)
        
        # Set initial transform
        transform = np.eye(4)
        transform[:3, 3] = position
        game_obj.transform = transform
        
        # Add to renderer
        material = {
            'albedo': obj_desc.color,
            'metallic': 0.1 if obj_desc.material == 'metallic' else 0.0,
            'roughness': 0.2 if obj_desc.material == 'smooth' else 0.8,
            'ao': 1.0
        }
        self.renderer.add_mesh(obj_id, mesh, material)
        
        # Add physics if enabled
        if enable_physics and self.physics:
            physics_props = physics_properties or {}
            mass = physics_props.get('mass', obj_desc.properties.get('mass', 1.0))
            restitution = physics_props.get('restitution', 0.5)
            friction = physics_props.get('friction', 0.7)
            is_static = physics_props.get('is_static', False)
            
            physics_body_id = self.physics.add_rigid_body(
                obj_id, mesh, np.array(position), mass=mass,
                restitution=restitution, friction=friction, is_static=is_static
            )
            game_obj.physics_body_id = physics_body_id
        
        # Add animation component if specified
        if 'animate' in obj_desc.properties:
            self._add_animation_component(game_obj, obj_desc.properties['animate'])
        
        # Store object
        self.objects[obj_id] = game_obj
        self.scenes[self.current_scene].add(obj_id)
        
        # Save to cache
        self._cache_object(obj_id, description, 'text')
        
        return obj_id
    
    def add_object_from_image(self, image_path: str,
                            position: tuple = (0, 0, 0),
                            generation_method: str = 'advanced',
                            enable_physics: bool = True,
                            physics_properties: Dict = None) -> str:
        """Add 3D object generated from image with advanced options"""
        mesh = self.image_generator.generate_from_image(image_path, generation_method)
        
        obj_id = f"image_object_{self.object_counter}"
        self.object_counter += 1
        
        # Create game object
        game_obj = GameObject(obj_id, mesh)
        
        # Set initial transform
        transform = np.eye(4)
        transform[:3, 3] = position
        game_obj.transform = transform
        
        # Add to renderer with texture from original image
        material = {
            'albedo': [1.0, 1.0, 1.0],  # White base for textured objects
            'metallic': 0.0,
            'roughness': 0.6,
            'ao': 1.0
        }
        self.renderer.add_mesh(obj_id, mesh, material)
        
        # Add physics if enabled
        if enable_physics and self.physics:
            physics_props = physics_properties or {}
            mass = physics_props.get('mass', 1.0)
            restitution = physics_props.get('restitution', 0.3)
            friction = physics_props.get('friction', 0.8)
            is_static = physics_props.get('is_static', False)
            
            physics_body_id = self.physics.add_rigid_body(
                obj_id, mesh, np.array(position), mass=mass,
                restitution=restitution, friction=friction, is_static=is_static
            )
            game_obj.physics_body_id = physics_body_id
        
        # Store object
        self.objects[obj_id] = game_obj
        self.scenes[self.current_scene].add(obj_id)
        
        # Save to cache
        self._cache_object(obj_id, image_path, 'image')
        
        return obj_id
    
    def _add_animation_component(self, game_obj: GameObject, animation_type: str):
        """Add animation component to game object"""
        if animation_type == 'rotate':
            game_obj.add_component('animation', {
                'type': 'rotate',
                'axis': np.array([0, 1, 0]),
                'speed': 1.0,
                'time': 0.0
            })
        elif animation_type == 'float':
            game_obj.add_component('animation', {
                'type': 'float',
                'amplitude': 0.5,
                'frequency': 2.0,
                'time': 0.0,
                'base_y': game_obj.transform[1, 3]
            })
    
    def update_object_transform(self, obj_id: str, position: tuple = None, 
                              rotation: tuple = None, scale: tuple = None):
        """Update object transformation"""
        if obj_id not in self.objects:
            return
        
        obj = self.objects[obj_id]
        transform = obj.transform.copy()
        
        if position:
            transform[:3, 3] = position
            if obj.physics_body_id and self.physics:
                self.physics.set_position(obj.physics_body_id, np.array(position))
        
        if rotation:
            # Convert Euler angles to rotation matrix
            rx, ry, rz = np.radians(rotation)
            Rx = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
            Ry = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
            Rz = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])
            rotation_matrix = Rz @ Ry @ Rx
            transform[:3, :3] = rotation_matrix
        
        if scale:
            if isinstance(scale, (int, float)):
                scale = (scale, scale, scale)
            scale_matrix = np.diag([*scale, 1])
            transform = transform @ scale_matrix
        
        obj.transform = transform
        self.renderer.update_object_transform(obj_id, transform)
    
    def apply_force(self, obj_id: str, force: np.ndarray, point: np.ndarray = None):
        """Apply force to object"""
        if obj_id in self.objects and self.physics:
            obj = self.objects[obj_id]
            if obj.physics_body_id:
                self.physics.apply_force(obj.physics_body_id, force, point)
    
    def apply_impulse(self, obj_id: str, impulse: np.ndarray, point: np.ndarray = None):
        """Apply impulse to object"""
        if obj_id in self.objects and self.physics:
            obj = self.objects[obj_id]
            if obj.physics_body_id:
                self.physics.apply_impulse(obj.physics_body_id, impulse, point)
    
    def remove_object(self, obj_id: str):
        """Remove object from engine"""
        if obj_id not in self.objects:
            return
        
        obj = self.objects[obj_id]
        
        # Remove from physics
        if obj.physics_body_id and self.physics:
            self.physics.remove_body(obj.physics_body_id)
        
        # Remove from renderer (would need to implement in renderer)
        # self.renderer.remove_mesh(obj_id)
        
        # Remove from scene
        if obj_id in self.scenes[self.current_scene]:
            self.scenes[self.current_scene].remove(obj_id)
        
        # Remove from objects
        del self.objects[obj_id]
    
    def set_camera(self, position: np.ndarray, target: np.ndarray, up: np.ndarray = None):
        """Set camera parameters"""
        self.camera_controller['position'] = position
        self.camera_controller['target'] = target
        if up is not None:
            self.camera_controller['up'] = up
        
        self.renderer.set_camera(position, target, up)
    
    def add_event_listener(self, event_type: str, callback: Callable):
        """Add event listener"""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(callback)
    
    def emit_event(self, event_type: str, data: Any = None):
        """Emit event to listeners"""
        if event_type in self.event_listeners:
            for callback in self.event_listeners[event_type]:
                callback(data)
    
    def _on_collision(self, collision: Collision):
        """Handle collision events"""
        self.emit_event('collision', collision)
    
    def run(self):
        """Main game loop with advanced features"""
        self.running = True
        
        # Start physics simulation
        if self.physics:
            self.physics.start_simulation()
        
        # Start update thread
        self.thread_running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.start()
        
        last_time = time.time()
        frame_count = 0
        fps_timer = 0
        
        try:
            while self.running:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                # Handle events
                self._handle_events()
                
                if not self.paused:
                    # Update animations
                    self._update_animations(dt)
                    
                    # Update camera
                    self._update_camera(dt)
                    
                    # Sync physics transforms
                    self._sync_physics_transforms()
                
                # Render
                self._render()
                
                # Performance monitoring
                frame_count += 1
                fps_timer += dt
                if fps_timer >= 1.0:
                    self.performance_stats['fps'] = frame_count / fps_timer
                    self.performance_stats['frame_time'] = fps_timer / frame_count * 1000
                    frame_count = 0
                    fps_timer = 0
                
                self.clock.tick(60)
        
        finally:
            self._cleanup()
    
    def _update_loop(self):
        """Separate update thread for non-rendering updates"""
        while self.thread_running:
            if not self.paused:
                # Update game logic here
                pass
            time.sleep(1/120)  # 120 Hz update rate
    
    def _handle_events(self):
        """Enhanced event handling"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset_scene()
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                self._handle_mouse_look(event.rel)
    
    def _handle_mouse_look(self, mouse_delta):
        """Handle mouse look for camera"""
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            dx, dy = mouse_delta
            sensitivity = self.camera_controller['sensitivity']
            
            self.camera_controller['yaw'] += dx * sensitivity
            self.camera_controller['pitch'] -= dy * sensitivity
            self.camera_controller['pitch'] = np.clip(self.camera_controller['pitch'], -np.pi/2, np.pi/2)
    
    def _update_camera(self, dt: float):
        """Update camera based on input"""
        speed = self.camera_controller['speed'] * dt
        
        # WASD movement
        forward = np.array([0, 0, -1])
        right = np.array([1, 0, 0])
        
        if pygame.K_w in self.keys_pressed:
            self.camera_controller['position'] += forward * speed
        if pygame.K_s in self.keys_pressed:
            self.camera_controller['position'] -= forward * speed
        if pygame.K_a in self.keys_pressed:
            self.camera_controller['position'] -= right * speed
        if pygame.K_d in self.keys_pressed:
            self.camera_controller['position'] += right * speed
        if pygame.K_q in self.keys_pressed:
            self.camera_controller['position'][1] -= speed
        if pygame.K_e in self.keys_pressed:
            self.camera_controller['position'][1] += speed
        
        # Update camera target based on yaw/pitch
        yaw = self.camera_controller['yaw']
        pitch = self.camera_controller['pitch']
        
        target_offset = np.array([
            np.cos(pitch) * np.sin(yaw),
            np.sin(pitch),
            np.cos(pitch) * np.cos(yaw)
        ])
        
        self.camera_controller['target'] = self.camera_controller['position'] + target_offset
        
        # Update renderer camera
        self.renderer.set_camera(
            self.camera_controller['position'],
            self.camera_controller['target'],
            self.camera_controller['up']
        )
    
    def _update_animations(self, dt: float):
        """Update object animations"""
        for obj in self.objects.values():
            if obj.has_component('animation'):
                anim = obj.get_component('animation')
                anim['time'] += dt
                
                if anim['type'] == 'rotate':
                    angle = anim['speed'] * anim['time']
                    axis = anim['axis']
                    
                    # Create rotation matrix
                    cos_a = np.cos(angle)
                    sin_a = np.sin(angle)
                    rotation_matrix = np.eye(4)
                    
                    if np.allclose(axis, [0, 1, 0]):  # Y-axis rotation
                        rotation_matrix[:3, :3] = np.array([
                            [cos_a, 0, sin_a],
                            [0, 1, 0],
                            [-sin_a, 0, cos_a]
                        ])
                    
                    # Preserve position
                    position = obj.transform[:3, 3].copy()
                    obj.transform = rotation_matrix
                    obj.transform[:3, 3] = position
                    
                    self.renderer.update_object_transform(obj.id, obj.transform)
                
                elif anim['type'] == 'float':
                    y_offset = np.sin(anim['frequency'] * anim['time']) * anim['amplitude']
                    obj.transform[1, 3] = anim['base_y'] + y_offset
                    
                    self.renderer.update_object_transform(obj.id, obj.transform)
    
    def _sync_physics_transforms(self):
        """Sync transforms from physics simulation"""
        if not self.physics:
            return
        
        for obj in self.objects.values():
            if obj.physics_body_id:
                transform = self.physics.get_transform_matrix(obj.physics_body_id)
                obj.transform = transform
                self.renderer.update_object_transform(obj.id, transform)
    
    def _render(self):
        """Render frame"""
        self.renderer.render()
        pygame.display.flip()
        
        # Update performance stats
        self.performance_stats['objects_rendered'] = len(self.objects)
        if self.physics:
            self.performance_stats['physics_bodies'] = len(self.physics.bodies)
    
    def _reset_scene(self):
        """Reset current scene"""
        # Remove all objects
        for obj_id in list(self.objects.keys()):
            self.remove_object(obj_id)
        
        # Reset camera
        self.camera_controller = self._init_camera_controller()
        self.set_camera(
            self.camera_controller['position'],
            self.camera_controller['target'],
            self.camera_controller['up']
        )
    
    def _cache_object(self, obj_id: str, source: str, source_type: str):
        """Cache object data for quick loading"""
        cache_data = {
            'id': obj_id,
            'source': source,
            'type': source_type,
            'timestamp': time.time()
        }
        
        cache_file = os.path.join(self.asset_directory, f"{obj_id}_cache.json")
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        return self.performance_stats.copy()
    
    def _cleanup(self):
        """Cleanup resources"""
        self.thread_running = False
        if self.update_thread:
            self.update_thread.join()
        
        if self.physics:
            self.physics.stop_simulation()
        
        self.renderer.cleanup()
        pygame.quit()