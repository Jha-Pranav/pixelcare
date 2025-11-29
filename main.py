#!/usr/bin/env python3
"""
PixelCare Phase 1 - Live Vitals Collection
State-of-the-art vital signs monitoring from webcam
"""
import sys
sys.path.append('app/vitals')

from app.vitals.live_collector import LiveVitalsCollector

def main():
    print("="*60)
    print("🏥 PixelCare - AI Health Companion")
    print("Phase 1: Live Vitals Collection (SOTA)")
    print("="*60)
    print("\n📋 Features:")
    print("  ❤️  Heart Rate (CHROM rPPG)")
    print("  🫁 Breathing Rate (Pose tracking)")
    print("  👁️  Blink Rate (EAR method)")
    print("  😊 Emotion Detection")
    print("\n💡 Tips:")
    print("  - Sit 30-100cm from camera")
    print("  - Ensure good lighting")
    print("  - Stay still during capture")
    print("  - Press 'q' to stop early")
    print("\n" + "="*60 + "\n")
    
    collector = LiveVitalsCollector(duration=10)
    results = collector.collect()
    
    if results:
        print("\n✅ Collection complete!")
        print("📁 Results saved in memory")
    else:
        print("\n❌ Collection failed")

if __name__ == "__main__":
    main()
