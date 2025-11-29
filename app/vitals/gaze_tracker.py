import cv2
import mediapipe as mp
import numpy as np

class GazeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)
    
    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        h, w = frame.shape[:2]
        
        # Use left eye for gaze
        # Eye corners: 33 (left), 133 (right)
        # Iris center: 468
        eye_left = landmarks[33]
        eye_right = landmarks[133]
        iris = landmarks[468]
        
        # Calculate horizontal positions
        eye_left_x = eye_left.x
        eye_right_x = eye_right.x
        iris_x = iris.x
        
        # Eye center
        eye_center_x = (eye_left_x + eye_right_x) / 2
        
        # Iris offset from center
        offset = iris_x - eye_center_x
        
        # Normalize by eye width
        eye_width = abs(eye_right_x - eye_left_x)
        if eye_width > 0:
            normalized_offset = offset / eye_width
        else:
            normalized_offset = 0
        
        # Determine direction with adjusted thresholds
        if normalized_offset < -0.08:
            direction = "LEFT"
        elif normalized_offset > 0.08:
            direction = "RIGHT"
        else:
            direction = "CENTER"
        
        return {'direction': direction, 'ratio': round(normalized_offset, 3)}
