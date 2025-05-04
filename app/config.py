import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


UPLOAD_DIR = BASE_DIR / "uploads"        
PROCESSED_DIR = BASE_DIR / "processed"   
HISTORY_DIR = BASE_DIR / "history"       
REPORTS_DIR = BASE_DIR / "reports"       


MODEL_NAME = "yolov8n.pt"  
BIRD_ID = 14               


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)