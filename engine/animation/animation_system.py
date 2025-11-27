import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import trimesh
from scipy.spatial.transform import Rotation, Slerp

@dataclass
class Keyframe:
    time: float
    position: np.ndarray
    rotation: np.ndarray
    scale: np.ndarray

class AnimationClip:
    def __init__(self, name: str, duration: float):
        self.name = name
        self.duration = duration
        self.keyframes: List[Keyframe] = []
        self.loop = False
        self.speed = 1.0
        
    def add_keyframe(self, time: float, position: np.ndarray, rotation: np.ndarray, scale: np.ndarray):
        self.keyframes.append(Keyframe(time, position, rotation, scale))
        self.keyframes.sort(key=lambda k: k.time)
    
    def sample(self, time: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.keyframes:
            return np.zeros(3), np.array([0,0,0,1]), np.ones(3)
        
        time = time * self.speed
        if self.loop:
            time = time % self.duration
        
        if time <= self.keyframes[0].time:
            k = self.keyframes[0]
            return k.position, k.rotation, k.scale
        
        if time >= self.keyframes[-1].time:
            k = self.keyframes[-1]
            return k.position, k.rotation, k.scale
        
        for i in range(len(self.keyframes) - 1):
            k1, k2 = self.keyframes[i], self.keyframes[i+1]
            if k1.time <= time <= k2.time:
                t = (time - k1.time) / (k2.time - k1.time)
                
                pos = k1.position + t * (k2.position - k1.position)
                scale = k1.scale + t * (k2.scale - k1.scale)
                
                rot = Rotation.from_quat([k1.rotation, k2.rotation])
                slerp = Slerp([0, 1], rot)
                rotation = slerp([t])[0].as_quat()
                
                return pos, rotation, scale
        
        return self.keyframes[-1].position, self.keyframes[-1].rotation, self.keyframes[-1].scale

class ProceduralAnimator:
    @staticmethod
    def create_walk_cycle(duration: float = 2.0) -> AnimationClip:
        clip = AnimationClip("walk", duration)
        clip.loop = True
        
        for i in range(9):
            t = i / 8.0 * duration
            x = i * 0.5
            y = abs(np.sin(i * np.pi / 4)) * 0.2
            
            clip.add_keyframe(t, np.array([x, y, 0]), np.array([0,0,0,1]), np.ones(3))
        
        return clip
    
    @staticmethod
    def create_rotation_animation(duration: float = 4.0, axis: str = 'y') -> AnimationClip:
        clip = AnimationClip("rotate", duration)
        clip.loop = True
        
        axis_vec = {'x': [1,0,0], 'y': [0,1,0], 'z': [0,0,1]}[axis]
        
        for i in range(17):
            t = i / 16.0 * duration
            angle = t / duration * 2 * np.pi
            rotation = Rotation.from_rotvec(angle * np.array(axis_vec)).as_quat()
            
            clip.add_keyframe(t, np.zeros(3), rotation, np.ones(3))
        
        return clip