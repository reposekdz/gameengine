#!/usr/bin/env python3
"""
Advanced 3D Game Engine - Main Entry Point
Full-featured game engine with AI-powered 3D generation, physics, and rendering
"""

import sys
import os
import argparse
import time
import numpy as np
from engine.core.game_engine import GameEngine
from engine.core.physics_engine import Collision

def create_demo_scene(engine: GameEngine):
    """Create comprehensive demo scene"""
    print("Creating advanced demo scene...")
    
    # Ground plane
    ground_id = engine.add_object_from_text(
        "large flat gray terrain plane",
        position=(0, -2, 0),
        physics_properties={'is_static': True, 'friction': 0.8}
    )
    
    # Various objects with different materials and physics
    objects = [
        ("shiny metallic red cube", (-3, 2, 0), {'mass': 2.0, 'restitution': 0.3}),
        ("smooth blue sphere", (0, 4, 0), {'mass': 1.0, 'restitution': 0.8}),
        ("rough wooden cylinder", (3, 2, 0), {'mass': 1.5, 'restitution': 0.2}),
        ("spinning golden torus", (-1, 3, 2), {'mass': 0.8, 'restitution': 0.6}),
        ("tall glass tower", (2, 1, -2), {'mass': 3.0, 'restitution': 0.1}),
        ("floating organic sphere", (0, 6, 0), {'mass': 0.5, 'restitution': 0.9})
    ]
    
    created_objects = []
    for desc, pos, physics_props in objects:
        obj_id = engine.add_object_from_text(
            desc, position=pos, physics_properties=physics_props
        )
        created_objects.append(obj_id)
        print(f"Created: {desc} -> {obj_id}")
    
    # Add some initial forces for dynamic behavior
    time.sleep(1)  # Let physics initialize
    
    # Apply random impulses to make scene dynamic
    for obj_id in created_objects[1:4]:  # Skip ground
        force = np.random.uniform(-5, 5, 3)
        force[1] = abs(force[1])  # Upward force
        engine.apply_impulse(obj_id, force)
    
    return created_objects

def setup_collision_handler(engine: GameEngine):
    """Setup collision event handling"""
    def on_collision(collision: Collision):
        print(f"Collision: {collision.body1_id} <-> {collision.body2_id} "
              f"(depth: {collision.penetration_depth:.3f})")
    
    engine.add_event_listener('collision', on_collision)

def interactive_mode(engine: GameEngine):
    """Interactive mode for real-time object creation"""
    print("\n=== Interactive Mode ===")
    print("Commands:")
    print("  'create <description>' - Create object from text")
    print("  'force <object_id> <fx> <fy> <fz>' - Apply force")
    print("  'camera <x> <y> <z>' - Move camera")
    print("  'stats' - Show performance stats")
    print("  'quit' - Exit interactive mode")
    print("  'help' - Show this help")
    
    import threading
    
    def input_handler():
        while engine.running:
            try:
                cmd = input("> ").strip().lower()
                
                if cmd.startswith('create '):
                    desc = cmd[7:]
                    pos = (np.random.uniform(-3, 3), np.random.uniform(2, 5), np.random.uniform(-3, 3))
                    obj_id = engine.add_object_from_text(desc, position=pos)
                    print(f"Created {obj_id} at {pos}")
                
                elif cmd.startswith('force '):
                    parts = cmd.split()
                    if len(parts) >= 5:
                        obj_id = parts[1]
                        force = [float(parts[2]), float(parts[3]), float(parts[4])]
                        engine.apply_force(obj_id, np.array(force))
                        print(f"Applied force {force} to {obj_id}")
                
                elif cmd.startswith('camera '):
                    parts = cmd.split()
                    if len(parts) >= 4:
                        pos = [float(parts[1]), float(parts[2]), float(parts[3])]
                        engine.set_camera(np.array(pos), np.array([0, 0, 0]))
                        print(f"Camera moved to {pos}")
                
                elif cmd == 'stats':
                    stats = engine.get_performance_stats()
                    print(f"FPS: {stats['fps']:.1f}, Frame Time: {stats['frame_time']:.2f}ms")
                    print(f"Objects: {stats['objects_rendered']}, Physics Bodies: {stats['physics_bodies']}")
                
                elif cmd == 'quit':
                    engine.running = False
                    break
                
                elif cmd == 'help':
                    print("Commands: create, force, camera, stats, quit, help")
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
            
            except (EOFError, KeyboardInterrupt):
                engine.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
    
    input_thread = threading.Thread(target=input_handler, daemon=True)
    input_thread.start()

