# Deploy PixelCare to Hugging Face Spaces

## 📝 Space Details

### Basic Information

**Space Name:** `pixelcare-virtual-doctor`

**Display Name:** PixelCare - Virtual Doctor

**Description:**
```
Your 24/7 Virtual Doctor for Second Opinions 🏥

AI-powered health companion that:
• Measures 10 vital signs from webcam in 10 seconds
• Analyzes medical reports with transparent reasoning
• Provides expert second opinions in plain language
• 100% private - all processing happens locally

Not replacing your doctor - Empowering you with informed health decisions.

Features: Heart Rate (CHROM rPPG), HRV, Breathing, Blink Rate, Gaze, Head Pose, Posture, Movement, Emotion, Facial AUs
```

**Tags:**
```
healthcare, medical, ai-doctor, health-monitoring, computer-vision, 
gradio, opencv, mediapipe, rppg, vital-signs, telemedicine, 
second-opinion, health-ai, wellness, agentic-ai
```

**License:** `apache-2.0`

**SDK:** `gradio`

**Python Version:** `3.10`

**Visibility:** `public`

## 📁 Required Files

### 1. Create `app.py` (Entry Point)

```python
#!/usr/bin/env python3
import gradio as gr
import sys
import json
sys.path.append('app/vitals')
sys.path.append('app/ui')

from app.vitals.live_collector import LiveVitalsCollector
from app.ui.agent import HealthAgent

agent = HealthAgent()
latest_vitals = None

def collect_vitals():
    global latest_vitals
    collector = LiveVitalsCollector(duration=10, headless=True)
    latest_vitals = collector.collect()
    return latest_vitals

def format_vitals_display(vitals):
    if not vitals:
        return "No vitals collected yet"
    
    summary = vitals.get('session_summary', {})
    pv = vitals.get('physiological_vitals', {})
    
    html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white;">
        <h2>📊 Health Status: {summary.get('overall_health_status', {}).get('status', 'N/A').upper()}</h2>
        <h3>Score: {summary.get('overall_health_status', {}).get('score', 0)}/100</h3>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #e74c3c;">
            <h3>❤️ Heart Rate</h3>
            <p style="font-size: 24px; font-weight: bold;">{pv.get('heart_rate', {}).get('average', 'N/A')} BPM</p>
            <p style="font-size: 12px; color: #666;">{pv.get('heart_rate', {}).get('interpretation', '')}</p>
        </div>
        
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #3498db;">
            <h3>🫁 Breathing Rate</h3>
            <p style="font-size: 24px; font-weight: bold;">{pv.get('breathing_rate', {}).get('average', 'N/A')} BPM</p>
            <p style="font-size: 12px; color: #666;">{pv.get('breathing_rate', {}).get('interpretation', '')}</p>
        </div>
        
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #9b59b6;">
            <h3>💓 HRV</h3>
            <p style="font-size: 18px; font-weight: bold;">SDNN: {pv.get('hrv', {}).get('sdnn', 'N/A')}ms</p>
            <p style="font-size: 12px; color: #666;">Stress: {pv.get('hrv', {}).get('stress_level', 'N/A').upper()}</p>
        </div>
        
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #f39c12;">
            <h3>👁️ Blink Rate</h3>
            <p style="font-size: 24px; font-weight: bold;">{vitals.get('eye_attention', {}).get('blink_rate', {}).get('average', 'N/A')}/min</p>
            <p style="font-size: 12px; color: #666;">{vitals.get('eye_attention', {}).get('blink_rate', {}).get('interpretation', '')}</p>
        </div>
    </div>
    
    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px;">
        <h3>🔍 Key Findings</h3>
        <ul>
            {''.join([f'<li>{finding}</li>' for finding in summary.get('key_findings', [])])}
        </ul>
    </div>
    
    <div style="background: #d4edda; padding: 15px; border-radius: 10px; margin-top: 15px; border-left: 4px solid #28a745;">
        <h3>💡 Recommendations</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in summary.get('recommendations', [])])}
        </ul>
    </div>
    """
    
    return html

def chat_with_vitals(message, history):
    global latest_vitals
    
    if latest_vitals and "vitals" in message.lower():
        vitals_summary = json.dumps(latest_vitals.get('session_summary', {}), indent=2)
        message = f"{message}\n\nCurrent vitals:\n{vitals_summary}"
    
    thinking_text = ""
    answer_text = ""
    
    for thinking, answer in agent.chat(message):
        thinking_text = thinking
        answer_text = answer
        
        if thinking_text:
            thinking_display = f"""<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 15px; border-radius: 10px; margin-bottom: 15px; 
                                    border-left: 4px solid #764ba2;">
                <div style="color: #fff; font-weight: bold; margin-bottom: 8px;">🤔 Thinking</div>
                <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap;">{thinking_text}</div>
            </div>"""
            
            answer_display = f"""<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; 
                                  border-left: 4px solid #28a745;">
                <div style="color: #28a745; font-weight: bold; margin-bottom: 8px;">💬 Answer</div>
                <div style="color: #333;">{answer_text}</div>
            </div>"""
            
            full_response = thinking_display + answer_display
        else:
            full_response = answer_text
        
        yield full_response

def run_vitals_collection():
    vitals = collect_vitals()
    return format_vitals_display(vitals), json.dumps(vitals, indent=2)

with gr.Blocks(title="PixelCare - Virtual Doctor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏥 PixelCare - Your Virtual Doctor for Second Opinions")
    gr.Markdown("Collect vitals from webcam and chat with AI about your health")
    
    with gr.Tabs():
        with gr.Tab("📊 Vitals Collection"):
            gr.Markdown("### Collect Your Vitals in 10 Seconds")
            gr.Markdown("⚠️ **Note:** Allow camera access when prompted")
            
            collect_btn = gr.Button("🎥 Start Vitals Collection", variant="primary", size="lg")
            
            vitals_display = gr.HTML(label="Vitals Summary")
            
            with gr.Accordion("📄 Raw JSON Data", open=False):
                vitals_json = gr.JSON(label="Complete Data")
            
            collect_btn.click(
                fn=run_vitals_collection,
                outputs=[vitals_display, vitals_json]
            )
        
        with gr.Tab("💬 AI Chat"):
            gr.Markdown("### Chat with Your Virtual Doctor")
            
            gr.ChatInterface(
                fn=chat_with_vitals,
                examples=[
                    "Analyze my latest vitals",
                    "What do my vitals indicate?",
                    "How can I improve my HRV?",
                    "What is a normal heart rate?",
                    "Explain my stress levels"
                ]
            )
    
    gr.Markdown("""
    ---
    **Medical Disclaimer:** PixelCare provides health information and second opinions. 
    Not a replacement for licensed medical professionals. Always consult your doctor for medical decisions.
    """)

if __name__ == "__main__":
    demo.launch()
```

