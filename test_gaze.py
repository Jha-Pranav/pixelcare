import cv2
import sys
sys.path.append('app/vitals')
from gaze_tracker import GazeTracker

tracker = GazeTracker()
cap = cv2.VideoCapture(0)

print("Testing gaze - Look LEFT, CENTER, RIGHT")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    result = tracker.detect(frame)
    if result:
        cv2.putText(frame, f"Gaze: {result['direction']} (offset: {result['ratio']:.3f})", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Gaze Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
