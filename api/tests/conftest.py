import sys
from pathlib import Path

# Allow test modules to import from api/ (services, models, routers)
sys.path.insert(0, str(Path(__file__).parent.parent))