### 2. Create `requirements.txt`

```
opencv-python-headless==4.8.1.78
mediapipe==0.10.14
numpy==1.26.4
scipy==1.11.4
gradio==4.44.0
```

### 3. Create `README.md` for Space

```markdown
---
title: PixelCare - Virtual Doctor
emoji: 🏥
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - healthcare
  - medical
  - computer-vision
  - vital-signs
  - telemedicine
---

# PixelCare 🏥

**Your Virtual Doctor for Second Opinions**

## What is PixelCare?

AI-powered health companion that:
- 🩺 Measures 10 vital signs from webcam in 10 seconds
- 📄 Analyzes medical reports with transparent reasoning
- 💬 Provides expert second opinions in plain language
- 🔒 100% private - all processing happens locally

## Features

### Virtual Examination
- ❤️ Heart Rate (CHROM rPPG) - ±2-4 BPM accuracy
- 💓 HRV (Stress indicator)
- 🫁 Breathing Rate
- 👁️ Blink Rate
- 👀 Gaze Tracking
- 🧭 Head Pose
- 🧍 Posture Analysis
- 🤸 Movement/Fidgeting
- 😊 Emotion Detection
- 😀 Facial Action Units

### AI Chat
- Natural conversation with virtual doctor
- Transparent clinical reasoning
- Personalized health recommendations

## How to Use

1. **Vitals Collection Tab**
   - Click "Start Vitals Collection"
   - Allow camera access
   - Wait 10 seconds
   - View your health report

2. **AI Chat Tab**
   - Ask health questions
   - Get expert second opinions
   - See AI's reasoning process

## Medical Disclaimer

PixelCare provides health information and second opinions. Not a replacement for licensed medical professionals. Always consult your doctor for medical diagnosis and treatment.

## Technology

- MediaPipe (Google Research)
- CHROM rPPG for heart rate
- EAR method for blink detection
- Clinical-grade algorithms

---

**Not replacing your doctor - Empowering you with informed health decisions**
```

