import numpy as np
import trimesh
import cv2
from typing import Tuple, Optional, Dict, List
from scipy.ndimage import gaussian_filter
from skimage import filters, morphology, measure
import torch
import torch.nn as nn
import torch.nn.functional as F

class CartoonStyler:
    def __init__(self):
        self.edge_threshold = 0.1
        self.color_quantization = 8
        self.outline_thickness = 2
        
    def convert_to_cartoon(self, mesh: trimesh.Trimesh, style: str = 'cel_shaded') -> trimesh.Trimesh:
        """Convert 3D model to cartoon style"""
        if style == 'cel_shaded':
            return self._cel_shading(mesh)
        elif style == 'toon':
            return self._toon_style(mesh)
        elif style == 'anime':
            return self._anime_style(mesh)
        elif style == 'comic':
            return self._comic_style(mesh)
        else:
            return self._cel_shading(mesh)
    
    def _cel_shading(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply cel-shading cartoon effect"""
        cartoon_mesh = mesh.copy()
        
        # Quantize colors
        if hasattr(cartoon_mesh.visual, 'vertex_colors'):
            colors = cartoon_mesh.visual.vertex_colors[:, :3].astype(float) / 255.0
            quantized = self._quantize_colors(colors, self.color_quantization)
            cartoon_mesh.visual.vertex_colors = (quantized * 255).astype(np.uint8)
        
        # Simplify geometry for cartoon look
        cartoon_mesh = self._simplify_for_cartoon(cartoon_mesh)
        
        # Add edge detection data
        cartoon_mesh = self._add_edge_data(cartoon_mesh)
        
        return cartoon_mesh
    
    def _toon_style(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply toon shading style"""
        toon_mesh = mesh.copy()
        
        # Aggressive color quantization
        if hasattr(toon_mesh.visual, 'vertex_colors'):
            colors = toon_mesh.visual.vertex_colors[:, :3].astype(float) / 255.0
            
            # Posterize colors
            levels = 4
            quantized = np.floor(colors * levels) / levels
            
            # Boost saturation
            hsv = self._rgb_to_hsv(quantized)
            hsv[:, 1] = np.clip(hsv[:, 1] * 1.5, 0, 1)
            quantized = self._hsv_to_rgb(hsv)
            
            toon_mesh.visual.vertex_colors = (quantized * 255).astype(np.uint8)
        
        # Smooth and simplify
        toon_mesh = toon_mesh.smoothed()
        
        return toon_mesh
    
    def _anime_style(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply anime-style rendering"""
        anime_mesh = mesh.copy()
        
        # Smooth surfaces
        anime_mesh = anime_mesh.smoothed()
        
        # Enhance colors with anime palette
        if hasattr(anime_mesh.visual, 'vertex_colors'):
            colors = anime_mesh.visual.vertex_colors[:, :3].astype(float) / 255.0
            
            # Brighten and saturate
            hsv = self._rgb_to_hsv(colors)
            hsv[:, 1] = np.clip(hsv[:, 1] * 1.3, 0, 1)  # Saturation
            hsv[:, 2] = np.clip(hsv[:, 2] * 1.2, 0, 1)  # Brightness
            
            colors = self._hsv_to_rgb(hsv)
            
            # Quantize to anime-like levels
            quantized = self._quantize_colors(colors, 6)
            anime_mesh.visual.vertex_colors = (quantized * 255).astype(np.uint8)
        
        return anime_mesh
    
    def _comic_style(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Apply comic book style"""
        comic_mesh = mesh.copy()
        
        # High contrast colors
        if hasattr(comic_mesh.visual, 'vertex_colors'):
            colors = comic_mesh.visual.vertex_colors[:, :3].astype(float) / 255.0
            
            # Increase contrast
            colors = np.clip((colors - 0.5) * 1.5 + 0.5, 0, 1)
            
            # Quantize heavily
            quantized = self._quantize_colors(colors, 5)
            comic_mesh.visual.vertex_colors = (quantized * 255).astype(np.uint8)
        
        # Add halftone effect data
        comic_mesh = self._add_halftone_data(comic_mesh)
        
        return comic_mesh
    
    def _quantize_colors(self, colors: np.ndarray, levels: int) -> np.ndarray:
        """Quantize colors to specific levels"""
        return np.round(colors * (levels - 1)) / (levels - 1)
    
    def _simplify_for_cartoon(self, mesh: trimesh.Trimesh, target_faces: int = None) -> trimesh.Trimesh:
        """Simplify mesh for cartoon appearance"""
        if target_faces is None:
            target_faces = max(len(mesh.faces) // 2, 100)
        
        try:
            simplified = mesh.simplify_quadric_decimation(target_faces)
            return simplified
        except:
            return mesh
    
    def _add_edge_data(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Add edge detection data for outline rendering"""
        edges = mesh.edges_unique
        edge_normals = []
        
        for edge in edges:
            v1, v2 = mesh.vertices[edge[0]], mesh.vertices[edge[1]]
            edge_vec = v2 - v1
            edge_normals.append(edge_vec / np.linalg.norm(edge_vec))
        
        mesh.metadata['edge_data'] = {
            'edges': edges,
            'normals': np.array(edge_normals)
        }
        
        return mesh
    
    def _add_halftone_data(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Add halftone pattern data"""
        if hasattr(mesh.visual, 'vertex_colors'):
            colors = mesh.visual.vertex_colors[:, :3].astype(float) / 255.0
            brightness = np.mean(colors, axis=1)
            
            mesh.metadata['halftone'] = {
                'brightness': brightness,
                'pattern_scale': 0.1
            }
        
        return mesh
    
    def _rgb_to_hsv(self, rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV"""
        hsv = np.zeros_like(rgb)
        
        r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
        max_c = np.max(rgb, axis=1)
        min_c = np.min(rgb, axis=1)
        diff = max_c - min_c
        
        # Hue
        mask = diff != 0
        hsv[mask & (max_c == r), 0] = (60 * ((g[mask & (max_c == r)] - b[mask & (max_c == r)]) / diff[mask & (max_c == r)]) + 360) % 360
        hsv[mask & (max_c == g), 0] = (60 * ((b[mask & (max_c == g)] - r[mask & (max_c == g)]) / diff[mask & (max_c == g)]) + 120) % 360
        hsv[mask & (max_c == b), 0] = (60 * ((r[mask & (max_c == b)] - g[mask & (max_c == b)]) / diff[mask & (max_c == b)]) + 240) % 360
        hsv[:, 0] /= 360
        
        # Saturation
        hsv[max_c != 0, 1] = diff[max_c != 0] / max_c[max_c != 0]
        
        # Value
        hsv[:, 2] = max_c
        
        return hsv
    
    def _hsv_to_rgb(self, hsv: np.ndarray) -> np.ndarray:
        """Convert HSV to RGB"""
        rgb = np.zeros_like(hsv)
        
        h, s, v = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
        c = v * s
        x = c * (1 - np.abs((h / 60) % 2 - 1))
        m = v - c
        
        mask1 = (h >= 0) & (h < 60)
        mask2 = (h >= 60) & (h < 120)
        mask3 = (h >= 120) & (h < 180)
        mask4 = (h >= 180) & (h < 240)
        mask5 = (h >= 240) & (h < 300)
        mask6 = (h >= 300) & (h < 360)
        
        rgb[mask1] = np.column_stack([c[mask1], x[mask1], np.zeros(np.sum(mask1))])
        rgb[mask2] = np.column_stack([x[mask2], c[mask2], np.zeros(np.sum(mask2))])
        rgb[mask3] = np.column_stack([np.zeros(np.sum(mask3)), c[mask3], x[mask3]])
        rgb[mask4] = np.column_stack([np.zeros(np.sum(mask4)), x[mask4], c[mask4]])
        rgb[mask5] = np.column_stack([x[mask5], np.zeros(np.sum(mask5)), c[mask5]])
        rgb[mask6] = np.column_stack([c[mask6], np.zeros(np.sum(mask6)), x[mask6]])
        
        rgb += m[:, np.newaxis]
        
        return rgb

class NPRRenderer:
    """Non-Photorealistic Rendering for cartoon effects"""
    
    def __init__(self):
        self.outline_color = [0, 0, 0]
        self.outline_width = 3
        
    def render_with_outlines(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Add thick outlines for cartoon effect"""
        outlined_mesh = mesh.copy()
        
        # Detect silhouette edges
        silhouette_edges = self._detect_silhouette_edges(mesh)
        
        # Create outline geometry
        outline_mesh = self._create_outline_mesh(mesh, silhouette_edges)
        
        # Combine with original
        if outline_mesh:
            outlined_mesh = trimesh.util.concatenate([mesh, outline_mesh])
        
        return outlined_mesh
    
    def _detect_silhouette_edges(self, mesh: trimesh.Trimesh) -> List[Tuple[int, int]]:
        """Detect silhouette edges"""
        silhouette = []
        
        face_adjacency = mesh.face_adjacency
        face_normals = mesh.face_normals
        
        for edge_idx, (f1, f2) in enumerate(face_adjacency):
            n1, n2 = face_normals[f1], face_normals[f2]
            
            # Check if normals face away from each other
            if np.dot(n1, n2) < 0.3:  # Threshold for silhouette
                edge = mesh.face_adjacency_edges[edge_idx]
                silhouette.append(tuple(edge))
        
        return silhouette
    
    def _create_outline_mesh(self, mesh: trimesh.Trimesh, edges: List[Tuple[int, int]]) -> Optional[trimesh.Trimesh]:
        """Create mesh for outlines"""
        if not edges:
            return None
        
        outline_vertices = []
        outline_faces = []
        vertex_map = {}
        current_idx = 0
        
        for v1_idx, v2_idx in edges:
            v1 = mesh.vertices[v1_idx]
            v2 = mesh.vertices[v2_idx]
            n1 = mesh.vertex_normals[v1_idx]
            n2 = mesh.vertex_normals[v2_idx]
            
            # Extrude along normals
            offset = 0.02
            v1_out = v1 + n1 * offset
            v2_out = v2 + n2 * offset
            
            # Add vertices
            if v1_idx not in vertex_map:
                vertex_map[v1_idx] = current_idx
                outline_vertices.extend([v1, v1_out])
                current_idx += 2
            
            if v2_idx not in vertex_map:
                vertex_map[v2_idx] = current_idx
                outline_vertices.extend([v2, v2_out])
                current_idx += 2
            
            # Create quad faces
            i1 = vertex_map[v1_idx]
            i2 = vertex_map[v2_idx]
            outline_faces.extend([
                [i1, i1+1, i2],
                [i1+1, i2+1, i2]
            ])
        
        if outline_vertices:
            outline_mesh = trimesh.Trimesh(
                vertices=np.array(outline_vertices),
                faces=np.array(outline_faces)
            )
            outline_mesh.visual.vertex_colors = np.tile(self.outline_color + [255], (len(outline_vertices), 1))
            return outline_mesh
        
        return None