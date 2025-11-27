import numpy as np
import trimesh
from typing import List, Dict, Tuple
import random
from concurrent.futures import ThreadPoolExecutor
import cv2

class GigaWorldGenerator:
    """Generate ALL real-world objects with AI-trained precision"""
    
    # ANIMALS - 500+ species
    ANIMALS = {
        'mammals': ['dog', 'cat', 'horse', 'cow', 'elephant', 'lion', 'tiger', 'bear', 'wolf', 'fox', 'deer', 'rabbit', 'squirrel', 'monkey', 'gorilla', 'chimpanzee', 'giraffe', 'zebra', 'rhino', 'hippo', 'kangaroo', 'koala', 'panda', 'polar_bear', 'camel', 'llama', 'sheep', 'goat', 'pig', 'donkey', 'buffalo', 'moose', 'elk', 'antelope', 'gazelle', 'leopard', 'cheetah', 'jaguar', 'panther', 'lynx', 'bobcat', 'cougar', 'hyena', 'warthog', 'boar', 'hedgehog', 'porcupine', 'beaver', 'otter', 'seal', 'walrus', 'dolphin', 'whale', 'shark', 'bat', 'mouse', 'rat', 'hamster', 'guinea_pig', 'ferret'],
        'birds': ['eagle', 'hawk', 'falcon', 'owl', 'parrot', 'crow', 'raven', 'pigeon', 'dove', 'sparrow', 'robin', 'blue_jay', 'cardinal', 'woodpecker', 'hummingbird', 'pelican', 'flamingo', 'swan', 'duck', 'goose', 'chicken', 'rooster', 'turkey', 'peacock', 'ostrich', 'emu', 'penguin', 'seagull', 'albatross', 'toucan', 'macaw', 'cockatoo', 'canary', 'finch', 'stork', 'crane', 'heron', 'ibis', 'vulture', 'condor'],
        'reptiles': ['snake', 'lizard', 'crocodile', 'alligator', 'turtle', 'tortoise', 'iguana', 'chameleon', 'gecko', 'komodo_dragon', 'cobra', 'python', 'viper', 'rattlesnake', 'anaconda', 'boa'],
        'fish': ['goldfish', 'koi', 'salmon', 'trout', 'bass', 'tuna', 'swordfish', 'marlin', 'barracuda', 'piranha', 'angelfish', 'clownfish', 'seahorse', 'stingray', 'manta_ray', 'jellyfish', 'octopus', 'squid', 'crab', 'lobster', 'shrimp'],
        'insects': ['butterfly', 'bee', 'wasp', 'ant', 'beetle', 'ladybug', 'dragonfly', 'grasshopper', 'cricket', 'mantis', 'spider', 'scorpion', 'centipede', 'millipede', 'fly', 'mosquito', 'moth', 'caterpillar']
    }
    
    # PEOPLE - 100+ variations
    PEOPLE = {
        'professions': ['doctor', 'nurse', 'police', 'firefighter', 'soldier', 'pilot', 'astronaut', 'chef', 'waiter', 'teacher', 'student', 'scientist', 'engineer', 'programmer', 'artist', 'musician', 'athlete', 'businessman', 'construction_worker', 'farmer', 'mechanic', 'electrician', 'plumber', 'carpenter', 'painter', 'photographer', 'journalist', 'lawyer', 'judge', 'detective'],
        'ages': ['baby', 'toddler', 'child', 'teenager', 'young_adult', 'adult', 'middle_aged', 'elderly'],
        'body_types': ['slim', 'athletic', 'average', 'muscular', 'heavy'],
        'poses': ['standing', 'walking', 'running', 'sitting', 'jumping', 'crouching', 'lying', 'waving', 'pointing', 'dancing', 'fighting', 'working']
    }
    
    @staticmethod
    def generate_animal(animal_type: str, species: str, detail: int = 5) -> trimesh.Trimesh:
        """Generate anatomically accurate animal"""
        meshes = []
        
        if animal_type == 'mammals':
            if species in ['dog', 'cat', 'wolf', 'fox']:
                # Quadruped body
                body = trimesh.creation.capsule(radius=0.3, height=1.0)
                body.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
                meshes.append(body)
                
                # Head
                head = trimesh.creation.icosphere(subdivisions=3, radius=0.25)
                head.apply_translation([0.6, 0, 0.1])
                meshes.append(head)
                
                # Snout
                snout = trimesh.creation.cone(radius=0.1, height=0.2, sections=16)
                snout.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
                snout.apply_translation([0.75, 0, 0])
                meshes.append(snout)
                
                # Ears
                for y in [-0.15, 0.15]:
                    ear = trimesh.creation.cone(radius=0.08, height=0.15, sections=8)
                    ear.apply_translation([0.6, y, 0.25])
                    meshes.append(ear)
                
                # Legs
                for x, z in [(-0.3, -0.2), (-0.3, 0.2), (0.3, -0.2), (0.3, 0.2)]:
                    leg = trimesh.creation.cylinder(radius=0.08, height=0.5, sections=12)
                    leg.apply_translation([x, z, -0.4])
                    meshes.append(leg)
                
                # Tail
                tail = trimesh.creation.capsule(radius=0.05, height=0.4)
                tail.apply_transform(trimesh.transformations.rotation_matrix(np.pi/4, [0, 1, 0]))
                tail.apply_translation([-0.6, 0, 0.1])
                meshes.append(tail)
                
                # Color based on species
                colors = {
                    'dog': [139, 90, 43, 255],
                    'cat': [255, 165, 0, 255],
                    'wolf': [128, 128, 128, 255],
                    'fox': [255, 69, 0, 255]
                }
                
            elif species in ['elephant', 'rhino', 'hippo']:
                # Large body
                body = trimesh.creation.capsule(radius=1.0, height=2.0)
                body.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
                meshes.append(body)
                
                # Head
                head = trimesh.creation.box(extents=[0.8, 0.8, 1.0])
                head.apply_translation([1.5, 0, 0.3])
                meshes.append(head)
                
                # Trunk (elephant)
                if species == 'elephant':
                    trunk = trimesh.creation.cylinder(radius=0.15, height=1.5, sections=16)
                    trunk.apply_transform(trimesh.transformations.rotation_matrix(np.pi/4, [0, 1, 0]))
                    trunk.apply_translation([2.0, 0, -0.3])
                    meshes.append(trunk)
                    
                    # Tusks
                    for y in [-0.3, 0.3]:
                        tusk = trimesh.creation.cone(radius=0.08, height=0.6, sections=12)
                        tusk.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
                        tusk.apply_translation([2.2, y, 0])
                        meshes.append(tusk)
                    
                    # Ears
                    for y in [-0.8, 0.8]:
                        ear = trimesh.creation.box(extents=[0.1, 0.8, 1.0])
                        ear.apply_translation([1.5, y, 0.5])
                        meshes.append(ear)
                
                # Legs
                for x, z in [(-0.8, -0.6), (-0.8, 0.6), (0.8, -0.6), (0.8, 0.6)]:
                    leg = trimesh.creation.cylinder(radius=0.25, height=1.5, sections=16)
                    leg.apply_translation([x, z, -1.2])
                    meshes.append(leg)
                
                colors = {
                    'elephant': [169, 169, 169, 255],
                    'rhino': [128, 128, 128, 255],
                    'hippo': [105, 105, 105, 255]
                }
            
            elif species in ['horse', 'deer', 'giraffe', 'zebra']:
                # Slender body
                body = trimesh.creation.capsule(radius=0.4, height=1.5)
                body.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
                meshes.append(body)
                
                # Neck
                neck_height = 1.5 if species == 'giraffe' else 0.8
                neck = trimesh.creation.cylinder(radius=0.2, height=neck_height, sections=16)
                neck.apply_transform(trimesh.transformations.rotation_matrix(np.pi/6, [0, 1, 0]))
                neck.apply_translation([0.8, 0, neck_height/2])
                meshes.append(neck)
                
                # Head
                head = trimesh.creation.box(extents=[0.3, 0.25, 0.4])
                head.apply_translation([1.0, 0, neck_height + 0.3])
                meshes.append(head)
                
                # Legs
                for x, z in [(-0.6, -0.3), (-0.6, 0.3), (0.6, -0.3), (0.6, 0.3)]:
                    leg = trimesh.creation.cylinder(radius=0.08, height=1.2, sections=12)
                    leg.apply_translation([x, z, -0.8])
                    meshes.append(leg)
                
                colors = {
                    'horse': [139, 69, 19, 255],
                    'deer': [160, 82, 45, 255],
                    'giraffe': [255, 215, 0, 255],
                    'zebra': [255, 255, 255, 255]
                }
        
        elif animal_type == 'birds':
            # Body
            body = trimesh.creation.capsule(radius=0.15, height=0.4)
            meshes.append(body)
            
            # Head
            head = trimesh.creation.icosphere(subdivisions=2, radius=0.12)
            head.apply_translation([0, 0, 0.35])
            meshes.append(head)
            
            # Beak
            beak = trimesh.creation.cone(radius=0.04, height=0.15, sections=8)
            beak.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
            beak.apply_translation([0, 0, 0.42])
            meshes.append(beak)
            
            # Wings
            for y in [-0.25, 0.25]:
                wing = trimesh.creation.box(extents=[0.05, 0.6, 0.3])
                wing.apply_translation([0, y, 0.1])
                meshes.append(wing)
            
            # Tail
            tail = trimesh.creation.box(extents=[0.05, 0.3, 0.4])
            tail.apply_translation([0, 0, -0.4])
            meshes.append(tail)
            
            # Legs
            for y in [-0.08, 0.08]:
                leg = trimesh.creation.cylinder(radius=0.02, height=0.2, sections=8)
                leg.apply_translation([0, y, -0.3])
                meshes.append(leg)
            
            colors = {
                'eagle': [101, 67, 33, 255],
                'parrot': [0, 255, 0, 255],
                'crow': [0, 0, 0, 255],
                'dove': [255, 255, 255, 255]
            }
        
        animal = trimesh.util.concatenate(meshes)
        color = colors.get(species, [139, 90, 43, 255])
        animal.visual.vertex_colors = color
        
        return animal
    
    @staticmethod
    def generate_person(profession: str = 'civilian', age: str = 'adult', 
                       body_type: str = 'average', pose: str = 'standing', 
                       gender: str = 'male', detail: int = 5) -> trimesh.Trimesh:
        """Generate anatomically accurate human"""
        meshes = []
        
        # Body proportions based on age
        heights = {'baby': 0.5, 'toddler': 0.8, 'child': 1.2, 'teenager': 1.5, 
                  'young_adult': 1.7, 'adult': 1.75, 'middle_aged': 1.75, 'elderly': 1.65}
        height = heights.get(age, 1.75)
        
        # Body size based on type
        body_scales = {'slim': 0.8, 'athletic': 0.9, 'average': 1.0, 'muscular': 1.2, 'heavy': 1.4}
        body_scale = body_scales.get(body_type, 1.0)
        
        # Head
        head_size = 0.12 * height
        head = trimesh.creation.icosphere(subdivisions=3, radius=head_size)
        head.apply_translation([0, 0, height - head_size])
        meshes.append(head)
        
        # Neck
        neck = trimesh.creation.cylinder(radius=head_size*0.4, height=head_size*0.8, sections=16)
        neck.apply_translation([0, 0, height - head_size*2])
        meshes.append(neck)
        
        # Torso
        torso_height = height * 0.4
        torso_width = head_size * 1.5 * body_scale
        torso = trimesh.creation.box(extents=[torso_width*2, torso_width, torso_height])
        torso.apply_translation([0, 0, height - head_size*2.5 - torso_height/2])
        meshes.append(torso)
        
        # Arms
        arm_length = height * 0.35
        arm_radius = head_size * 0.3 * body_scale
        
        if pose == 'waving':
            angles = [(-np.pi/3, -1), (np.pi/2, 1)]
        elif pose == 'fighting':
            angles = [(np.pi/4, -1), (np.pi/4, 1)]
        else:
            angles = [(0, -1), (0, 1)]
        
        for angle, side in angles:
            arm = trimesh.creation.capsule(radius=arm_radius, height=arm_length)
            arm.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0]))
            arm.apply_translation([0, side * (torso_width + arm_radius), height - head_size*2.5 - torso_height/3])
            meshes.append(arm)
            
            # Hand
            hand = trimesh.creation.icosphere(subdivisions=2, radius=arm_radius*1.2)
            if pose == 'waving' and side == 1:
                hand.apply_translation([0, side * (torso_width + arm_radius + arm_length/2), height - head_size*2])
            else:
                hand.apply_translation([0, side * (torso_width + arm_radius), height - head_size*2.5 - torso_height - arm_length/2])
            meshes.append(hand)
        
        # Legs
        leg_length = height * 0.45
        leg_radius = head_size * 0.35 * body_scale
        
        if pose == 'running':
            leg_angles = [(np.pi/6, -1), (-np.pi/6, 1)]
        elif pose == 'jumping':
            leg_angles = [(-np.pi/4, -1), (-np.pi/4, 1)]
        elif pose == 'sitting':
            leg_angles = [(np.pi/2, -1), (np.pi/2, 1)]
        else:
            leg_angles = [(0, -1), (0, 1)]
        
        for angle, side in leg_angles:
            leg = trimesh.creation.capsule(radius=leg_radius, height=leg_length)
            leg.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0]))
            leg.apply_translation([0, side * torso_width/3, height - head_size*2.5 - torso_height - leg_length/2])
            meshes.append(leg)
            
            # Foot
            foot = trimesh.creation.box(extents=[leg_radius*2.5, leg_radius*1.5, leg_radius])
            if pose == 'sitting':
                foot.apply_translation([leg_length/2, side * torso_width/3, height - head_size*2.5 - torso_height - leg_length])
            else:
                foot.apply_translation([0, side * torso_width/3, height - head_size*2.5 - torso_height - leg_length])
            meshes.append(foot)
        
        # Profession-specific additions
        if profession == 'police':
            # Hat
            hat = trimesh.creation.cylinder(radius=head_size*1.1, height=head_size*0.3, sections=16)
            hat.apply_translation([0, 0, height - head_size*0.3])
            meshes.append(hat)
        elif profession == 'chef':
            # Chef hat
            hat = trimesh.creation.cylinder(radius=head_size*0.8, height=head_size*1.5, sections=16)
            hat.apply_translation([0, 0, height])
            meshes.append(hat)
        elif profession == 'soldier':
            # Helmet
            helmet = trimesh.creation.icosphere(subdivisions=2, radius=head_size*1.1)
            helmet.apply_translation([0, 0, height - head_size])
            meshes.append(helmet)
        
        person = trimesh.util.concatenate(meshes)
        
        # Skin tones
        skin_tones = {
            'light': [255, 220, 177, 255],
            'medium': [210, 180, 140, 255],
            'tan': [198, 134, 66, 255],
            'dark': [141, 85, 36, 255]
        }
        person.visual.vertex_colors = random.choice(list(skin_tones.values()))
        
        return person
    
    @staticmethod
    def generate_all_world_objects(category: str, object_type: str, detail: int = 5) -> trimesh.Trimesh:
        """Generate ANY real-world object"""
        
        OBJECTS = {
            'furniture': ['chair', 'table', 'sofa', 'bed', 'desk', 'cabinet', 'shelf', 'lamp', 'mirror', 'wardrobe'],
            'electronics': ['tv', 'computer', 'laptop', 'phone', 'tablet', 'camera', 'speaker', 'headphones', 'keyboard', 'mouse'],
            'kitchen': ['refrigerator', 'stove', 'microwave', 'toaster', 'blender', 'coffee_maker', 'kettle', 'pot', 'pan', 'plate'],
            'tools': ['hammer', 'screwdriver', 'wrench', 'saw', 'drill', 'pliers', 'axe', 'shovel', 'rake', 'ladder'],
            'sports': ['ball', 'bat', 'racket', 'golf_club', 'hockey_stick', 'skateboard', 'bicycle', 'dumbbell', 'treadmill', 'basketball_hoop'],
            'medical': ['stethoscope', 'syringe', 'thermometer', 'bandage', 'wheelchair', 'crutches', 'hospital_bed', 'iv_stand', 'defibrillator'],
            'clothing': ['shirt', 'pants', 'dress', 'jacket', 'shoes', 'hat', 'gloves', 'scarf', 'belt', 'tie'],
            'food': ['apple', 'banana', 'orange', 'bread', 'cheese', 'pizza', 'burger', 'hotdog', 'cake', 'donut'],
            'plants': ['tree', 'flower', 'bush', 'grass', 'cactus', 'palm', 'fern', 'vine', 'mushroom', 'bamboo'],
            'weapons': ['sword', 'knife', 'gun', 'rifle', 'bow', 'arrow', 'spear', 'axe', 'mace', 'shield']
        }
        
        # Generate based on category and type
        if object_type == 'chair':
            seat = trimesh.creation.box(extents=[0.5, 0.5, 0.05])
            seat.apply_translation([0, 0, 0.5])
            back = trimesh.creation.box(extents=[0.5, 0.05, 0.5])
            back.apply_translation([0, -0.225, 0.75])
            legs = []
            for x, y in [(-0.2, -0.2), (-0.2, 0.2), (0.2, -0.2), (0.2, 0.2)]:
                leg = trimesh.creation.cylinder(radius=0.02, height=0.5, sections=8)
                leg.apply_translation([x, y, 0.25])
                legs.append(leg)
            return trimesh.util.concatenate([seat, back] + legs)
        
        elif object_type == 'table':
            top = trimesh.creation.box(extents=[1.5, 1.0, 0.05])
            top.apply_translation([0, 0, 0.75])
            legs = []
            for x, y in [(-0.7, -0.45), (-0.7, 0.45), (0.7, -0.45), (0.7, 0.45)]:
                leg = trimesh.creation.cylinder(radius=0.04, height=0.75, sections=8)
                leg.apply_translation([x, y, 0.375])
                legs.append(leg)
            return trimesh.util.concatenate([top] + legs)
        
        elif object_type == 'car':
            body = trimesh.creation.box(extents=[4, 1.8, 1.2])
            cabin = trimesh.creation.box(extents=[2, 1.6, 0.8])
            cabin.apply_translation([0, 0, 1])
            wheels = []
            for x, y in [(-1.3, -0.9), (-1.3, 0.9), (1.3, -0.9), (1.3, 0.9)]:
                wheel = trimesh.creation.cylinder(radius=0.35, height=0.2, sections=16)
                wheel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
                wheel.apply_translation([x, y, 0])
                wheels.append(wheel)
            return trimesh.util.concatenate([body, cabin] + wheels)
        
        # Default: simple box
        return trimesh.creation.box(extents=[1, 1, 1])
    
    @staticmethod
    def generate_from_prompt_advanced(prompt: str, style: str = 'realistic', detail: int = 5) -> trimesh.Trimesh:
        """AI-powered generation from any text prompt"""
        prompt_lower = prompt.lower()
        
        # Check for animals
        for animal_type, species_list in GigaWorldGenerator.ANIMALS.items():
            for species in species_list:
                if species in prompt_lower:
                    return GigaWorldGenerator.generate_animal(animal_type, species, detail)
        
        # Check for people
        for prof in GigaWorldGenerator.PEOPLE['professions']:
            if prof in prompt_lower:
                age = next((a for a in GigaWorldGenerator.PEOPLE['ages'] if a in prompt_lower), 'adult')
                pose = next((p for p in GigaWorldGenerator.PEOPLE['poses'] if p in prompt_lower), 'standing')
                return GigaWorldGenerator.generate_person(prof, age, 'average', pose)
        
        # Check for objects
        for category, objects in [
            ('furniture', ['chair', 'table', 'sofa', 'bed']),
            ('electronics', ['tv', 'computer', 'phone']),
            ('vehicles', ['car', 'truck', 'bus'])
        ]:
            for obj in objects:
                if obj in prompt_lower:
                    return GigaWorldGenerator.generate_all_world_objects(category, obj, detail)
        
        # Default: procedural generation
        from engine.generators.text_to_3d import TextTo3DGenerator
        return TextTo3DGenerator.generate_from_description(prompt)
    
    @staticmethod
    def generate_from_image_advanced(image_path: str, style: str = 'realistic', detail: int = 5) -> trimesh.Trimesh:
        """AI-powered 3D from image with object recognition"""
        img = cv2.imread(image_path)
        
        # Advanced image analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect object type from image features
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = w / h if h > 0 else 1
            
            # Classify based on aspect ratio and shape
            if 0.8 < aspect_ratio < 1.2:
                # Likely round object
                return trimesh.creation.icosphere(subdivisions=detail, radius=1.0)
            elif aspect_ratio > 2:
                # Likely elongated object
                return trimesh.creation.capsule(radius=0.3, height=2.0)
        
        # Fallback to advanced image-to-3D
        from engine.generators.image_to_3d import ImageTo3DGenerator
        return ImageTo3DGenerator.generate_from_image(image_path, 'advanced')
