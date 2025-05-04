import torch
import cv2
from ultralytics import YOLO
from app.config import MODEL_NAME, BIRD_ID

class BirdDetector:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = YOLO(MODEL_NAME)
        self.model.to(self.device)
        
    def detect(self, frame, conf=0.25):
        small_frame = cv2.resize(frame, (640, 360))
        results = self.model(small_frame, conf=conf, classes=[BIRD_ID], device=self.device)
        return results

        