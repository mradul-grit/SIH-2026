import os
from pathlib import Path

# Dynamically resolve root directory of natraj26227
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parent.parent))

DATASETS_DIR = PROJECT_ROOT / "datasets"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
MODELS_DIR = PROJECT_ROOT / "models"
DATABASE_DIR = PROJECT_ROOT / "database"
LOGS_DIR = PROJECT_ROOT / "logs"
INVENTORY_FILE = PROJECT_ROOT / "dataset_inventory.json"
GUI_STATIC_DIR = PROJECT_ROOT / "project_code" / "gui" / "static"
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
