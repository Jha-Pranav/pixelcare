#!/usr/bin/env -S uv run
"""PixelCare - AI Health Companion"""
import gradio as gr
import sys
import json
import time
import cv2
import numpy as np
sys.path.append('../vitals')

from live_collector import LiveVitalsCollector
from agent import HealthAgent

agent = HealthAgent()
latest_vitals = None
collecting = False

def get_mood_prompt(vitals):
    """Adjust LLM mood based on vitals"""
    summary = vitals.get('session_summary', {})
    status = summary.get('overall_health_status', {})
    score = status.get('score', 50)
    
    if score >= 80:
        return "You are an enthusiastic and encouraging health companion. The user's vitals are excellent! Be celebratory and motivating."
    elif score >= 60:
        return "You are a supportive and positive health companion. The user's vitals are good with room for improvement. Be encouraging and constructive."
    elif score >= 40:
        return "You are a caring and gentle health companion. The user's vitals show some concerns. Be empathetic and provide actionable advice."
    else:
        return "You are a compassionate and serious health companion. The user's vitals need attention. Be caring but emphasize the importance of taking action."

def format_vitals_summary(vitals):
    """Format vitals as beautiful HTML"""
    summary = vitals.get('session_summary', {})
    pv = vitals.get('physiological_vitals', {})
    status = summary.get('overall_health_status', {})
    
    score = status.get('score', 0)
    status_text = status.get('status', 'N/A').upper()
    
    # Color based on score
    if score >= 80:
        color = "#28a745"
        emoji = "🎉"
    elif score >= 60:
        color = "#ffc107"
        emoji = "👍"
    else:
        color = "#dc3545"
        emoji = "⚠️"
    
    html = f"""
    <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); padding: 25px; border-radius: 15px; color: white; margin-bottom: 20px;">
        <h2 style="margin: 0;">{emoji} Health Score: {score}/100</h2>
        <h3 style="margin: 10px 0 0 0;">Status: {status_text}</h3>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #e74c3c; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #e74c3c;">❤️ Heart Rate</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 0; color: #333;">{pv.get('heart_rate', {}).get('average', 'N/A')} BPM</p>
            <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">{pv.get('heart_rate', {}).get('interpretation', '')}</p>
        </div>
        
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #3498db;">🫁 Breathing</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 0; color: #333;">{pv.get('breathing_rate', {}).get('average', 'N/A')} BPM</p>
            <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">{pv.get('breathing_rate', {}).get('interpretation', '')}</p>
        </div>
        
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #9b59b6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #9b59b6;">💓 HRV</h3>
            <p style="font-size: 20px; font-weight: bold; margin: 0; color: #333;">SDNN: {pv.get('hrv', {}).get('sdnn', 'N/A')}ms</p>
            <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">Stress: {pv.get('hrv', {}).get('stress_level', 'N/A').upper()}</p>
        </div>
        
        <div style="background: #fff; padding: 15px; border-radius: 10px; border-left: 4px solid #f39c12; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #f39c12;">👁️ Blink Rate</h3>
            <p style="font-size: 28px; font-weight: bold; margin: 0; color: #333;">{vitals.get('eye_attention', {}).get('blink_rate', {}).get('average', 'N/A')}/min</p>
            <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">{vitals.get('eye_attention', {}).get('blink_rate', {}).get('interpretation', '')}</p>
        </div>
    </div>
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #17a2b8;">
        <h3 style="margin: 0 0 15px 0; color: #17a2b8;">🔍 Key Findings</h3>
        <ul style="margin: 0; padding-left: 20px;">
            {''.join([f'<li style="margin: 8px 0; color: #333;">{finding}</li>' for finding in summary.get('key_findings', [])])}
        </ul>
    </div>
    
    <div style="background: #d4edda; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745;">
        <h3 style="margin: 0 0 15px 0; color: #28a745;">💡 Recommendations</h3>
        <ul style="margin: 0; padding-left: 20px;">
            {''.join([f'<li style="margin: 8px 0; color: #333;">{rec}</li>' for rec in summary.get('recommendations', [])])}
        </ul>
    </div>
    """
    
    return html

def collect_vitals_with_feed():
    """Collect vitals and show camera feed"""
    global latest_vitals, collecting
    collecting = True
    
    # Start camera
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    frame_count = 0
    
    # Show camera feed for 10 seconds
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            elapsed = int(time.time() - start_time)
            remaining = 10 - elapsed
            
            # Add timer overlay
            cv2.putText(frame, f"Collecting: {remaining}s", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            yield frame_rgb, None, None
            time.sleep(0.1)
    
    cap.release()
    
    # Now collect vitals
    yield None, "🔬 Analyzing vitals...", None
    collector = LiveVitalsCollector(duration=10, headless=True)
    latest_vitals = collector.collect()
    collecting = False
    
    # Format summary
    summary_html = format_vitals_summary(latest_vitals)
    
    # Get LLM analysis with mood
    mood_prompt = get_mood_prompt(latest_vitals)
    vitals_json = json.dumps(latest_vitals, indent=2)
    
    analysis_prompt = f"""{mood_prompt}

Here are the user's vitals data:
{vitals_json}

Provide a warm, personalized analysis of their health status. Be specific about what the numbers mean and give actionable advice."""
    
    # Get AI analysis
    yield None, summary_html, "🤖 AI is analyzing your vitals..."
    
    analysis = ""
    for thinking, answer in agent.chat(analysis_prompt):
        if answer:
            analysis = answer
            
            if thinking:
                thinking_display = f"""<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        padding: 15px; border-radius: 10px; margin-bottom: 15px; 
                                        border-left: 4px solid #764ba2;">
                    <summary style="color: #fff; font-weight: bold; cursor: pointer; user-select: none;">
                        🤔 AI Thinking Process (click to expand)
                    </summary>
                    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking}</div>
                </details>"""
                
                answer_display = f"""<div style="background: #f8f9fa; padding: 20px; border-radius: 10px; 
                                      border-left: 4px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 12px; font-size: 18px;">🤖 AI Health Analysis</div>
                    <div style="color: #333; line-height: 1.6;">{answer}</div>
                </div>"""
                
                full_analysis = thinking_display + answer_display
            else:
                full_analysis = f"""<div style="background: #f8f9fa; padding: 20px; border-radius: 10px; 
                                      border-left: 4px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 12px; font-size: 18px;">🤖 AI Health Analysis</div>
                    <div style="color: #333; line-height: 1.6;">{answer}</div>
                </div>"""
            
            yield None, summary_html, full_analysis

with gr.Blocks(title="PixelCare AI") as demo:
    gr.Markdown("# 🏥 PixelCare - AI Health Companion")
    gr.Markdown("Click button below to start vitals collection with live camera feed")
    
    with gr.Row():
        collect_btn = gr.Button("🎥 Start Vitals Collection", variant="primary", size="lg")
    
    with gr.Row():
        camera_feed = gr.Image(label="📹 Camera Feed", type="numpy")
    
    with gr.Row():
        vitals_summary = gr.HTML(label="📊 Vitals Summary")
    
    with gr.Row():
        ai_analysis = gr.HTML(label="🤖 AI Analysis")
    
    collect_btn.click(
        fn=collect_vitals_with_feed,
        outputs=[camera_feed, vitals_summary, ai_analysis]
    )

if __name__ == "__main__":
    from config import get_model_config
    config = get_model_config()
    
    print("🏥 PixelCare AI")
    print("=" * 50)
    print(f"📍 http://localhost:7860")
    print(f"🤖 {config['name']}")
    print("=" * 50)
    
    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)
