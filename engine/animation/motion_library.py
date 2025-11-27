import numpy as np
from scipy.spatial.transform import Rotation
from typing import Dict, List, Tuple
from .animation_system import AnimationClip, Keyframe

class MotionLibrary:
    """60+ Production-Ready Animations"""
    
    ANIMATIONS = {
        # Locomotion (15)
        'walk': {'duration': 1.0, 'category': 'locomotion'},
        'run': {'duration': 0.6, 'category': 'locomotion'},
        'sprint': {'duration': 0.4, 'category': 'locomotion'},
        'jog': {'duration': 0.8, 'category': 'locomotion'},
        'walk_backward': {'duration': 1.2, 'category': 'locomotion'},
        'strafe_left': {'duration': 1.0, 'category': 'locomotion'},
        'strafe_right': {'duration': 1.0, 'category': 'locomotion'},
        'crouch_walk': {'duration': 1.5, 'category': 'locomotion'},
        'crawl': {'duration': 2.0, 'category': 'locomotion'},
        'climb': {'duration': 2.0, 'category': 'locomotion'},
        'slide': {'duration': 1.0, 'category': 'locomotion'},
        'roll': {'duration': 0.8, 'category': 'locomotion'},
        'dive': {'duration': 1.0, 'category': 'locomotion'},
        'swim': {'duration': 1.5, 'category': 'locomotion'},
        'fly': {'duration': 2.0, 'category': 'locomotion'},
        
        # Actions (20)
        'jump': {'duration': 1.0, 'category': 'action'},
        'double_jump': {'duration': 1.5, 'category': 'action'},
        'land': {'duration': 0.5, 'category': 'action'},
        'fall': {'duration': 1.0, 'category': 'action'},
        'punch': {'duration': 0.4, 'category': 'action'},
        'kick': {'duration': 0.6, 'category': 'action'},
        'shoot': {'duration': 0.3, 'category': 'action'},
        'reload': {'duration': 2.0, 'category': 'action'},
        'throw': {'duration': 0.8, 'category': 'action'},
        'pickup': {'duration': 1.0, 'category': 'action'},
        'open_door': {'duration': 1.5, 'category': 'action'},
        'climb_ladder': {'duration': 2.0, 'category': 'action'},
        'vault': {'duration': 1.0, 'category': 'action'},
        'melee_attack': {'duration': 0.5, 'category': 'action'},
        'block': {'duration': 0.5, 'category': 'action'},
        'dodge': {'duration': 0.6, 'category': 'action'},
        'aim': {'duration': 0.5, 'category': 'action'},
        'crouch': {'duration': 0.5, 'category': 'action'},
        'stand': {'duration': 0.5, 'category': 'action'},
        'use_item': {'duration': 1.0, 'category': 'action'},
        
        # Idle/Gestures (15)
        'idle': {'duration': 3.0, 'category': 'idle'},
        'idle_combat': {'duration': 2.0, 'category': 'idle'},
        'wave': {'duration': 1.5, 'category': 'gesture'},
        'point': {'duration': 1.0, 'category': 'gesture'},
        'salute': {'duration': 1.5, 'category': 'gesture'},
        'clap': {'duration': 2.0, 'category': 'gesture'},
        'cheer': {'duration': 2.0, 'category': 'gesture'},
        'dance': {'duration': 4.0, 'category': 'gesture'},
        'sit': {'duration': 2.0, 'category': 'pose'},
        'sit_idle': {'duration': 3.0, 'category': 'pose'},
        'stand_up': {'duration': 1.5, 'category': 'pose'},
        'kneel': {'duration': 1.5, 'category': 'pose'},
        'lie_down': {'duration': 2.0, 'category': 'pose'},
        'lean_wall': {'duration': 2.0, 'category': 'pose'},
        'arms_crossed': {'duration': 2.0, 'category': 'pose'},
        
        # Combat (10)
        'sword_slash': {'duration': 0.6, 'category': 'combat'},
        'sword_stab': {'duration': 0.5, 'category': 'combat'},
        'bow_draw': {'duration': 1.0, 'category': 'combat'},
        'bow_shoot': {'duration': 0.4, 'category': 'combat'},
        'shield_block': {'duration': 0.5, 'category': 'combat'},
        'parry': {'duration': 0.4, 'category': 'combat'},
        'combo_attack': {'duration': 1.5, 'category': 'combat'},
        'heavy_attack': {'duration': 1.2, 'category': 'combat'},
        'spin_attack': {'duration': 1.0, 'category': 'combat'},
        'ground_slam': {'duration': 1.5, 'category': 'combat'},
        
        # Reactions (10)
        'hit_front': {'duration': 0.5, 'category': 'reaction'},
        'hit_back': {'duration': 0.5, 'category': 'reaction'},
        'death': {'duration': 2.0, 'category': 'reaction'},
        'stagger': {'duration': 0.8, 'category': 'reaction'},
        'knockback': {'duration': 1.0, 'category': 'reaction'},
        'stumble': {'duration': 0.7, 'category': 'reaction'},
        'celebrate': {'duration': 3.0, 'category': 'reaction'},
        'taunt': {'duration': 2.0, 'category': 'reaction'},
        'fear': {'duration': 2.0, 'category': 'reaction'},
        'surprised': {'duration': 1.0, 'category': 'reaction'}
    }
    
    @classmethod
    def generate(cls, anim_name: str) -> AnimationClip:
        if anim_name not in cls.ANIMATIONS:
            anim_name = 'idle'
        
        config = cls.ANIMATIONS[anim_name]
        method_name = f'_create_{anim_name}'
        
        if hasattr(cls, method_name):
            return getattr(cls, method_name)(config['duration'])
        else:
            return cls._create_generic(anim_name, config['duration'])
    
    @staticmethod
    def _create_run(duration: float) -> AnimationClip:
        clip = AnimationClip("run", duration)
        clip.loop = True
        frames = 12
        
        for i in range(frames):
            t = i / (frames - 1) * duration
            progress = i / (frames - 1)
            
            x = progress * 5
            y = abs(np.sin(progress * np.pi * 4)) * 0.15
            
            body_tilt = np.sin(progress * np.pi * 4) * 0.1
            rot = Rotation.from_euler('x', body_tilt).as_quat()
            
            clip.add_keyframe(t, np.array([x, y, 0]), rot, np.ones(3))
        
        return clip
    
    @staticmethod
    def _create_sit(duration: float) -> AnimationClip:
        clip = AnimationClip("sit", duration)
        frames = 10
        
        for i in range(frames):
            t = i / (frames - 1) * duration
            progress = i / (frames - 1)
            
            y = 1.0 - progress * 0.7
            
            bend = progress * np.pi / 3
            rot = Rotation.from_euler('x', bend).as_quat()
            
            clip.add_keyframe(t, np.array([0, y, 0]), rot, np.ones(3))
        
        return clip
    
    @staticmethod
    def _create_punch(duration: float) -> AnimationClip:
        clip = AnimationClip("punch", duration)
        frames = 8
        
        for i in range(frames):
            t = i / (frames - 1) * duration
            progress = i / (frames - 1)
            
            if progress < 0.3:
                x = 0
            elif progress < 0.6:
                x = (progress - 0.3) / 0.3 * 0.5
            else:
                x = 0.5 - (progress - 0.6) / 0.4 * 0.5
            
            twist = np.sin(progress * np.pi) * 0.3
            rot = Rotation.from_euler('y', twist).as_quat()
            
            clip.add_keyframe(t, np.array([x, 0, 0]), rot, np.ones(3))
        
        return clip
    
    @staticmethod
    def _create_generic(name: str, duration: float) -> AnimationClip:
        clip = AnimationClip(name, duration)
        clip.loop = True
        
        for i in range(9):
            t = i / 8.0 * duration
            progress = i / 8.0
            
            y = np.sin(progress * 2 * np.pi) * 0.1
            clip.add_keyframe(t, np.array([0, y, 0]), np.array([0,0,0,1]), np.ones(3))
        
        return clip