#!/usr/bin/env python3
"""PixelCare - Cloud Demo (Chat Only)"""
import gradio as gr
import sys
from pathlib import Path

# Add paths
root = Path(__file__).parent
sys.path.insert(0, str(root / "app" / "ui"))

# Import only what we need
from agent import HealthAgent

agent = HealthAgent()

def chat_response(message, history):
    """Simple chat without vitals"""
    thinking_text = ""
    answer_text = ""
    
    for thinking, answer in agent.chat(message):
        thinking_text = thinking
        answer_text = answer
        
        if thinking_text:
            full_response = f"""
<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #764ba2;">
    <summary style="color: #fff; font-weight: bold; cursor: pointer;">🤔 Thinking (click to expand)</summary>
    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking_text}</div>
</details>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745;">
    <div style="color: #28a745; font-weight: bold; margin-bottom: 8px;">💬 Answer</div>
    <div style="color: #333;">{answer_text}</div>
</div>
"""
        else:
            full_response = answer_text
        
        yield full_response

with gr.Blocks(title="PixelCare AI") as demo:
    gr.Markdown("# 🏥 PixelCare - AI Health Companion")
    gr.Markdown("⚠️ **Demo Mode** - Vitals collection requires local camera. Chat available!")
    
    gr.ChatInterface(
        fn=chat_response,
        examples=[
            "What is a normal heart rate?",
            "How can I reduce stress?",
            "Explain blood pressure",
            "Signs of good health?",
            "Improve sleep quality?"
        ]
    )
    
    gr.Markdown("""
    ---
    ### 📹 Full Version (Local)
    
    **10 vitals in 10 seconds from webcam:**
    ```bash
    git clone https://github.com/Jha-Pranav/pixelcare
    cd pixelcare
    pip install -r requirements.txt
    cd app/ui && python main.py
    ```
    
    **Features:**
    - 📊 Heart Rate, HRV, Breathing, Blink Rate, etc.
    - 🤖 Agentic AI (auto-collects vitals)
    - 🔒 100% private & local
    """)

if __name__ == "__main__":
    demo.launch()
