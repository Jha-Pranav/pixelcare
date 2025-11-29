import numpy as np
from scipy import signal

class HRVAnalyzer:
    def __init__(self, fps=30):
        self.fps = fps
        
    def calculate_hrv(self, green_values):
        if len(green_values) < 150:
            return None
        
        signal_data = np.array(green_values)
        detrended = signal.detrend(signal_data)
        
        nyquist = self.fps / 2
        b, a = signal.butter(3, [0.7/nyquist, 4.0/nyquist], btype='band')
        filtered = signal.filtfilt(b, a, detrended)
        
        peaks, _ = signal.find_peaks(filtered, distance=self.fps * 0.5)
        
        if len(peaks) < 3:
            return None
        
        rr_intervals = np.diff(peaks) / self.fps * 1000
        
        if len(rr_intervals) < 2:
            return None
        
        sdnn = np.std(rr_intervals)
        rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))
        mean_hr = 60000 / np.mean(rr_intervals)
        hrv_score = min(100, int(sdnn / 2))
        
        return {'sdnn': round(sdnn, 1), 'rmssd': round(rmssd, 1), 'mean_hr': round(mean_hr, 1), 'hrv_score': hrv_score}