def benchmark_mode(engine: GameEngine):
    """Benchmark mode for performance testing"""
    print("\n=== Benchmark Mode ===")
    
    # Create many objects for stress testing
    objects = []
    start_time = time.time()
    
    descriptions = [
        "red cube", "blue sphere", "green cylinder", "yellow cone",
        "purple torus", "orange pyramid", "pink plane", "brown box"
    ]
    
    for i in range(50):  # Create 50 objects
        desc = descriptions[i % len(descriptions)]
        pos = (np.random.uniform(-10, 10), np.random.uniform(1, 8), np.random.uniform(-10, 10))
        obj_id = engine.add_object_from_text(f"{desc} {i}", position=pos)
        objects.append(obj_id)
        
        if i % 10 == 0:
            print(f"Created {i+1} objects...")
    
    creation_time = time.time() - start_time
    print(f"Created {len(objects)} objects in {creation_time:.2f} seconds")
    print(f"Average: {creation_time/len(objects)*1000:.2f}ms per object")
    
    # Run for a while to measure performance
    print("Running benchmark for 30 seconds...")
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 30 and engine.running:
        time.sleep(1/60)  # Simulate 60 FPS
        frame_count += 1
        
        if frame_count % 300 == 0:  # Every 5 seconds
            stats = engine.get_performance_stats()
            print(f"FPS: {stats['fps']:.1f}, Objects: {stats['objects_rendered']}")
    
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time
    print(f"\nBenchmark complete: {avg_fps:.1f} average FPS over {total_time:.1f} seconds")

def main():
    parser = argparse.ArgumentParser(description='Advanced 3D Game Engine')
    parser.add_argument('--mode', choices=['demo', 'interactive', 'benchmark', 'minimal'], 
                       default='demo', help='Engine mode')
    parser.add_argument('--width', type=int, default=1024, help='Window width')
    parser.add_argument('--height', type=int, default=768, help='Window height')
    parser.add_argument('--no-physics', action='store_true', help='Disable physics')
    parser.add_argument('--server', action='store_true', help='Start web server alongside engine')
    
    args = parser.parse_args()
    
    print("=== Advanced 3D Game Engine ===")
    print(f"Mode: {args.mode}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Physics: {'Disabled' if args.no_physics else 'Enabled'}")
    print()
    
    # Initialize game engine
    engine = GameEngine(
        width=args.width, 
        height=args.height, 
        enable_physics=not args.no_physics
    )
    
    # Setup collision handling
    if not args.no_physics:
        setup_collision_handler(engine)
    
    # Start web server if requested
    if args.server:
        import threading
        import subprocess
        
        def start_server():
            subprocess.run([sys.executable, "server/web_server.py"])
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        print("Web server starting on http://localhost:5000")
    
    # Run based on mode
    if args.mode == 'demo':
        create_demo_scene(engine)
        print("\nControls:")
        print("  WASD - Move camera")
        print("  QE - Move up/down")
        print("  Mouse - Look around (hold left button)")
        print("  Space - Pause/unpause")
        print("  R - Reset scene")
        print("  ESC - Exit")
        
    elif args.mode == 'interactive':
        create_demo_scene(engine)
        interactive_mode(engine)
        
    elif args.mode == 'benchmark':
        benchmark_mode(engine)
        
    elif args.mode == 'minimal':
        # Just a simple cube for testing
        engine.add_object_from_text("red cube", position=(0, 0, 0))
    
    print("\nStarting engine...")
    
    try:
        # Run the engine
        engine.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        print("Engine stopped.")

if __name__ == "__main__":
    main()