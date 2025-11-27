import cv2
import numpy as np
import trimesh
from PIL import Image, ImageFilter, ImageEnhance
from typing import Optional, Tuple, List
import torch
import torchvision.transforms as transforms
from sklearn.cluster import KMeans
from scipy import ndimage
from skimage import measure, morphology, segmentation
import open3d as o3d

class ImageTo3DGenerator:
    def __init__(self):
        self.depth_scale = 0.2
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def generate_from_image(self, image_path: str, method: str = 'advanced') -> trimesh.Trimesh:
        """Generate 3D model from image using advanced depth estimation"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        if method == 'advanced':
            return self._advanced_generation(image)
        elif method == 'photogrammetry':
            return self._photogrammetry_style(image)
        elif method == 'volumetric':
            return self._volumetric_reconstruction(image)
        else:
            return self._basic_generation(image)
    
    def _advanced_generation(self, image: np.ndarray) -> trimesh.Trimesh:
        """Advanced 3D generation with multiple techniques"""
        # Multi-scale depth estimation
        depth_maps = self._multi_scale_depth(image)
        
        # Edge-aware depth refinement
        refined_depth = self._refine_depth_edges(depth_maps, image)
        
        # Semantic segmentation for better structure
        segments = self._semantic_segmentation(image)
        
        # Generate mesh with improved topology
        mesh = self._advanced_mesh_generation(refined_depth, image, segments)
        
        # Post-processing
        mesh = self._mesh_post_processing(mesh)
        
        return mesh
    
    def _multi_scale_depth(self, image: np.ndarray) -> List[np.ndarray]:
        """Generate depth maps at multiple scales"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        depth_maps = []
        
        scales = [1.0, 0.5, 0.25]
        for scale in scales:
            if scale != 1.0:
                h, w = gray.shape
                scaled = cv2.resize(gray, (int(w*scale), int(h*scale)))
            else:
                scaled = gray
            
            # Enhanced depth estimation
            depth = self._enhanced_depth_estimation(scaled)
            
            if scale != 1.0:
                depth = cv2.resize(depth, (gray.shape[1], gray.shape[0]))
            
            depth_maps.append(depth)
        
        return depth_maps
    
    def _enhanced_depth_estimation(self, gray_image: np.ndarray) -> np.ndarray:
        """Enhanced depth estimation using multiple cues"""
        # Gradient-based depth
        grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Texture-based depth
        texture = cv2.Laplacian(gray_image, cv2.CV_64F)
        texture = np.abs(texture)
        
        # Intensity-based depth (traditional)
        intensity_depth = gray_image.astype(np.float32) / 255.0
        
        # Combine depth cues
        combined_depth = (
            0.4 * intensity_depth +
            0.3 * (gradient_magnitude / gradient_magnitude.max()) +
            0.3 * (texture / texture.max())
        )
        
        # Apply bilateral filter for edge preservation
        combined_depth = cv2.bilateralFilter(combined_depth.astype(np.float32), 9, 75, 75)
        
        return combined_depth * self.depth_scale
    
    def _refine_depth_edges(self, depth_maps: List[np.ndarray], image: np.ndarray) -> np.ndarray:
        """Refine depth using edge information"""
        # Detect edges in original image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Combine multi-scale depth maps
        base_depth = depth_maps[0]
        for depth_map in depth_maps[1:]:
            base_depth = 0.7 * base_depth + 0.3 * depth_map
        
        # Edge-aware smoothing
        refined_depth = base_depth.copy()
        edge_mask = edges > 0
        
        # Preserve depth discontinuities at edges
        kernel = np.ones((3, 3), np.float32) / 9
        smoothed = cv2.filter2D(base_depth, -1, kernel)
        refined_depth[~edge_mask] = smoothed[~edge_mask]
        
        return refined_depth
    
    def _semantic_segmentation(self, image: np.ndarray) -> np.ndarray:
        """Basic semantic segmentation for structure understanding"""
        # Convert to LAB color space for better segmentation
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # K-means clustering for region segmentation
        data = lab.reshape((-1, 3))
        kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data)
        
        segmented = labels.reshape(image.shape[:2])
        
        # Morphological operations to clean up segments
        segmented = morphology.closing(segmented, morphology.disk(3))
        segmented = morphology.opening(segmented, morphology.disk(2))
        
        return segmented
    
    def _advanced_mesh_generation(self, depth_map: np.ndarray, image: np.ndarray, segments: np.ndarray) -> trimesh.Trimesh:
        """Generate mesh with improved topology"""
        h, w = depth_map.shape
        
        # Adaptive resolution based on depth variation
        depth_variance = ndimage.generic_filter(depth_map, np.var, size=5)
        high_detail_mask = depth_variance > np.percentile(depth_variance, 75)
        
        vertices = []
        faces = []
        colors = []
        
        # Generate vertices with adaptive sampling
        vertex_map = np.full((h, w), -1, dtype=int)
        vertex_count = 0
        
        for i in range(0, h, 1):
            for j in range(0, w, 1):
                # Skip vertices in low-detail areas (subsample)
                if not high_detail_mask[i, j] and (i % 2 != 0 or j % 2 != 0):
                    continue
                
                x = (j / w - 0.5) * 2
                y = (i / h - 0.5) * 2
                z = depth_map[i, j]
                
                vertices.append([x, -y, z])  # Flip Y for correct orientation
                colors.append(image[i, j] / 255.0)
                vertex_map[i, j] = vertex_count
                vertex_count += 1
        
        # Generate faces with better triangulation
        for i in range(h - 1):
            for j in range(w - 1):
                # Get vertex indices
                v1 = vertex_map[i, j]
                v2 = vertex_map[i, j + 1]
                v3 = vertex_map[i + 1, j]
                v4 = vertex_map[i + 1, j + 1]
                
                # Skip if any vertex is missing
                if v1 == -1 or v2 == -1 or v3 == -1 or v4 == -1:
                    continue
                
                # Create triangles with better aspect ratios
                depth_diff1 = abs(depth_map[i, j] - depth_map[i + 1, j + 1])
                depth_diff2 = abs(depth_map[i, j + 1] - depth_map[i + 1, j])
                
                if depth_diff1 < depth_diff2:
                    faces.extend([[v1, v2, v4], [v1, v4, v3]])
                else:
                    faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
        
        # Add vertex colors
        if colors:
            mesh.visual.vertex_colors = np.array(colors)
        
        return mesh
    
    def _photogrammetry_style(self, image: np.ndarray) -> trimesh.Trimesh:
        """Generate 3D model using photogrammetry-inspired techniques"""
        # Feature detection and matching (simulated)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # SIFT features for key points
        sift = cv2.SIFT_create()
        keypoints, descriptors = sift.detectAndCompute(gray, None)
        
        # Create depth based on feature density
        feature_map = np.zeros_like(gray, dtype=np.float32)
        for kp in keypoints:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
                feature_map[y, x] = kp.response
        
        # Smooth feature map
        feature_map = cv2.GaussianBlur(feature_map, (15, 15), 0)
        
        # Combine with intensity depth
        intensity_depth = gray.astype(np.float32) / 255.0
        combined_depth = 0.6 * intensity_depth + 0.4 * (feature_map / feature_map.max())
        
        return self._depth_to_mesh(combined_depth * self.depth_scale, image)
    
    def _volumetric_reconstruction(self, image: np.ndarray) -> trimesh.Trimesh:
        """Volumetric reconstruction approach"""
        # Create voxel grid from image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Threshold for solid voxels
        threshold = np.mean(gray)
        solid_mask = gray > threshold
        
        # Create 3D volume
        depth_layers = 32
        volume = np.zeros((gray.shape[0], gray.shape[1], depth_layers), dtype=bool)
        
        for z in range(depth_layers):
            # Vary threshold by depth
            layer_threshold = threshold * (1 - z / depth_layers * 0.5)
            volume[:, :, z] = gray > layer_threshold
        
        # Extract isosurface using marching cubes
        try:
            vertices, faces, _, _ = measure.marching_cubes(volume.astype(float), level=0.5)
            
            # Scale and center
            vertices[:, 0] = (vertices[:, 0] / gray.shape[0] - 0.5) * 2
            vertices[:, 1] = (vertices[:, 1] / gray.shape[1] - 0.5) * 2
            vertices[:, 2] = vertices[:, 2] / depth_layers * self.depth_scale
            
            return trimesh.Trimesh(vertices=vertices, faces=faces)
        except:
            # Fallback to basic method
            return self._basic_generation(image)
    
    def _basic_generation(self, image: np.ndarray) -> trimesh.Trimesh:
        """Basic depth-based generation (fallback)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        depth_map = self._create_depth_map(gray)
        return self._depth_to_mesh(depth_map, image)
    
    def _create_depth_map(self, image: np.ndarray) -> np.ndarray:
        """Create enhanced depth map from grayscale image"""
        normalized = image.astype(np.float32) / 255.0
        
        # Multi-pass filtering
        blurred = cv2.bilateralFilter(normalized, 9, 75, 75)
        blurred = cv2.GaussianBlur(blurred, (5, 5), 0)
        
        return blurred * self.depth_scale
    
    def _depth_to_mesh(self, depth_map: np.ndarray, image: np.ndarray) -> trimesh.Trimesh:
        """Convert depth map to 3D mesh with colors"""
        h, w = depth_map.shape
        
        # Create vertex grid
        x, y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
        vertices = np.column_stack([x.flatten(), -y.flatten(), depth_map.flatten()])
        
        # Extract colors
        if len(image.shape) == 3:
            colors = image.reshape(-1, 3) / 255.0
        else:
            colors = np.tile(image.reshape(-1, 1) / 255.0, (1, 3))
        
        # Create faces
        faces = []
        for i in range(h - 1):
            for j in range(w - 1):
                v1 = i * w + j
                v2 = i * w + (j + 1)
                v3 = (i + 1) * w + j
                v4 = (i + 1) * w + (j + 1)
                
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces))
        mesh.visual.vertex_colors = colors
        
        return mesh
    
    def _mesh_post_processing(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Post-process mesh for better quality"""
        # Remove degenerate faces
        mesh.remove_degenerate_faces()
        
        # Remove duplicate vertices
        mesh.merge_vertices()
        
        # Smooth if needed
        if len(mesh.vertices) < 10000:  # Only smooth smaller meshes
            mesh = mesh.smoothed()
        
        # Fix normals
        mesh.fix_normals()
        
        return mesh