import cv2
import mediapipe as mp
import numpy as np

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    def analyze(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[23]
        nose = landmarks[0]
        
        shoulder_slope = abs(left_shoulder.y - right_shoulder.y)
        forward_lean = abs(nose.y - (left_shoulder.y + right_shoulder.y) / 2)
        
        score = 100
        if shoulder_slope > 0.08:  # More lenient (was 0.05)
            score -= 30
        if forward_lean > 0.20:  # More lenient (was 0.15)
            score -= 40
        
        status = "GOOD" if score >= 60 else "POOR"  # Lower threshold (was 70)
        
        return {'status': status, 'score': max(0, score), 'shoulder_slope': round(shoulder_slope, 3), 'forward_lean': round(forward_lean, 3)}
