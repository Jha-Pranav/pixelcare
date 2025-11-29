import cv2
import time
import json
import numpy as np
from .heart_rate_chrom import CHROMHeartRate
from .breathing_rate import BreathingDetector
from .blink_detector import BlinkDetector
from .hrv_analyzer import HRVAnalyzer
from .emotion import EmotionDetector
from .pose_extractor import PoseExtractor
from .gaze_tracker import GazeTracker
from .head_pose_estimator import HeadPoseEstimator
from .posture_analyzer import PostureAnalyzer
from .movement_detector import MovementDetector
from .facial_action_units import FacialActionUnits

class LiveVitalsCollector:
    def __init__(self, duration=10, fps=30, sample_interval=30, vital_sample_interval=60, headless=False):
        self.duration = duration
        self.fps = fps
        self.sample_interval = sample_interval  # Sample behavioral metrics every 1s
        self.vital_sample_interval = vital_sample_interval  # Sample vitals every 2s
        self.headless = headless  # No GUI display
        
        self.hr_detector = CHROMHeartRate(fps)
        self.br_detector = BreathingDetector(fps)
        self.blink_detector = BlinkDetector()
        self.hrv_analyzer = HRVAnalyzer(fps)
        self.emotion_detector = EmotionDetector()
        self.pose_extractor = PoseExtractor()
        self.gaze_tracker = GazeTracker()
        self.head_pose = HeadPoseEstimator()
        self.posture = PostureAnalyzer()
        self.movement = MovementDetector()
        self.facial_au = FacialActionUnits()
        
        # Sample storage for rich data
        self.emotion_samples = []
        self.posture_samples = []
        self.head_pose_samples = []
        self.gaze_samples = []
        self.movement_samples = []
        self.au_samples = []
        
        # Vital signs samples
        self.hr_samples = []
        self.br_samples = []
        self.blink_samples = []
        
        # Continuous data for HRV
        self.all_frames = []
        self.all_pose_landmarks = []
        
    def collect(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access webcam")
            return None
        
        print(f"📹 Collecting vitals for {self.duration} seconds...")
        
        frames = []
        pose_landmarks = []
        
        target_frames = self.duration * self.fps
        start_time = time.time()
        frame_count = 0
        
        while frame_count < target_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frames.append(frame)
            frame_count += 1
            
            # Store all data for final analysis
            self.all_frames.append(frame)
            
            # Extract pose
            pose = self.pose_extractor.extract(frame)
            if pose is not None:
                pose_landmarks.append(pose)
                self.all_pose_landmarks.append(pose)
            
            # Real-time metrics for display
            blink_result = self.blink_detector.detect(frame)
            gaze_result = self.gaze_tracker.detect(frame)
            head_pose_result = self.head_pose.estimate(frame)
            posture_result = self.posture.analyze(frame)
            movement_result = self.movement.detect(frame)
            emotion_result = self.emotion_detector.detect(frame)
            au_result = self.facial_au.detect(frame)
            
            # Sample vital signs every 2 seconds
            if frame_count % self.vital_sample_interval == 0 and frame_count >= self.vital_sample_interval:
                # Calculate HR from frames so far
                hr_temp = self.hr_detector.estimate(self.all_frames[-self.vital_sample_interval*2:])
                if hr_temp:
                    self.hr_samples.append({
                        'timestamp': frame_count / self.fps,
                        'value': hr_temp
                    })
                
                # Calculate BR from pose so far
                br_temp = self.br_detector.estimate(self.all_pose_landmarks[-self.vital_sample_interval*2:])
                if br_temp:
                    self.br_samples.append({
                        'timestamp': frame_count / self.fps,
                        'value': br_temp
                    })
                
                # Blink rate at this point
                if blink_result:
                    self.blink_samples.append({
                        'timestamp': frame_count / self.fps,
                        'rate': blink_result['blink_rate'],
                        'count': blink_result['blink_count']
                    })
            
            # Sample at intervals for rich data
            if frame_count % self.sample_interval == 0:
                if emotion_result:
                    self.emotion_samples.append({
                        'timestamp': frame_count / self.fps,
                        'emotion': emotion_result['emotion'],
                        'confidence': emotion_result['confidence']
                    })
                if posture_result:
                    self.posture_samples.append({
                        'timestamp': frame_count / self.fps,
                        'status': posture_result['status'],
                        'score': posture_result['score'],
                        'shoulder_slope': posture_result['shoulder_slope'],
                        'forward_lean': posture_result['forward_lean']
                    })
                if head_pose_result:
                    self.head_pose_samples.append({
                        'timestamp': frame_count / self.fps,
                        'pitch': head_pose_result['pitch'],
                        'yaw': head_pose_result['yaw'],
                        'roll': head_pose_result['roll']
                    })
                if gaze_result:
                    self.gaze_samples.append({
                        'timestamp': frame_count / self.fps,
                        'direction': gaze_result['direction'],
                        'ratio': gaze_result['ratio']
                    })
                if movement_result:
                    self.movement_samples.append({
                        'timestamp': frame_count / self.fps,
                        'fidget_level': movement_result['fidget_level'],
                        'restlessness_score': movement_result['restlessness_score']
                    })
                if au_result:
                    self.au_samples.append({
                        'timestamp': frame_count / self.fps,
                        'count': au_result['count'],
                        'units': au_result['action_units']
                    })
            
            # Display on frame
            elapsed = frame_count / self.fps
            y = 30
            cv2.putText(frame, f"Recording: {elapsed:.1f}s / {self.duration}s", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y += 30
            
            # Show latest vital samples
            if self.hr_samples:
                cv2.putText(frame, f"HR: {self.hr_samples[-1]['value']:.1f} BPM", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if self.br_samples:
                cv2.putText(frame, f"BR: {self.br_samples[-1]['value']:.1f} BPM", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if blink_result:
                cv2.putText(frame, f"Blinks: {blink_result['blink_count']} | Rate: {blink_result['blink_rate']:.1f}/min", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if gaze_result:
                cv2.putText(frame, f"Gaze: {gaze_result['direction']}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if head_pose_result:
                cv2.putText(frame, f"Head: P{head_pose_result['pitch']:.0f} Y{head_pose_result['yaw']:.0f} R{head_pose_result['roll']:.0f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if posture_result:
                color = (0, 255, 0) if posture_result['status'] == 'GOOD' else (0, 0, 255)
                cv2.putText(frame, f"Posture: {posture_result['status']} ({posture_result['score']}%)", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y += 25
            
            if movement_result:
                cv2.putText(frame, f"Movement: {movement_result['fidget_level']}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if emotion_result:
                cv2.putText(frame, f"Emotion: {emotion_result['emotion']}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25
            
            if au_result:
                cv2.putText(frame, f"Facial AUs: {au_result['count']} active", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Only show window if not headless
            if not self.headless:
                cv2.imshow('Vitals Collection', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            else:
                # In headless mode, just wait 1ms
                cv2.waitKey(1)
        
        # Force close all windows
        cap.release()
        for _ in range(5):
            cv2.destroyAllWindows()
            cv2.waitKey(1)
        
        cap.release()
        cv2.destroyAllWindows()
        
        capture_time = time.time() - start_time
        print(f"✅ Captured {len(frames)} frames in {capture_time:.1f}s")
        print("\n🔍 Analyzing vitals...")
        
        # Analyze vitals
        hr = self.hr_detector.estimate(frames)
        br = self.br_detector.estimate(pose_landmarks)
        blink_final = self.blink_detector.detect(frames[-1]) if frames else None
        emotion = self.emotion_detector.detect(frames[-1]) if frames else None
        au_result = self.facial_au.detect(frames[-1]) if frames else None
        
        # Calculate HRV
        hrv_result = self._calculate_hrv(frames)
        
        # Aggregate time-series data from samples
        hr_summary = self._analyze_hr_samples(hr)
        br_summary = self._analyze_br_samples(br)
        blink_summary = self._analyze_blink_samples(blink_final)
        posture_summary = self._analyze_posture_samples()
        head_pose_summary = self._analyze_head_pose_samples()
        gaze_summary = self._analyze_gaze_samples()
        movement_summary = self._analyze_movement_samples()
        emotion_summary = self._analyze_emotion_samples()
        
        results = {
            "session_summary": {
                "overall_health_status": self._calculate_overall_health(hr_summary, br_summary, hrv_result, posture_summary),
                "key_findings": self._generate_key_findings(hr_summary, br_summary, hrv_result, blink_summary, posture_summary, movement_summary),
                "recommendations": self._generate_recommendations(hr_summary, br_summary, hrv_result, posture_summary, movement_summary),
                "risk_factors": self._identify_risk_factors(hr_summary, br_summary, hrv_result, posture_summary)
            },
            "physiological_vitals": {
                "heart_rate": hr_summary,
                "breathing_rate": br_summary,
                "hrv": hrv_result
            },
            "eye_attention": {
                "blink_rate": blink_summary,
                "gaze": gaze_summary
            },
            "posture_behavior": {
                "posture": posture_summary,
                "head_pose": head_pose_summary,
                "movement": movement_summary
            },
            "emotion": emotion_summary,
            "facial_action_units": {
                "samples": self.au_samples,
                "average_active": sum(s['count'] for s in self.au_samples) / len(self.au_samples) if self.au_samples else 0
            },
            "capture_info": {
                "frames_captured": len(frames),
                "duration_seconds": round(capture_time, 2),
                "fps": self.fps,
                "behavioral_samples": len(self.emotion_samples),
                "vital_samples": len(self.hr_samples),
                "sample_intervals": {
                    "behavioral": f"every {self.sample_interval} frames (1s)",
                    "vitals": f"every {self.vital_sample_interval} frames (2s)"
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "data_quality": {
                    "hr_samples_collected": len(self.hr_samples),
                    "br_samples_collected": len(self.br_samples),
                    "blink_samples_collected": len(self.blink_samples),
                    "behavioral_samples_collected": len(self.emotion_samples),
                    "hrv_calculated": hrv_result.get('status') == 'calculated'
                }
            }
        }
        
        self._display_results(results)
        
        # Final cleanup
        cv2.destroyAllWindows()
        for _ in range(10):
            cv2.waitKey(1)
        
        return results
    
    def _calculate_hrv(self, frames):
        """Calculate HRV from all frames"""
        if len(frames) < 150:
            return {"status": "insufficient_data"}
        
        # Extract green channel values for HRV
        green_values = []
        for frame in frames:
            roi = self.hr_detector.extract_face_roi(frame)
            if roi is not None and roi.size > 200:
                green_values.append(np.mean(roi[:, :, 1]))
        
        if len(green_values) < 150:
            return {"status": "insufficient_data"}
        
        hrv_result = self.hrv_analyzer.calculate_hrv(green_values)
        
        if hrv_result:
            # Add interpretation
            sdnn = hrv_result['sdnn']
            if sdnn > 50:
                stress_level = "low"
                interpretation = "Good HRV indicates low stress and good recovery"
            elif sdnn > 30:
                stress_level = "moderate"
                interpretation = "Moderate HRV suggests some stress present"
            else:
                stress_level = "high"
                interpretation = "Low HRV indicates high stress or fatigue"
            
            hrv_result['stress_level'] = stress_level
            hrv_result['interpretation'] = interpretation
            hrv_result['status'] = "calculated"
        
        return hrv_result or {"status": "calculation_failed"}
    
    def _analyze_hr_samples(self, final_hr):
        """Analyze heart rate samples"""
        if not self.hr_samples:
            return {
                "value": final_hr,
                "unit": "BPM",
                "method": "CHROM rPPG",
                "status": "normal" if final_hr and 60 <= final_hr <= 100 else "abnormal" if final_hr else "not_detected",
                "samples": [],
                "trend": "no_data"
            }
        
        values = [s['value'] for s in self.hr_samples]
        avg_hr = sum(values) / len(values)
        min_hr = min(values)
        max_hr = max(values)
        
        # Determine trend
        if len(values) >= 3:
            first_half = sum(values[:len(values)//2]) / (len(values)//2)
            second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
            
            if second_half > first_half + 3:
                trend = "increasing"
                interpretation = f"HR increased from {first_half:.1f} to {second_half:.1f} BPM - possible stress response"
            elif second_half < first_half - 3:
                trend = "decreasing"
                interpretation = f"HR decreased from {first_half:.1f} to {second_half:.1f} BPM - relaxation"
            else:
                trend = "stable"
                interpretation = f"HR remained stable around {avg_hr:.1f} BPM"
        else:
            trend = "insufficient_samples"
            interpretation = "Need more samples for trend analysis"
        
        return {
            "samples": self.hr_samples,
            "final_value": final_hr,
            "average": round(avg_hr, 1),
            "min": round(min_hr, 1),
            "max": round(max_hr, 1),
            "range": round(max_hr - min_hr, 1),
            "unit": "BPM",
            "method": "CHROM rPPG",
            "trend": trend,
            "interpretation": interpretation,
            "status": "normal" if 60 <= avg_hr <= 100 else "abnormal"
        }
    
    def _analyze_br_samples(self, final_br):
        """Analyze breathing rate samples"""
        if not self.br_samples:
            return {
                "value": final_br,
                "unit": "BPM",
                "status": "normal" if final_br and 12 <= final_br <= 20 else "abnormal" if final_br else "not_detected",
                "samples": [],
                "trend": "no_data"
            }
        
        values = [s['value'] for s in self.br_samples]
        avg_br = sum(values) / len(values)
        
        # Check for rapid breathing
        rapid_count = sum(1 for v in values if v > 20)
        rapid_pct = (rapid_count / len(values)) * 100
        
        if rapid_pct > 50:
            interpretation = f"Rapid breathing detected in {rapid_pct:.0f}% of samples - possible anxiety or stress"
        elif avg_br > 18:
            interpretation = f"Slightly elevated breathing rate ({avg_br:.1f} BPM) - mild stress"
        else:
            interpretation = f"Normal breathing pattern ({avg_br:.1f} BPM)"
        
        return {
            "samples": self.br_samples,
            "final_value": final_br,
            "average": round(avg_br, 1),
            "min": round(min(values), 1),
            "max": round(max(values), 1),
            "unit": "BPM",
            "rapid_breathing_percentage": round(rapid_pct, 1),
            "interpretation": interpretation,
            "status": "normal" if 12 <= avg_br <= 20 else "abnormal"
        }
    
    def _analyze_blink_samples(self, final_blink):
        """Analyze blink rate samples"""
        if not self.blink_samples:
            return {
                "value": final_blink['blink_rate'] if final_blink else None,
                "unit": "blinks/min",
                "status": "normal" if final_blink and 15 <= final_blink['blink_rate'] <= 20 else "abnormal" if final_blink else "not_detected",
                "samples": [],
                "trend": "no_data"
            }
        
        rates = [s['rate'] for s in self.blink_samples]
        avg_rate = sum(rates) / len(rates)
        
        # Check for reduced blinking (concentration/fatigue)
        low_count = sum(1 for r in rates if r < 12)
        low_pct = (low_count / len(rates)) * 100
        
        if low_pct > 50:
            interpretation = f"Reduced blinking in {low_pct:.0f}% of samples - high concentration or screen fatigue"
        elif avg_rate > 25:
            interpretation = f"Elevated blink rate ({avg_rate:.1f}/min) - possible eye strain or stress"
        else:
            interpretation = f"Normal blink pattern ({avg_rate:.1f}/min)"
        
        return {
            "samples": self.blink_samples,
            "final_value": final_blink['blink_rate'] if final_blink else None,
            "average": round(avg_rate, 1),
            "min": round(min(rates), 1),
            "max": round(max(rates), 1),
            "unit": "blinks/min",
            "low_blink_percentage": round(low_pct, 1),
            "interpretation": interpretation,
            "status": "normal" if 15 <= avg_rate <= 20 else "abnormal"
        }
    
    def _calculate_overall_health(self, hr, br, hrv, posture):
        """Calculate overall health status"""
        score = 100
        issues = []
        
        # Heart rate check
        if hr['status'] == 'abnormal':
            score -= 20
            issues.append(f"Heart rate {hr['average']} BPM is outside normal range")
        
        # Breathing check
        if br['status'] == 'abnormal':
            score -= 15
            issues.append(f"Breathing rate {br['average']} BPM is abnormal")
        
        # HRV check
        if hrv.get('status') == 'calculated':
            if hrv['stress_level'] == 'high':
                score -= 25
                issues.append("High stress detected via HRV")
            elif hrv['stress_level'] == 'moderate':
                score -= 10
        
        # Posture check
        if posture['status'] == 'poor':
            score -= 15
            issues.append("Poor posture detected")
        
        if score >= 80:
            status = "excellent"
        elif score >= 60:
            status = "good"
        elif score >= 40:
            status = "fair"
        else:
            status = "needs_attention"
        
        return {
            "score": max(0, score),
            "status": status,
            "issues": issues if issues else ["No significant issues detected"]
        }
    
    def _generate_key_findings(self, hr, br, hrv, blink, posture, movement):
        """Generate key findings for LLM"""
        findings = []
        
        # Vital signs
        if hr.get('trend') == 'increasing':
            findings.append(f"Heart rate showed increasing trend ({hr['interpretation']})")
        elif hr.get('trend') == 'decreasing':
            findings.append(f"Heart rate showed decreasing trend ({hr['interpretation']})")
        
        if br.get('rapid_breathing_percentage', 0) > 30:
            findings.append(f"Rapid breathing detected in {br['rapid_breathing_percentage']:.0f}% of samples")
        
        # HRV
        if hrv.get('status') == 'calculated':
            findings.append(f"HRV analysis: {hrv['stress_level']} stress (SDNN: {hrv['sdnn']}ms)")
        
        # Attention
        if blink.get('low_blink_percentage', 0) > 50:
            findings.append(f"Reduced blinking in {blink['low_blink_percentage']:.0f}% of samples - high concentration")
        
        # Posture
        if posture.get('consistency_percentage', 0) < 50:
            findings.append(f"Inconsistent posture - only {posture['consistency_percentage']:.0f}% good posture")
        
        # Movement
        if movement.get('status') == 'restless':
            findings.append(f"High restlessness detected ({movement['restlessness_percentage']:.0f}%)")
        
        return findings if findings else ["Session completed normally with no significant findings"]
    
    def _generate_recommendations(self, hr, br, hrv, posture, movement):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Heart rate
        if hr.get('average', 0) > 100:
            recommendations.append("Consider relaxation techniques - elevated heart rate detected")
        elif hr.get('trend') == 'increasing':
            recommendations.append("Monitor stress levels - heart rate is trending upward")
        
        # Breathing
        if br.get('average', 0) > 20:
            recommendations.append("Practice deep breathing exercises - breathing rate is elevated")
        
        # HRV
        if hrv.get('stress_level') in ['moderate', 'high']:
            recommendations.append("Take breaks and practice stress management - HRV indicates stress")
        
        # Posture
        if posture.get('status') in ['poor', 'moderate']:
            recommendations.append(posture.get('recommendation', 'Improve posture'))
        
        # Movement
        if movement.get('status') == 'restless':
            recommendations.append("Consider taking a break - high movement detected")
        
        return recommendations if recommendations else ["Continue current wellness practices"]
    
    def _identify_risk_factors(self, hr, br, hrv, posture):
        """Identify potential health risk factors"""
        risks = []
        
        if hr.get('average', 0) > 100 or hr.get('average', 0) < 50:
            risks.append({
                "factor": "abnormal_heart_rate",
                "severity": "moderate",
                "description": f"Heart rate {hr['average']} BPM is outside typical range"
            })
        
        if br.get('rapid_breathing_percentage', 0) > 50:
            risks.append({
                "factor": "rapid_breathing",
                "severity": "moderate",
                "description": "Frequent rapid breathing may indicate stress or anxiety"
            })
        
        if hrv.get('stress_level') == 'high':
            risks.append({
                "factor": "high_stress",
                "severity": "high",
                "description": "Low HRV indicates high stress or poor recovery"
            })
        
        if posture.get('consistency_percentage', 0) < 30:
            risks.append({
                "factor": "poor_posture",
                "severity": "low",
                "description": "Consistently poor posture may lead to musculoskeletal issues"
            })
        
        return risks if risks else [{"factor": "none", "severity": "none", "description": "No significant risk factors identified"}]
    
    def _analyze_posture_samples(self):
        if not self.posture_samples:
            return {"status": "not_detected", "recommendation": "Unable to analyze posture"}
        
        scores = [s['score'] for s in self.posture_samples]
        good_count = sum(1 for s in self.posture_samples if s['status'] == 'GOOD')
        consistency = (good_count / len(self.posture_samples)) * 100
        
        avg_score = sum(scores) / len(scores)
        
        if consistency >= 70:
            status = "excellent"
            recommendation = "Posture is consistently good throughout the session."
        elif consistency >= 50:
            status = "moderate"
            recommendation = "Posture varies. Detected slouching in some samples."
        else:
            status = "poor"
            recommendation = "Frequent poor posture detected. Consider ergonomic adjustments."
        
        return {
            "samples": self.posture_samples,
            "average_score": round(avg_score, 1),
            "consistency_percentage": round(consistency, 1),
            "good_samples": good_count,
            "poor_samples": len(self.posture_samples) - good_count,
            "status": status,
            "recommendation": recommendation
        }
    
    def _analyze_head_pose_samples(self):
        if not self.head_pose_samples:
            return {"status": "not_detected"}
        
        pitches = [s['pitch'] for s in self.head_pose_samples]
        yaws = [s['yaw'] for s in self.head_pose_samples]
        rolls = [s['roll'] for s in self.head_pose_samples]
        
        avg_pitch = sum(pitches) / len(pitches)
        forward_head_count = sum(1 for p in pitches if p < -15)
        forward_head_pct = (forward_head_count / len(pitches)) * 100
        
        return {
            "samples": self.head_pose_samples,
            "average_pitch": round(avg_pitch, 1),
            "average_yaw": round(sum(yaws) / len(yaws), 1),
            "average_roll": round(sum(rolls) / len(rolls), 1),
            "forward_head_percentage": round(forward_head_pct, 1),
            "recommendation": f"Forward head detected in {forward_head_pct:.0f}% of samples" if forward_head_pct > 30 else "Head position is generally neutral"
        }
    
    def _analyze_gaze_samples(self):
        if not self.gaze_samples:
            return {"status": "not_detected"}
        
        directions = [s['direction'] for s in self.gaze_samples]
        center_count = sum(1 for d in directions if d == 'CENTER')
        focus_pct = (center_count / len(directions)) * 100
        
        return {
            "samples": self.gaze_samples,
            "center_gaze_percentage": round(focus_pct, 1),
            "status": "focused" if focus_pct >= 70 else "distracted",
            "recommendation": f"Maintained center focus in {focus_pct:.0f}% of samples" if focus_pct >= 70 else f"Gaze wandered in {100-focus_pct:.0f}% of samples"
        }
    
    def _analyze_movement_samples(self):
        if not self.movement_samples:
            return {"status": "not_detected"}
        
        fidget_levels = [s['fidget_level'] for s in self.movement_samples]
        high_count = sum(1 for f in fidget_levels if f == 'HIGH')
        restlessness_pct = (high_count / len(fidget_levels)) * 100
        
        if restlessness_pct < 20:
            status = "calm"
            recommendation = "Movement levels are normal throughout session"
        elif restlessness_pct < 50:
            status = "moderate"
            recommendation = f"Restlessness detected in {restlessness_pct:.0f}% of samples"
        else:
            status = "restless"
            recommendation = f"High movement in {restlessness_pct:.0f}% of samples - may indicate discomfort"
        
        return {
            "samples": self.movement_samples,
            "restlessness_percentage": round(restlessness_pct, 1),
            "status": status,
            "recommendation": recommendation
        }
    
    def _analyze_emotion_samples(self):
        if not self.emotion_samples:
            return {"status": "not_detected"}
        
        emotions = [s['emotion'] for s in self.emotion_samples]
        emotion_counts = {}
        for e in emotions:
            emotion_counts[e] = emotion_counts.get(e, 0) + 1
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        dominant_pct = (emotion_counts[dominant_emotion] / len(emotions)) * 100
        
        return {
            "samples": self.emotion_samples,
            "dominant_emotion": dominant_emotion,
            "dominant_percentage": round(dominant_pct, 1),
            "emotion_distribution": emotion_counts,
            "recommendation": f"Predominantly {dominant_emotion} throughout session ({dominant_pct:.0f}% of samples)"
        }
    
    def _display_results(self, results):
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE VITAL SIGNS & BEHAVIORAL METRICS (SOTA)")
        print("="*70)
        
        pv = results['physiological_vitals']
        print("\n🫀 PHYSIOLOGICAL VITALS:")
        print(f"  ❤️  Heart Rate: {pv['heart_rate']['average']} BPM (range: {pv['heart_rate']['min']}-{pv['heart_rate']['max']})")
        print(f"     Trend: {pv['heart_rate']['trend']} | {pv['heart_rate']['interpretation']}")
        print(f"     Samples: {len(self.hr_samples)} collected")
        
        print(f"  🫁 Breathing Rate: {pv['breathing_rate']['average']} BPM (range: {pv['breathing_rate']['min']}-{pv['breathing_rate']['max']})")
        print(f"     {pv['breathing_rate']['interpretation']}")
        print(f"     Samples: {len(self.br_samples)} collected")
        
        if pv['hrv']['status'] == 'calculated':
            print(f"  💓 HRV: SDNN={pv['hrv']['sdnn']}ms, RMSSD={pv['hrv']['rmssd']}ms")
            print(f"     Stress Level: {pv['hrv']['stress_level'].upper()} | {pv['hrv']['interpretation']}")
        
        ea = results['eye_attention']
        print("\n👁️  EYE & ATTENTION:")
        print(f"  👁️  Blink Rate: {ea['blink_rate']['average']}/min (range: {ea['blink_rate']['min']}-{ea['blink_rate']['max']})")
        print(f"     {ea['blink_rate']['interpretation']}")
        print(f"     Samples: {len(self.blink_samples)} collected")
        print(f"  👀 Gaze Focus: {ea['gaze']['center_gaze_percentage']}% - {ea['gaze']['status']}")
        
        pb = results['posture_behavior']
        print("\n🧭 POSTURE & BEHAVIOR (Time-Series Analysis):")
        print(f"  🧍 Posture: {pb['posture']['status'].upper()} (avg: {pb['posture']['average_score']}%, consistency: {pb['posture']['consistency_percentage']}%)")
        print(f"     → {pb['posture']['recommendation']}")
        print(f"  🧭 Head Pose: Pitch {pb['head_pose']['average_pitch']}° | Yaw {pb['head_pose']['average_yaw']}° | Roll {pb['head_pose']['average_roll']}°")
        print(f"     → {pb['head_pose']['recommendation']}")
        print(f"  🤸 Movement: {pb['movement']['status'].upper()} (restlessness: {pb['movement']['restlessness_percentage']}%)")
        print(f"     → {pb['movement']['recommendation']}")
        
        print(f"\n😊 EMOTION: {results['emotion']['dominant_emotion']} ({results['emotion']['dominant_percentage']}% of {len(self.emotion_samples)} samples)")
        print(f"   Distribution: {results['emotion']['emotion_distribution']}")
        print(f"😀 FACIAL AUs: {results['facial_action_units']['average_active']:.1f} avg active")
        
        print(f"\n📊 CAPTURE: {results['capture_info']['frames_captured']} frames")
        print(f"   Behavioral samples: {results['capture_info']['behavioral_samples']} (every 1s)")
        print(f"   Vital samples: {results['capture_info']['vital_samples']} (every 2s)")
        print("="*70)

if __name__ == "__main__":
    collector = LiveVitalsCollector(duration=10)
    results = collector.collect()
