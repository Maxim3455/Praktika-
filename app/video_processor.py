import cv2
import logging
from datetime import datetime
from app.detector import BirdDetector
from app.config import PROCESSED_DIR, UPLOAD_DIR

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.detector = BirdDetector()
    
    def process_video(self, input_path, output_path):
        try:
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Не удалось открыть видео: {input_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            frame_count = 0
            max_birds = 0
            detection_log = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                results = self.detector.detect(frame)
                bird_count = self._draw_boxes(frame, results)
                
                detection_log.append({
                    "frame": frame_count,
                    "birds": bird_count,
                    "time": frame_count / fps
                })
                
                out.write(frame)
                max_birds = max(max_birds, bird_count)
                frame_count += 1
                
                if frame_count % 100 == 0:
                    logger.info(f"Обработано {frame_count}/{total_frames} кадров")
            
            cap.release()
            out.release()
            
            return {
                "max_birds": max_birds,
                "total_frames": frame_count,
                "detections": detection_log,
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки видео: {str(e)}")
            raise

    def _draw_boxes(self, frame, results):
        bird_count = 0
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, [coord * frame.shape[1] / 640 for coord in box.xyxy[0][:4]])
                conf = float(box.conf)
                
                if (x2 - x1) < 15 or (y2 - y1) < 15:
                    continue
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
                label = f"Bird {conf:.2f}"
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
                bird_count += 1
        
        cv2.putText(frame, f"Birds: {bird_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return bird_count