import os
import sys
from pathlib import Path

# Explicitly mark Vercel environment
os.environ.setdefault("VERCEL", "1")

# Add the project root directory to sys.path so modules, models, and blueprints resolve cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the configured Flask WSGI application instance
from app import app