## 🚀 Deployment Steps

### Step 1: Prepare Repository

```bash
cd /Users/angelkashyap/hackathon/pixelcare

# Create app.py at root
cp app/ui/main.py app.py
# Edit app.py to use relative imports

# Ensure requirements.txt uses headless OpenCV
# opencv-python-headless (not opencv-python)
```

### Step 2: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in details:
   - **Owner:** Your username
   - **Space name:** `pixelcare-virtual-doctor`
   - **License:** Apache 2.0
   - **SDK:** Gradio
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public

### Step 3: Push to Space

```bash
# Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/pixelcare-virtual-doctor
cd pixelcare-virtual-doctor

# Copy files
cp -r /Users/angelkashyap/hackathon/pixelcare/app .
cp /Users/angelkashyap/hackathon/pixelcare/app.py .
cp /Users/angelkashyap/hackathon/pixelcare/requirements.txt .

# Create README.md with frontmatter (see above)

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### Step 4: Configure Space Settings

In Space settings:
- **Hardware:** CPU basic (free tier)
- **Persistent storage:** Not needed
- **Secrets:** None needed (all local)
- **Sleep time:** Default (48 hours)

## ⚠️ Important Notes

### Free Tier Limitations

**CPU Basic (Free):**
- ✅ Sufficient for PixelCare
- ✅ 2 vCPU, 16GB RAM
- ⚠️ Sleeps after 48h inactivity
- ⚠️ May have queue during high traffic

### Camera Access

**Browser Permissions:**
- Users must allow camera access
- Works on HTTPS (Hugging Face provides)
- May not work on some mobile browsers

### Performance

**Expected:**
- Vitals collection: 10-15 seconds
- AI response: 2-5 seconds
- First load: 30-60 seconds (model loading)

### Troubleshooting

**If space fails to build:**
1. Check requirements.txt uses `opencv-python-headless`
2. Ensure all imports are relative
3. Check logs in Space settings

**If camera doesn't work:**
1. User must allow permissions
2. HTTPS required (automatic on HF)
3. Some browsers block camera in iframes

## 📊 Space Metadata

Add to top of README.md:

```yaml
---
title: PixelCare - Virtual Doctor
emoji: 🏥
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
---
```

## 🎯 Post-Deployment

### Share Your Space

**URL:** `https://huggingface.co/spaces/YOUR_USERNAME/pixelcare-virtual-doctor`

**Embed in Website:**
```html
<iframe
  src="https://YOUR_USERNAME-pixelcare-virtual-doctor.hf.space"
  frameborder="0"
  width="850"
  height="450"
></iframe>
```

### Monitor Usage

- View in Space settings
- Check logs for errors
- Monitor user feedback

### Update Space

```bash
# Make changes locally
git add .
git commit -m "Update description"
git push
# Space rebuilds automatically
```

## 💡 Tips for Free Hosting

1. **Use CPU Basic** - Sufficient for PixelCare
2. **Optimize imports** - Faster cold starts
3. **Add examples** - Help users get started
4. **Clear disclaimer** - Medical liability
5. **Monitor logs** - Fix issues quickly

## 🔗 Useful Links

- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces
- Gradio Documentation: https://gradio.app/docs
- Space Hardware: https://huggingface.co/docs/hub/spaces-overview#hardware-resources
