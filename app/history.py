import json
from datetime import datetime
from pathlib import Path
from app.config import HISTORY_DIR
import uuid

def save_history_entry(data: dict):
    """Сохраняет запись в истории обработки"""
    entry_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    entry = {
        "id": entry_id,
        "timestamp": timestamp,
        **data
    }
    
    file_path = HISTORY_DIR / f"{entry_id}.json"
    with open(file_path, 'w') as f:
        json.dump(entry, f, indent=2)
    
    return entry

def get_history():
    """Возвращает всю историю обработки"""
    history = []
    for file in HISTORY_DIR.glob('*.json'):
        with open(file) as f:
            history.append(json.load(f))
    return sorted(history, key=lambda x: x['timestamp'], reverse=True)