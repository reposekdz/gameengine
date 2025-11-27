# 3D Game Engine with AI Generation

A self-hosted game engine that generates 3D models from text descriptions and images without external APIs.

## Features

- **Text-to-3D Generation**: Create 3D models from natural language descriptions
- **Image-to-3D Conversion**: Generate 3D meshes from 2D images using depth estimation
- **Real-time Integration**: Seamlessly add generated models to the game environment
- **Web API**: REST endpoints and WebSocket support for remote generation
- **Self-hosted**: No external dependencies or API calls required

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game engine:
```bash
python main.py
```

3. Start the web server (optional):
```bash
python server/web_server.py
```

## API Usage

### Text Generation
```bash
curl -X POST http://localhost:5000/api/generate/text \
  -H "Content-Type: application/json" \
  -d '{"description": "large red cube"}'
```

### Image Generation
```bash
curl -X POST http://localhost:5000/api/generate/image \
  -F "image=@path/to/image.jpg"
```

## Architecture

- `engine/core/` - Core game engine components
- `engine/generators/` - 3D model generation modules
- `server/` - Web server and API endpoints
- `assets/` - Generated and uploaded assets

## Extending the Engine

The engine is designed for extensibility. Add new generators by implementing the base generation interface and registering them with the core engine.