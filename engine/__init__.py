"""
Advanced 3D Game Engine with AI Generation

A comprehensive game engine featuring:
- Text-to-3D model generation with advanced NLP
- Image-to-3D conversion with multiple algorithms
- Real-time physics simulation
- Advanced PBR rendering
- Asset management and caching
- Multi-session web API
- Performance optimization

Author: Game Engine Team
Version: 2.0.0
"""

from .core.game_engine import GameEngine, GameObject
from .core.nlp_processor import NLPProcessor, ObjectDescription, ShapeType
from .core.physics_engine import PhysicsEngine, RigidBody, Collision
from .core.asset_manager import AssetManager, AssetMetadata

from .generators.text_to_3d import TextTo3DGenerator
from .generators.image_to_3d import ImageTo3DGenerator

from .rendering.renderer import AdvancedRenderer

__version__ = "2.0.0"
__author__ = "Game Engine Team"

__all__ = [
    # Core classes
    'GameEngine',
    'GameObject',
    'NLPProcessor',
    'ObjectDescription',
    'ShapeType',
    'PhysicsEngine',
    'RigidBody',
    'Collision',
    'AssetManager',
    'AssetMetadata',
    
    # Generators
    'TextTo3DGenerator',
    'ImageTo3DGenerator',
    
    # Rendering
    'AdvancedRenderer',
]

# Engine configuration
DEFAULT_CONFIG = {
    'window': {
        'width': 1024,
        'height': 768,
        'title': 'Advanced 3D Game Engine',
        'vsync': True,
        'fullscreen': False
    },
    'physics': {
        'enabled': True,
        'gravity': [0.0, -9.81, 0.0],
        'time_step': 1.0 / 60.0,
        'max_iterations': 10
    },
    'rendering': {
        'shadows': True,
        'anti_aliasing': True,
        'post_processing': True,
        'max_lights': 8
    },
    'assets': {
        'cache_size_mb': 500,
        'auto_cleanup': True,
        'compression': True
    },
    'generation': {
        'text_quality': 'high',
        'image_method': 'advanced',
        'cache_results': True
    }
}

def create_engine(config: dict = None) -> GameEngine:
    """
    Create a game engine instance with optional configuration.
    
    Args:
        config: Configuration dictionary to override defaults
        
    Returns:
        Configured GameEngine instance
    """
    if config is None:
        config = DEFAULT_CONFIG
    else:
        # Merge with defaults
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        config = merged_config
    
    return GameEngine(
        width=config['window']['width'],
        height=config['window']['height'],
        enable_physics=config['physics']['enabled']
    )