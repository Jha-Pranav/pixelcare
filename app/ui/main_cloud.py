#!/usr/bin/env python3
"""PixelCare - Cloud Version (No Camera)"""
import gradio as gr
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent import HealthAgent

agent = HealthAgent()

def chat_response(message, history):
    """Simple chat without vitals collection"""
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
    gr.Markdown("⚠️ **Demo Mode** - Vitals collection requires local camera access. Chat functionality available!")
    
    gr.ChatInterface(
        fn=chat_response,
        examples=[
            "What is a normal heart rate?",
            "How can I reduce stress?",
            "Explain blood pressure readings",
            "What are signs of good health?",
            "How to improve sleep quality?"
        ]
    )
    
    gr.Markdown("""
    ---
    ### 📹 Full Version with Vitals Collection
    
    To use vitals collection (10 metrics in 10 seconds):
    1. Clone: `git clone https://github.com/Jha-Pranav/pixelcare`
    2. Install: `pip install -r requirements.txt`
    3. Run: `cd app/ui && python main.py`
    
    **Features in local version:**
    - 📊 10 vitals from webcam
    - 🤖 Agentic AI (auto-collects when needed)
    - 🔒 100% private & local
    """)

if __name__ == "__main__":
    demo.launch()
