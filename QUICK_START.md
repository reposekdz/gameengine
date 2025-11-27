# GIGA ENGINE - QUICK START GUIDE

## 5-Minute Setup to Universe-Scale Generation

### Step 1: Install Dependencies (2 minutes)

```bash
cd "c:\Users\yy9\Downloads\game engine"
pip install -r requirements.txt
```

### Step 2: Setup MySQL Database (2 minutes)

**Option A - Quick Setup (No Password):**
```bash
# Install MySQL, then:
mysql -u root -e "CREATE DATABASE giga_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root giga_engine < database/schema.sql
```

**Option B - With Password:**
```bash
mysql -u root -p
# Enter password, then:
CREATE DATABASE giga_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SOURCE c:/Users/yy9/Downloads/game engine/database/schema.sql;
exit;
```

**Configure Connection:**
Edit `database/models/db_manager.py` line 27:
```python
password="YOUR_PASSWORD"  # Change from "" to your password
```

### Step 3: Start Server (1 minute)

```bash
python server/web_server.py
```

Server runs at: http://localhost:5000

API Docs: http://localhost:5000/docs

### Test It Works

**Generate Planet:**
```bash
curl -X POST http://localhost:5000/api/giga/generate-planet -H "Content-Type: application/json" -d "{\"radius\": 6371, \"detail\": 5}"
```

**Generate Mega City:**
```bash
curl -X POST http://localhost:5000/api/giga/generate-mega-city -H "Content-Type: application/json" -d "{\"size\": [1000, 1000], \"style\": \"gta\"}"
```

**Generate Vehicle Fleet:**
```bash
curl -X POST http://localhost:5000/api/giga/generate-vehicle-fleet -H "Content-Type: application/json" -d "{\"count\": 100, \"vehicle_type\": \"mixed\"}"
```

**Get Statistics:**
```bash
curl http://localhost:5000/api/giga/stats
```

### Python Usage

```python
# Generate Universe
from engine.generators.giga_generator import GigaGenerator
universe = GigaGenerator.generate_universe(size=50000, galaxies=100)

# Generate Planet
planet = GigaGenerator.generate_planet(radius=6371, detail=6)
planet.export("planet.glb")

# Generate Mega City
from engine.procedural.mega_city_generator import MegaCityGenerator
city = MegaCityGenerator.generate_mega_city((5000, 5000), 0.9)

# Generate Cartoon Scene
from engine.core.cartoon_engine import CartoonEngine
from engine.generators.text_to_3d import TextTo3DGenerator

car = TextTo3DGenerator.generate_from_description("red sports car")
building = TextTo3DGenerator.generate_from_description("tall building")

scene = CartoonEngine.generate_cartoon_scene([
    {'mesh': car, 'position': [0, 0, 0]},
    {'mesh': building, 'position': [10, 0, 0]}
], style='toon')

scene.export("cartoon_scene.glb")

# Database Operations
from database.models.db_manager import GigaDBManager
db = GigaDBManager()

# Store asset
asset_uuid = db.insert_asset(
    name="Red Sports Car",
    category="vehicle",
    asset_type="car",
    style="realistic",
    vertices=50000,
    faces=100000,
    files={'glb': 'assets/car.glb'},
    metadata={'color': 'red'},
    tags=['vehicle', 'car', 'red']
)

# Search assets
vehicles = db.search_assets(category='vehicle', limit=100)

# Get stats
stats = db.get_stats()
print(f"Total assets: {stats['total_assets']}")
```

### Common Issues

**MySQL Connection Error:**
- Check MySQL is running: `net start MySQL80` (Windows)
- Verify password in `database/models/db_manager.py`

**Import Error:**
- Run: `pip install -r requirements.txt`

**Port Already in Use:**
- Change port in `server/web_server.py` line 558: `port=5000` → `port=8000`

### Next Steps

1. **Read Full Documentation**: See `GIGA_README.md`
2. **Database Guide**: See `DATABASE_SETUP.md`
3. **API Reference**: Visit http://localhost:5000/docs
4. **Examples**: Check generated files in `assets/` folder

### Performance Tips

- **Parallel Generation**: Use `ThreadPoolExecutor` for batch operations
- **Caching**: Enable database caching for 80% faster retrieval
- **GPU**: Install CUDA for faster processing (optional)
- **Memory**: Increase for larger generations (16GB+ recommended)

### What You Can Generate

| Feature | Command | Time |
|---------|---------|------|
| Single Object | `TextTo3DGenerator.generate_from_description("car")` | <0.1s |
| 3 Objects | Multi-input API | <0.5s |
| Small City | `generate_mega_city([1000, 1000])` | ~10s |
| Large City | `generate_mega_city([5000, 5000])` | ~60s |
| Vehicle Fleet | `generate_vehicle_fleet(1000)` | ~5s |
| Character Army | `generate_character_army(10000)` | ~15s |
| Planet | `generate_planet(6371, 6)` | ~30s |
| Universe | `generate_universe(50000, 100)` | ~60s |

### Support

- **Documentation**: All `.md` files in root directory
- **API Docs**: http://localhost:5000/docs (interactive)
- **Database**: See `DATABASE_SETUP.md` for complete guide

---

**You're ready to generate at GIGA scale! 🚀**
