import spacy
import nltk
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ShapeType(Enum):
    CUBE = "cube"
    SPHERE = "sphere"
    CYLINDER = "cylinder"
    CONE = "cone"
    TORUS = "torus"
    PYRAMID = "pyramid"
    PLANE = "plane"
    COMPLEX = "complex"

@dataclass
class ObjectDescription:
    shape: ShapeType
    size: float
    color: Tuple[float, float, float]
    material: str
    texture: Optional[str]
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    properties: Dict[str, any]

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
        self.shape_keywords = {
            'cube': ShapeType.CUBE, 'box': ShapeType.CUBE, 'block': ShapeType.CUBE,
            'sphere': ShapeType.SPHERE, 'ball': ShapeType.SPHERE, 'orb': ShapeType.SPHERE,
            'cylinder': ShapeType.CYLINDER, 'tube': ShapeType.CYLINDER, 'pipe': ShapeType.CYLINDER,
            'cone': ShapeType.CONE, 'pyramid': ShapeType.PYRAMID,
            'torus': ShapeType.TORUS, 'donut': ShapeType.TORUS, 'ring': ShapeType.TORUS,
            'plane': ShapeType.PLANE, 'surface': ShapeType.PLANE, 'ground': ShapeType.PLANE
        }
        
        self.color_map = {
            'red': (1.0, 0.0, 0.0), 'green': (0.0, 1.0, 0.0), 'blue': (0.0, 0.0, 1.0),
            'yellow': (1.0, 1.0, 0.0), 'purple': (1.0, 0.0, 1.0), 'cyan': (0.0, 1.0, 1.0),
            'orange': (1.0, 0.5, 0.0), 'pink': (1.0, 0.75, 0.8), 'brown': (0.6, 0.3, 0.1),
            'black': (0.0, 0.0, 0.0), 'white': (1.0, 1.0, 1.0), 'gray': (0.5, 0.5, 0.5),
            'grey': (0.5, 0.5, 0.5), 'silver': (0.75, 0.75, 0.75), 'gold': (1.0, 0.84, 0.0)
        }
        
        self.size_modifiers = {
            'tiny': 0.2, 'small': 0.5, 'little': 0.4, 'mini': 0.3,
            'medium': 1.0, 'normal': 1.0, 'regular': 1.0,
            'large': 2.0, 'big': 2.0, 'huge': 3.0, 'giant': 4.0, 'massive': 5.0
        }
        
        self.materials = {
            'metal': 'metallic', 'wood': 'wooden', 'glass': 'transparent',
            'plastic': 'smooth', 'stone': 'rough', 'concrete': 'rough',
            'fabric': 'soft', 'leather': 'textured', 'rubber': 'elastic'
        }

    def parse_description(self, text: str) -> ObjectDescription:
        doc = self.nlp(text.lower())
        
        shape = self._extract_shape(doc)
        size = self._extract_size(doc)
        color = self._extract_color(doc)
        material = self._extract_material(doc)
        texture = self._extract_texture(doc)
        position = self._extract_position(doc)
        rotation = self._extract_rotation(doc)
        scale = self._extract_scale(doc)
        properties = self._extract_properties(doc)
        
        return ObjectDescription(
            shape=shape, size=size, color=color, material=material,
            texture=texture, position=position, rotation=rotation,
            scale=scale, properties=properties
        )

    def _extract_shape(self, doc) -> ShapeType:
        for token in doc:
            if token.lemma_ in self.shape_keywords:
                return self.shape_keywords[token.lemma_]
        
        # Complex shape detection
        if any(word in doc.text for word in ['building', 'house', 'tower']):
            return ShapeType.COMPLEX
        
        return ShapeType.CUBE

    def _extract_size(self, doc) -> float:
        for token in doc:
            if token.lemma_ in self.size_modifiers:
                return self.size_modifiers[token.lemma_]
        
        # Extract numeric values
        numbers = re.findall(r'\d+\.?\d*', doc.text)
        if numbers:
            return float(numbers[0])
        
        return 1.0

    def _extract_color(self, doc) -> Tuple[float, float, float]:
        for token in doc:
            if token.lemma_ in self.color_map:
                return self.color_map[token.lemma_]
        
        # RGB extraction
        rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', doc.text)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return (r/255.0, g/255.0, b/255.0)
        
        return (0.7, 0.7, 0.7)  # Default gray

    def _extract_material(self, doc) -> str:
        for token in doc:
            if token.lemma_ in self.materials:
                return self.materials[token.lemma_]
        return 'default'

    def _extract_texture(self, doc) -> Optional[str]:
        texture_words = ['smooth', 'rough', 'bumpy', 'shiny', 'matte', 'glossy']
        for token in doc:
            if token.lemma_ in texture_words:
                return token.lemma_
        return None

    def _extract_position(self, doc) -> Tuple[float, float, float]:
        x, y, z = 0.0, 0.0, 0.0
        
        # Positional keywords
        if 'left' in doc.text: x = -2.0
        elif 'right' in doc.text: x = 2.0
        if 'up' in doc.text or 'above' in doc.text: y = 2.0
        elif 'down' in doc.text or 'below' in doc.text: y = -2.0
        if 'front' in doc.text: z = 2.0
        elif 'back' in doc.text or 'behind' in doc.text: z = -2.0
        
        # Coordinate extraction
        coords = re.findall(r'at\s*\(([^)]+)\)', doc.text)
        if coords:
            try:
                x, y, z = map(float, coords[0].split(','))
            except:
                pass
        
        return (x, y, z)

    def _extract_rotation(self, doc) -> Tuple[float, float, float]:
        rx, ry, rz = 0.0, 0.0, 0.0
        
        if 'rotated' in doc.text or 'tilted' in doc.text:
            angles = re.findall(r'(\d+)\s*degrees?', doc.text)
            if angles:
                rx = float(angles[0])
        
        return (rx, ry, rz)

    def _extract_scale(self, doc) -> Tuple[float, float, float]:
        base_scale = self._extract_size(doc)
        
        # Aspect ratio detection
        if 'tall' in doc.text or 'high' in doc.text:
            return (base_scale, base_scale * 2, base_scale)
        elif 'wide' in doc.text or 'broad' in doc.text:
            return (base_scale * 2, base_scale, base_scale)
        elif 'flat' in doc.text or 'thin' in doc.text:
            return (base_scale, base_scale * 0.2, base_scale)
        
        return (base_scale, base_scale, base_scale)

    def _extract_properties(self, doc) -> Dict[str, any]:
        properties = {}
        
        # Physics properties
        if 'heavy' in doc.text: properties['mass'] = 10.0
        elif 'light' in doc.text: properties['mass'] = 0.1
        else: properties['mass'] = 1.0
        
        # Interaction properties
        if 'solid' in doc.text: properties['collision'] = True
        elif 'ghost' in doc.text or 'transparent' in doc.text: properties['collision'] = False
        else: properties['collision'] = True
        
        # Animation properties
        if 'spinning' in doc.text or 'rotating' in doc.text:
            properties['animate'] = 'rotate'
        elif 'floating' in doc.text or 'hovering' in doc.text:
            properties['animate'] = 'float'
        
        return properties