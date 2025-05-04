from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import aiofiles
from pathlib import Path
from datetime import datetime
import json
import uuid
import logging
import os

from app.video_processor import VideoProcessor
from app.config import UPLOAD_DIR, PROCESSED_DIR, HISTORY_DIR, REPORTS_DIR
from app.reports import generate_pdf_report, generate_excel_report

router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

def save_history(data: dict) -> dict:
    
    os.makedirs(HISTORY_DIR, exist_ok=True)
    entry_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    history_entry = {
        "id": entry_id,
        "timestamp": timestamp,
        **data
    }
    
    history_file = HISTORY_DIR / f"{entry_id}.json"
    with open(history_file, "w", encoding='utf-8') as f:
        json.dump(history_entry, f, indent=2, ensure_ascii=False)
    
    return history_entry

def load_history() -> list:
   
    history = []
    if HISTORY_DIR.exists():
        for file in sorted(HISTORY_DIR.glob("*.json")):
            try:
                with open(file, encoding='utf-8') as f:
                    history.append(json.load(f))
            except Exception as e:
                logger.error(f"Ошибка при загрузке файла истории {file}: {str(e)}")
    return sorted(history, key=lambda x: x["timestamp"], reverse=True)

@router.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)

        video_id = str(int(datetime.now().timestamp()))
        original_filename = file.filename
        processed_filename = f"{video_id}.mp4"
        
        
        video_path = UPLOAD_DIR / processed_filename
        async with aiofiles.open(video_path, "wb") as f:
            await f.write(await file.read())
        
        
        output_path = PROCESSED_DIR / processed_filename
        processor = VideoProcessor()
        result = processor.process_video(video_path, output_path)
        
        
        history_entry = save_history({
            "original_filename": original_filename,
            "processed_filename": processed_filename,
            "max_birds": result["max_birds"],
            "total_frames": result["total_frames"],
            "detections": result["detections"]
        })
        
        
        try:
            pdf_path = generate_pdf_report(history_entry)
            excel_path = generate_excel_report(history_entry)
            logger.info(f"Успешно сгенерированные отчеты: PDF={pdf_path}, Excel={excel_path}")
        except Exception as e:
            logger.error(f"Не удалось сгенерировать отчет: {str(e)}")
            raise HTTPException(500, detail=f"Не удалось сгенерировать отчет: {str(e)}")
        
        return {"status": "success", "video_id": video_id}
    
    except Exception as e:
        logger.error(f"Ошибка загрузки: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=str(e))

@router.get("/report/pdf/{entry_id}")
async def download_pdf_report(entry_id: str):
    
    report_path = REPORTS_DIR / f"report_{entry_id}.pdf"
    
    if not report_path.exists():
        
        try:
            history = load_history()
            entry = next((e for e in history if e["id"] == entry_id), None)
            
            if entry:
                report_path = generate_pdf_report(entry)
                logger.info(f"Восстановленный отчет в формате PDF: {report_path}")
            else:
                raise HTTPException(404, detail="История не была найдена")
        except Exception as e:
            logger.error(f"Failed to regenerate PDF: {str(e)}")
            raise HTTPException(404, detail="Отчет в формате PDF не найден, и восстановление завершилось неудачно")
    
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=f"bird_report_{entry_id}.pdf"
    )

@router.get("/report/excel/{entry_id}")
async def download_excel_report(entry_id: str):
    
    report_path = REPORTS_DIR / f"report_{entry_id}.xlsx"
    
    if not report_path.exists():
        
        try:
            history = load_history()
            entry = next((e for e in history if e["id"] == entry_id), None)
            
            if entry:
                report_path = generate_excel_report(entry)
                logger.info(f"Regenerated Excel report: {report_path}")
            else:
                raise HTTPException(404, detail="History entry not found")
        except Exception as e:
            logger.error(f"Failed to regenerate Excel: {str(e)}")
            raise HTTPException(404, detail="Excel report not found and regeneration failed")
    
    return FileResponse(
        report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"bird_report_{entry_id}.xlsx"
    )


@router.get("/results/{video_id}", response_class=HTMLResponse)
async def show_results(request: Request, video_id: str):
    history = load_history()
    entry = next((e for e in history if e["processed_filename"] == f"{video_id}.mp4"), None)
    
    if not entry:
        raise HTTPException(404, detail="Video not found")
    
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "video_id": video_id,
            "video_info": entry,
            "video_url": f"/processed/{entry['processed_filename']}",
            "show_history_button": True
        }
    )

@router.post("/history/delete/{entry_id}")
async def delete_history_entry(entry_id: str):
    try:
        history_file = HISTORY_DIR / f"{entry_id}.json"
        
        
        history = load_history()
        entry = next((e for e in history if e["id"] == entry_id), None)
        video_file = None
        
        if entry:
            video_file = PROCESSED_DIR / entry["processed_filename"]
        
        
        if history_file.exists():
            history_file.unlink()
        
        
        if video_file and video_file.exists():
            video_file.unlink()
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Delete error: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=str(e))

@router.get("/history", response_class=HTMLResponse)
async def show_history(request: Request):
    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "history": load_history(),
            "show_upload_button": True
        }
    )

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "show_history_button": True
        }
    )