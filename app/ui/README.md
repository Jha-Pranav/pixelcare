# PixelCare UI

Complete Gradio-based web interface for vitals collection and AI health chat.

## Quick Start

```bash
cd app/ui
./main.py
```

Open: **http://localhost:7860**

## Features

### 📊 Vitals Collection Tab
- Click button to start 10-second collection
- Beautiful visual display with health score
- Shows: HR, BR, HRV, Blink Rate, Posture, Emotion
- Key findings and recommendations
- Raw JSON data available

### 💬 AI Chat Tab
- Chat with health assistant
- AI has access to your vitals data
- Ask: "Analyze my latest vitals"
- Get personalized health advice

## Architecture

```
app/ui/
├── main.py          # Single entry point (Gradio UI + vitals integration)
├── agent.py         # Health AI agent
├── config.py        # Configuration
└── README.md        # This file
```

## Usage

### Collect Vitals
1. Open UI at http://localhost:7860
2. Go to "Vitals Collection" tab
3. Click "Start Vitals Collection"
4. Camera captures for 10 seconds (headless mode)
5. View beautiful results

### Chat with AI
1. Go to "AI Chat" tab
2. Ask questions like:
   - "Analyze my latest vitals"
   - "What do my vitals indicate?"
   - "How can I improve my HRV?"
3. AI responds with personalized advice

## Configuration

Edit `config.py` to change:
- Ollama model
- Server URL
- Port settings

## Dependencies

```bash
gradio>=4.0.0
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
scipy>=1.11.0
```

## Troubleshooting

**Camera not opening**: Check permissions
**Port in use**: Change port in `main.py`
**Vitals not in chat**: Collect vitals first, mention "vitals" in question
