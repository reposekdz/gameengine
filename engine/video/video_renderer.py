import cv2
import numpy as np
from typing import List, Tuple, Optional
import trimesh
from PIL import Image
import subprocess
import os

class VideoRenderer:
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 60):
        self.width = width
        self.height = height
        self.fps = fps
        self.frames = []
        
    def render_animation(self, scene_objects: List[Dict], duration: float, output_path: str):
        total_frames = int(duration * self.fps)
        
        for frame_idx in range(total_frames):
            time = frame_idx / self.fps
            frame = self._render_frame(scene_objects, time)
            self.frames.append(frame)
        
        self._export_video(output_path)
    
    def _render_frame(self, scene_objects: List[Dict], time: float) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        for obj in scene_objects:
            mesh = obj['mesh']
            animation = obj.get('animation')
            
            if animation:
                pos, rot, scale = animation.sample(time)
                transform = self._create_transform(pos, rot, scale)
                transformed_mesh = mesh.copy()
                transformed_mesh.apply_transform(transform)
            else:
                transformed_mesh = mesh
            
            self._rasterize_mesh(frame, transformed_mesh)
        
        return frame
    
    def _create_transform(self, pos: np.ndarray, rot: np.ndarray, scale: np.ndarray) -> np.ndarray:
        from scipy.spatial.transform import Rotation
        
        transform = np.eye(4)
        transform[:3, :3] = Rotation.from_quat(rot).as_matrix() * scale
        transform[:3, 3] = pos
        
        return transform
    
    def _rasterize_mesh(self, frame: np.ndarray, mesh: trimesh.Trimesh):
        vertices_2d = self._project_vertices(mesh.vertices)
        
        for face in mesh.faces:
            pts = vertices_2d[face].astype(np.int32)
            
            if hasattr(mesh.visual, 'vertex_colors'):
                color = tuple(map(int, mesh.visual.vertex_colors[face[0]][:3]))
            else:
                color = (200, 200, 200)
            
            cv2.fillPoly(frame, [pts], color)
            cv2.polylines(frame, [pts], True, (0, 0, 0), 1)
    
    def _project_vertices(self, vertices: np.ndarray) -> np.ndarray:
        fov = 60
        aspect = self.width / self.height
        near, far = 0.1, 1000
        
        f = 1 / np.tan(np.radians(fov) / 2)
        
        proj = np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ])
        
        view = np.eye(4)
        view[2, 3] = -10
        
        vertices_h = np.column_stack([vertices, np.ones(len(vertices))])
        projected = vertices_h @ view.T @ proj.T
        
        projected[:, :2] /= projected[:, 3:4]
        
        screen_coords = np.zeros((len(vertices), 2))
        screen_coords[:, 0] = (projected[:, 0] + 1) * self.width / 2
        screen_coords[:, 1] = (1 - projected[:, 1]) * self.height / 2
        
        return screen_coords
    
    def _export_video(self, output_path: str):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        for frame in self.frames:
            out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        out.release()
        
        # Convert to H.264 if ffmpeg available
        try:
            temp_path = output_path.replace('.mp4', '_temp.mp4')
            os.rename(output_path, temp_path)
            subprocess.run([
                'ffmpeg', '-i', temp_path, '-c:v', 'libx264', 
                '-preset', 'slow', '-crf', '18', output_path
            ], check=True)
            os.remove(temp_path)
        except:
            pass

class MultiObjectComposer:
    def __init__(self):
        self.objects = []
        
    def add_object(self, mesh: trimesh.Trimesh, animation=None, position=(0,0,0)):
        self.objects.append({
            'mesh': mesh,
            'animation': animation,
            'position': np.array(position)
        })
    
    def compose_scene(self) -> trimesh.Trimesh:
        if not self.objects:
            return trimesh.Trimesh()
        
        meshes = []
        for obj in self.objects:
            mesh = obj['mesh'].copy()
            mesh.apply_translation(obj['position'])
            meshes.append(mesh)
        
        return trimesh.util.concatenate(meshes)
    
    def export_scene(self, output_path: str, format: str = 'glb'):
        scene = self.compose_scene()
        scene.export(output_path)