import cv2
import mediapipe as mp
import numpy as np

class FacialActionUnits:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)
    
    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Simplified AU detection using landmark distances
        mouth_open = abs(landmarks[13].y - landmarks[14].y)
        eyebrow_raise = abs(landmarks[70].y - landmarks[63].y)
        smile = abs(landmarks[61].x - landmarks[291].x)
        
        aus = {
            'AU12': 1 if smile > 0.3 else 0,  # Lip corner puller (smile)
            'AU01': 1 if eyebrow_raise > 0.02 else 0,  # Inner brow raiser
            'AU25': 1 if mouth_open > 0.02 else 0  # Lips part
        }
        
        return {'action_units': aus, 'count': sum(aus.values())}
