import cv2
import numpy as np
from scipy import signal
from scipy.fft import fft
import mediapipe as mp

class CHROMHeartRate:
    def __init__(self, fps=30):
        self.fps = fps
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)
    
    def extract_face_roi(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        h, w, _ = frame.shape
        landmarks = results.multi_face_landmarks[0]
        roi_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288]
        
        points = [(int(landmarks.landmark[i].x * w), int(landmarks.landmark[i].y * h)) for i in roi_indices]
        x_coords, y_coords = [p[0] for p in points], [p[1] for p in points]
        x_min, x_max = max(0, min(x_coords)), min(w, max(x_coords))
        y_min, y_max = max(0, min(y_coords)), min(h, max(y_coords))
        
        return frame[y_min:y_max, x_min:x_max]
    
    def estimate(self, frames):
        rgb_means = []
        valid_frames = 0
        
        # Extract RGB from valid frames
        for frame in frames:
            roi = self.extract_face_roi(frame)
            if roi is not None and roi.size > 200:  # Larger minimum ROI
                r = np.mean(roi[:, :, 2])
                g = np.mean(roi[:, :, 1])
                b = np.mean(roi[:, :, 0])
                if r > 10 and g > 10 and b > 10:  # Valid RGB threshold
                    rgb_means.append([r, g, b])
                    valid_frames += 1
        
        if valid_frames < 120:  # Need at least 4 seconds
            return None
        
        rgb_means = np.array(rgb_means)
        
        # Temporal normalization
        rgb_norm = np.zeros_like(rgb_means, dtype=float)
        for i in range(3):
            mean_val = np.mean(rgb_means[:, i])
            std_val = np.std(rgb_means[:, i])
            if mean_val > 0 and std_val > 0:
                rgb_norm[:, i] = (rgb_means[:, i] - mean_val) / std_val
        
        # CHROM method
        X = 3 * rgb_norm[:, 0] - 2 * rgb_norm[:, 1]
        Y = 1.5 * rgb_norm[:, 0] + rgb_norm[:, 1] - 1.5 * rgb_norm[:, 2]
        
        # Detrend
        X = signal.detrend(X)
        Y = signal.detrend(Y)
        
        # Moving average filter to remove noise
        window = 5
        X = np.convolve(X, np.ones(window)/window, mode='same')
        Y = np.convolve(Y, np.ones(window)/window, mode='same')
        
        # Bandpass filter (0.7-3.5 Hz = 42-210 BPM)
        nyquist = self.fps / 2
        low = 0.7 / nyquist
        high = 3.5 / nyquist
        
        if low >= 1 or high >= 1 or low <= 0 or high <= 0:
            return None
            
        b, a = signal.butter(4, [low, high], btype='band')  # 4th order for better filtering
        X_f = signal.filtfilt(b, a, X)
        Y_f = signal.filtfilt(b, a, Y)
        
        # Calculate alpha with regularization
        std_x = np.std(X_f)
        std_y = np.std(Y_f)
        
        if std_y < 0.001:  # Avoid division by very small numbers
            return None
            
        alpha = std_x / std_y
        
        # Pulse signal
        pulse_signal = X_f - alpha * Y_f
        
        # Normalize pulse signal
        pulse_signal = (pulse_signal - np.mean(pulse_signal)) / (np.std(pulse_signal) + 1e-6)
        
        # FFT with zero-padding for better frequency resolution
        N = len(pulse_signal)
        N_padded = 2 ** int(np.ceil(np.log2(N * 4)))  # Zero-pad to next power of 2
        fft_data = np.abs(fft(pulse_signal, n=N_padded))[:N_padded//2]
        freqs = np.fft.fftfreq(N_padded, 1/self.fps)[:N_padded//2]
        
        # Find peak in valid range
        valid_idx = np.where((freqs >= 0.7) & (freqs <= 3.5))[0]
        
        if len(valid_idx) == 0:
            return None
        
        valid_fft = fft_data[valid_idx]
        valid_freqs = freqs[valid_idx]
        
        # Find top 3 peaks and use the strongest
        peaks_idx = signal.find_peaks(valid_fft, height=np.max(valid_fft) * 0.3)[0]
        
        if len(peaks_idx) == 0:
            peak_idx = np.argmax(valid_fft)
        else:
            # Use the peak with highest amplitude
            peak_idx = peaks_idx[np.argmax(valid_fft[peaks_idx])]
        
        hr_hz = valid_freqs[peak_idx]
        hr_bpm = hr_hz * 60
        
        # Validate range
        if 50 <= hr_bpm <= 150:  # More realistic range
            return round(hr_bpm, 1)
        
        return None
