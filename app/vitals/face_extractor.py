import cv2
import mediapipe as mp

class FaceExtractor:
    def __init__(self):
        self.mp_face = mp.solutions.face_detection
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.5)
        
    def extract(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb)
        
        if not results.detections:
            return None
            
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        h, w = frame.shape[:2]
        
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
        x = max(0, x)
        y = max(0, y)
        
        return frame[y:y+height, x:x+width]
    
    def __del__(self):
        self.face_detection.close()
