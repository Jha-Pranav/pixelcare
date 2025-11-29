import numpy as np
from scipy import signal
from scipy.fft import fft

class HeartRateDetector:
    def __init__(self, fps=30):
        self.fps = fps
        
    def estimate(self, face_regions):
        if len(face_regions) < 30:
            return None
            
        green_values = [np.mean(r[:, :, 1]) for r in face_regions if r is not None and r.size > 0]
        
        if len(green_values) < 30:
            return None
            
        green_values = np.array(green_values)
        detrended = signal.detrend(green_values)
        
        nyquist = self.fps / 2
        b, a = signal.butter(3, [0.7/nyquist, 4.0/nyquist], btype='band')
        filtered = signal.filtfilt(b, a, detrended)
        
        fft_data = np.abs(fft(filtered))
        freqs = np.fft.fftfreq(len(filtered), 1/self.fps)
        
        valid_idx = np.where((freqs >= 0.7) & (freqs <= 4.0))
        valid_fft = fft_data[valid_idx]
        valid_freqs = freqs[valid_idx]
        
        if len(valid_fft) == 0:
            return None
            
        peak_idx = np.argmax(valid_fft)
        hr_bpm = valid_freqs[peak_idx] * 60
        
        return round(hr_bpm, 1) if 45 <= hr_bpm <= 180 else None
