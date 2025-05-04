import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Important directories
UPLOAD_DIR = BASE_DIR / "uploads"        # For original videos
PROCESSED_DIR = BASE_DIR / "processed"   # For processed videos with detections
HISTORY_DIR = BASE_DIR / "history"       # For processing history JSON files
REPORTS_DIR = BASE_DIR / "reports"       # For generated reports (PDF/Excel)

# Model configuration
MODEL_NAME = "yolov8n.pt"  # YOLOv8 nano model
BIRD_ID = 14               # COCO dataset class ID for birds

# Ensure directories exist on import
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)