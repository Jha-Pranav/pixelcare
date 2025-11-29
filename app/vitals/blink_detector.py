import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance

class BlinkDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)
        self.EAR_THRESHOLD = 0.25
        self.CONSEC_FRAMES = 2
        self.blink_counter = 0
        self.frame_counter = 0
        self.counter = 0
        
    def eye_aspect_ratio(self, eye_landmarks):
        A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
        C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])
        return (A + B) / (2.0 * C)
    
    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]
        
        left_eye = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in [33, 160, 158, 133, 153, 144]])
        right_eye = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in [362, 385, 387, 263, 373, 380]])
        
        ear = (self.eye_aspect_ratio(left_eye) + self.eye_aspect_ratio(right_eye)) / 2.0
        self.frame_counter += 1
        
        if ear < self.EAR_THRESHOLD:
            self.counter += 1
        else:
            if self.counter >= self.CONSEC_FRAMES:
                self.blink_counter += 1
            self.counter = 0
        
        blink_rate = (self.blink_counter / (self.frame_counter / 30)) * 60 if self.frame_counter > 30 else 0
        
        return {'ear': round(ear, 3), 'blink_count': self.blink_counter, 'blink_rate': round(blink_rate, 1)}
