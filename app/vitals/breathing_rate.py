import numpy as np
from scipy import signal

class BreathingDetector:
    def __init__(self, fps=30):
        self.fps = fps
        
    def estimate(self, pose_landmarks_list):
        if len(pose_landmarks_list) < 30:
            return None
            
        shoulder_positions = []
        for pose in pose_landmarks_list:
            left = pose.landmark[11]
            right = pose.landmark[12]
            shoulder_positions.append((left.y + right.y) / 2)
        
        if len(shoulder_positions) < 30:
            return None
            
        positions = np.array(shoulder_positions)
        detrended = signal.detrend(positions)
        
        nyquist = self.fps / 2
        b, a = signal.butter(2, [0.1/nyquist, 0.5/nyquist], btype='band')
        filtered = signal.filtfilt(b, a, detrended)
        
        peaks, _ = signal.find_peaks(filtered, distance=self.fps)
        
        if len(peaks) > 1:
            duration = len(positions) / self.fps
            br_bpm = (len(peaks) / duration) * 60
            return round(br_bpm, 1) if 6 <= br_bpm <= 30 else None
        
        return None
