# PixelCare 🏥

AI health companion via webcam: monitors vitals, understands emotions, and provides health insights—all processed locally.

## 🚀 Quick Start

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run the app
./run_ui.sh
```

Open: **http://localhost:7860**

## ✨ Features

### Phase 1: Live Vitals Collection ✅

**10 Vitals Collected in 10 Seconds:**

1. ❤️ **Heart Rate** - CHROM rPPG (±2-4 BPM)
2. 🫁 **Breathing Rate** - Shoulder movement tracking
3. 👁️ **Blink Detection** - Eye Aspect Ratio method
4. 👀 **Gaze Tracking** - Iris landmark tracking
5. 🧭 **Head Pose** - 3D estimation (pitch/yaw/roll)
6. 🧍 **Posture Analysis** - Quality scoring
7. 🤸 **Movement/Fidgeting** - Restlessness detection
8. 😀 **Facial Action Units** - Muscle movements
9. 💓 **HRV Analysis** - SDNN, RMSSD metrics
10. 😊 **Emotion Detection** - Basic emotions

### Rich Data Collection

- **~70+ timestamped samples** per session
- **Behavioral metrics**: Sampled every 1 second
- **Vital signs**: Sampled every 2 seconds
- **Trend analysis**: Increasing/decreasing/stable
- **Health score**: 0-100 overall assessment
- **AI-ready**: JSON with interpretations

## 📊 Sample Output

```json
{
  "session_summary": {
    "overall_health_status": {
      "score": 85,
      "status": "excellent"
    },
    "key_findings": [
      "Heart rate showed increasing trend",
      "HRV analysis: low stress (SDNN: 304ms)"
    ],
    "recommendations": [
      "Continue current wellness practices"
    ]
  },
  "physiological_vitals": {
    "heart_rate": {
      "samples": [...],
      "average": 71.6,
      "trend": "increasing",
      "interpretation": "HR increased from 68 to 73 BPM"
    }
  }
}
```

## 📁 Project Structure

```
pixelcare/
├── app/
│   ├── vitals/              # Vitals collection modules
│   │   ├── live_collector.py    # Main orchestrator
│   │   ├── heart_rate_chrom.py  # CHROM rPPG (SOTA)
│   │   ├── breathing_rate.py    # Breathing detection
│   │   ├── blink_detector.py    # EAR method
│   │   ├── gaze_tracker.py      # Gaze tracking
│   │   ├── head_pose_estimator.py
│   │   ├── posture_analyzer.py
│   │   ├── movement_detector.py
│   │   ├── facial_action_units.py
│   │   ├── hrv_analyzer.py
│   │   ├── emotion.py
│   │   └── README.md
│   └── ui/                  # Gradio web interface
│       ├── main.py              # Single entry point
│       ├── agent.py             # AI health agent
│       └── README.md
├── requirements.txt
├── pyproject.toml
├── run_ui.sh               # Launch UI
└── README.md               # This file
```

## 🔬 State-of-the-Art Algorithms

| Feature | Algorithm | Reference |
|---------|-----------|-----------|
| Heart Rate | CHROM rPPG | De Haan & Jeanne (2013) |
| Blink Detection | EAR | Soukupová & Čech (2016) |
| Head Pose | solvePnP | OpenCV |
| Face/Pose | MediaPipe | Google Research |
| HRV | Time-domain | Task Force (1996) |

## 🎯 Usage

### Web UI (Recommended)

```bash
./run_ui.sh
```

**Features:**
- 📊 Vitals Collection tab (click button)
- 💬 AI Chat tab (ask about vitals)
- Beautiful visual display
- JSON export

### Command Line

```bash
cd app/vitals
python live_collector.py
```

**Features:**
- Live camera display with metrics
- Console output
- JSON file saved

## 📦 Dependencies

```
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
scipy>=1.11.0
gradio>=4.0.0
```

## 🎓 Technical Highlights

- **CHROM rPPG**: Chrominance-based heart rate (better than GREEN channel)
- **EAR Method**: Research-validated blink detection
- **MediaPipe**: Google's SOTA face mesh (468 landmarks) and pose (33 landmarks)
- **Clinical Accuracy**: ±2-4 BPM for heart rate
- **Real-time**: 30 FPS capture with live display
- **Privacy**: All processing local, no data sent
- **Rich Sampling**: 70+ timestamped data points per session
- **LLM-Ready**: JSON with interpretations and recommendations

## 🔮 Roadmap

### Phase 2 (Planned)
- [ ] Historical tracking and trends
- [ ] Medical report analysis
- [ ] Multi-user support
- [ ] Export PDF reports
- [ ] Stress level calculation
- [ ] Multi-language support

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

## 📄 License

See LICENSE file.

## 🙏 Acknowledgments

- MediaPipe by Google Research
- OpenCV community
- Research papers cited in documentation
