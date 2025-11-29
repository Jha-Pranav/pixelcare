#!/usr/bin/env -S uv run
"""PixelCare - AI Health Companion"""
import gradio as gr
import sys
import json
import time
import cv2
sys.path.append('../vitals')

from live_collector import LiveVitalsCollector
from agent import HealthAgent

agent = HealthAgent()
latest_vitals = None

def get_mood_prompt(vitals):
    """Adjust LLM mood based on vitals"""
    summary = vitals.get('session_summary', {})
    status = summary.get('overall_health_status', {})
    score = status.get('score', 50)
    
    if score >= 80:
        return "You are enthusiastic and encouraging. The vitals are excellent! Be celebratory."
    elif score >= 60:
        return "You are supportive and positive. The vitals are good. Be encouraging."
    elif score >= 40:
        return "You are caring and gentle. The vitals show concerns. Be empathetic."
    else:
        return "You are compassionate and serious. The vitals need attention. Be caring but firm."

def format_vitals_summary(vitals):
    """Format vitals as beautiful HTML"""
    summary = vitals.get('session_summary', {})
    pv = vitals.get('physiological_vitals', {})
    status = summary.get('overall_health_status', {})
    
    score = status.get('score', 0)
    status_text = status.get('status', 'N/A').upper()
    
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
<div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 15px;">
    <h2 style="margin: 0;">{emoji} Health Score: {score}/100 - {status_text}</h2>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 15px;">
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #e74c3c;">
        <h4 style="margin: 0 0 8px 0; color: #e74c3c;">❤️ Heart Rate</h4>
        <p style="font-size: 24px; font-weight: bold; margin: 0;">{pv.get('heart_rate', {}).get('average', 'N/A')} BPM</p>
    </div>
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #3498db;">
        <h4 style="margin: 0 0 8px 0; color: #3498db;">🫁 Breathing</h4>
        <p style="font-size: 24px; font-weight: bold; margin: 0;">{pv.get('breathing_rate', {}).get('average', 'N/A')} BPM</p>
    </div>
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #9b59b6;">
        <h4 style="margin: 0 0 8px 0; color: #9b59b6;">💓 HRV</h4>
        <p style="font-size: 18px; font-weight: bold; margin: 0;">SDNN: {pv.get('hrv', {}).get('sdnn', 'N/A')}ms</p>
    </div>
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #f39c12;">
        <h4 style="margin: 0 0 8px 0; color: #f39c12;">👁️ Blinks</h4>
        <p style="font-size: 24px; font-weight: bold; margin: 0;">{vitals.get('eye_attention', {}).get('blink_rate', {}).get('average', 'N/A')}/min</p>
    </div>
</div>

<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 12px;">
    <h4 style="margin: 0 0 10px 0; color: #17a2b8;">🔍 Key Findings</h4>
    <ul style="margin: 0; padding-left: 20px;">
        {''.join([f'<li style="margin: 5px 0;">{finding}</li>' for finding in summary.get('key_findings', [])])}
    </ul>
</div>

<div style="background: #d4edda; padding: 15px; border-radius: 8px;">
    <h4 style="margin: 0 0 10px 0; color: #28a745;">💡 Recommendations</h4>
    <ul style="margin: 0; padding-left: 20px;">
        {''.join([f'<li style="margin: 5px 0;">{rec}</li>' for rec in summary.get('recommendations', [])])}
    </ul>
</div>
"""
    return html

def chat_with_vitals(message, history):
    """Chat with AI and handle vitals collection"""
    global latest_vitals
    
    # Check if user wants vitals collection
    if any(word in message.lower() for word in ['collect', 'measure', 'scan', 'analyze vitals', 'check vitals']):
        # Show camera feed with countdown
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        
        while time.time() - start_time < 10:
            ret, frame = cap.read()
            if ret:
                elapsed = int(time.time() - start_time)
                remaining = 10 - elapsed
                yield f"📹 **Collecting vitals from camera... {remaining}s remaining**\n\n*(Camera is active, please look at your webcam)*"
                time.sleep(0.5)
        
        cap.release()
        
        # Collect vitals
        yield "🔬 **Analyzing vitals data...**"
        collector = LiveVitalsCollector(duration=10, headless=True)
        latest_vitals = collector.collect()
        
        # Format summary
        summary_html = format_vitals_summary(latest_vitals)
        yield summary_html
        
        # Get AI analysis with mood
        mood_prompt = get_mood_prompt(latest_vitals)
        vitals_json = json.dumps(latest_vitals.get('session_summary', {}), indent=2)
        
        analysis_prompt = f"""{mood_prompt}

Here are the user's vitals:
{vitals_json}

Provide a warm, personalized analysis. Be specific and give actionable advice."""
        
        # Stream AI response
        thinking_text = ""
        answer_text = ""
        
        for thinking, answer in agent.chat(analysis_prompt):
            thinking_text = thinking
            answer_text = answer
            
            if thinking_text:
                thinking_display = f"""<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        padding: 15px; border-radius: 10px; margin: 15px 0; 
                                        border-left: 4px solid #764ba2;">
                    <summary style="color: #fff; font-weight: bold; cursor: pointer;">
                        🤔 AI Thinking (click to expand)
                    </summary>
                    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking_text}</div>
                </details>"""
                
                answer_display = f"""<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px;
                                      border-left: 4px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">🤖 AI Health Analysis</div>
                    <div style="color: #333; line-height: 1.6;">{answer_text}</div>
                </div>"""
                
                full_response = summary_html + thinking_display + answer_display
            else:
                full_response = summary_html + f"""<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px;
                                      border-left: 4px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">🤖 AI Health Analysis</div>
                    <div style="color: #333; line-height: 1.6;">{answer_text}</div>
                </div>"""
            
            yield full_response
        return
    
    # Regular chat
    if latest_vitals and any(word in message.lower() for word in ['vitals', 'health', 'heart', 'breathing', 'stress']):
        vitals_summary = json.dumps(latest_vitals.get('session_summary', {}), indent=2)
        message = f"{message}\n\nMy vitals:\n{vitals_summary}"
    
    thinking_text = ""
    answer_text = ""
    
    for thinking, answer in agent.chat(message):
        thinking_text = thinking
        answer_text = answer
        
        if thinking_text:
            thinking_display = f"""<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 15px; border-radius: 10px; margin-bottom: 15px; 
                                    border-left: 4px solid #764ba2;">
                <summary style="color: #fff; font-weight: bold; cursor: pointer;">
                    🤔 Thinking (click to expand)
                </summary>
                <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking_text}</div>
            </details>"""
            
            answer_display = f"""<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; 
                                  border-left: 4px solid #28a745;">
                <div style="color: #28a745; font-weight: bold; margin-bottom: 8px;">💬 Answer</div>
                <div style="color: #333;">{answer_text}</div>
            </div>"""
            
            full_response = thinking_display + answer_display
        else:
            full_response = answer_text
        
        yield full_response

with gr.Blocks(title="PixelCare AI") as demo:
    gr.Markdown("# 🏥 PixelCare - AI Health Companion")
    gr.Markdown("💬 Chat with AI • Type **'collect vitals'** to start analysis")
    
    gr.ChatInterface(
        fn=chat_with_vitals,
        examples=[
            "🎥 Collect vitals",
            "Analyze my health",
            "What is a normal heart rate?",
            "How can I reduce stress?",
            "Explain my vitals"
        ]
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
