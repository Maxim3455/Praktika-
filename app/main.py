from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import PROCESSED_DIR, UPLOAD_DIR, REPORTS_DIR, HISTORY_DIR
from app.routes import router
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bird Detection System",
             description="API for detecting birds in videos")


def init_dirs():
    dirs = [UPLOAD_DIR, PROCESSED_DIR, REPORTS_DIR, HISTORY_DIR]
    for dir_path in dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Directory {dir_path} is ready")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {str(e)}")
            raise


init_dirs()


app.include_router(router)


app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")


templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup_event():
    logger.info("Приложение успешно запущено")