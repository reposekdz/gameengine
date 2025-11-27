import os
from pathlib import Path

def create_directories():
    """Initialize all required directories"""
    
    directories = [
        'assets/models/characters',
        'assets/models/vehicles',
        'assets/models/buildings',
        'assets/models/props',
        'assets/models/nature',
        'assets/models/weapons',
        'assets/textures/diffuse',
        'assets/textures/normal',
        'assets/textures/roughness',
        'assets/textures/metallic',
        'assets/textures/ao',
        'assets/textures/emissive',
        'assets/materials/pbr',
        'assets/materials/shaders',
        'assets/animations/characters',
        'assets/animations/vehicles',
        'assets/audio/music',
        'assets/audio/sfx',
        'assets/audio/voice',
        'assets/scenes/levels',
        'assets/generated/text_to_3d',
        'assets/generated/image_to_3d',
        'assets/generated/giga',
        'assets/generated/worlds',
        'assets/generated/games',
        'assets/generated/cartoons',
        'assets/database',
        'cache/meshes',
        'cache/textures',
        'cache/scenes',
        'uploads',
        'logs',
        'models'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f'Created: {directory}')
    
    print(f'\nTotal directories created: {len(directories)}')
    print('Initialization complete!')

if __name__ == '__main__':
    create_directories()
