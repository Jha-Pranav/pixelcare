import cv2
import mediapipe as mp
import numpy as np

class MovementDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.prev_positions = []
        self.movement_history = []
    
    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        current_positions = np.array([(landmarks[i].x, landmarks[i].y) for i in [11, 12, 13, 14, 15, 16]])
        
        if len(self.prev_positions) > 0:
            movement = np.mean(np.linalg.norm(current_positions - self.prev_positions, axis=1))
            self.movement_history.append(movement)
            
            if len(self.movement_history) > 30:
                self.movement_history.pop(0)
            
            avg_movement = np.mean(self.movement_history)
            restlessness = min(100, int(avg_movement * 1000))
            
            if avg_movement < 0.01:
                fidget_level = "LOW"
            elif avg_movement < 0.03:
                fidget_level = "MODERATE"
            else:
                fidget_level = "HIGH"
        else:
            fidget_level = "LOW"
            restlessness = 0
        
        self.prev_positions = current_positions
        
        return {'fidget_level': fidget_level, 'restlessness_score': restlessness}
