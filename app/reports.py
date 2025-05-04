from fpdf import FPDF
import pandas as pd
from pathlib import Path
from app.config import REPORTS_DIR
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_pdf_report(history_entry: dict) -> Path:
   
    try:
        
        required_fields = ['id', 'original_filename', 'timestamp', 'max_birds', 'detections']
        for field in required_fields:
            if field not in history_entry:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(history_entry['detections'], list):
            raise ValueError("Detections should be a list")
        
        
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        
        pdf.cell(200, 10, txt="Bird Detection Report", ln=1, align='C')
        pdf.ln(10)
        
        
        pdf.cell(200, 10, txt=f"File: {history_entry['original_filename']}", ln=1)
        pdf.cell(200, 10, txt=f"Processing Date: {history_entry['timestamp']}", ln=1)
        pdf.cell(200, 10, txt=f"Maximum Birds in Frame: {history_entry['max_birds']}", ln=1)
        pdf.cell(200, 10, txt=f"Total Frames Processed: {history_entry['total_frames']}", ln=1)
        pdf.ln(15)
        
        
        pdf.cell(200, 10, txt="Frame-by-Frame Detection Results:", ln=1)
        pdf.set_font("Arial", size=10)
        
        
        headers = ["Frame #", "Time (sec)", "Birds Count"]
        col_widths = [30, 40, 30]
        
        
        pdf.set_fill_color(200, 220, 255)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, txt=header, border=1, fill=True)
        pdf.ln()
        
        
        pdf.set_fill_color(255, 255, 255)
        for detection in history_entry['detections'][:100]:  
            pdf.cell(col_widths[0], 8, txt=str(detection['frame']), border=1)
            pdf.cell(col_widths[1], 8, txt=f"{detection['time']:.2f}", border=1)
            pdf.cell(col_widths[2], 8, txt=str(detection['birds']), border=1)
            pdf.ln()
        
        
        if len(history_entry['detections']) > 100:
            pdf.ln(5)
            pdf.cell(200, 8, txt=f"... and {len(history_entry['detections']) - 100} more frames", ln=1)
        
        
        report_filename = f"report_{history_entry['id']}.pdf"
        report_path = REPORTS_DIR / report_filename
        pdf.output(report_path)
        
        
        if not report_path.exists():
            raise IOError("PDF файл не может быть создан")
        
        logger.info(f"Успешно создан PDF: {report_path}")
        return report_path
        
    except Exception as e:
        logger.error(f"Файл PDF не был создан: {str(e)}")
        raise

def generate_excel_report(history_entry: dict) -> Path:
    
    try:
        
        required_fields = ['id', 'detections']
        for field in required_fields:
            if field not in history_entry:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        if not isinstance(history_entry['detections'], list):
            raise ValueError("Обнаружения должны быть представлены в виде списка")
        
        
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        
        data = {
            'Frame': [d['frame'] for d in history_entry['detections']],
            'Time (seconds)': [d['time'] for d in history_entry['detections']],
            'Birds Count': [d['birds'] for d in history_entry['detections']]
        }
        df = pd.DataFrame(data)
        
        
        report_filename = f"report_{history_entry['id']}.xlsx"
        report_path = REPORTS_DIR / report_filename
        df.to_excel(report_path, index=False)
        
        
        if not report_path.exists():
            raise IOError("Excel файл не может быть создан")
        
        logger.info(f"Успешно созданный Excel файл: {report_path}")
        return report_path
        
    except Exception as e:
        logger.error(f"Ошибка создания Excel файла: {str(e)}")
        raise