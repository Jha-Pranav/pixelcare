#!/usr/bin/env python3
"""PixelCare - AI Health Companion with Agentic Vitals Collection"""
import gradio as gr
import sys
import json
import time
import cv2
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vitals.live_collector import LiveVitalsCollector
from ui.agent import HealthAgent
from ui.llm import LLMClient
from ui.document_processor import DocumentProcessor
from ui.document_processor import DocumentProcessor

agent = HealthAgent()
llm_client = LLMClient()
doc_processor = DocumentProcessor()
latest_vitals = None
uploaded_docs = []

# Tool definition for vitals collection
VITALS_TOOL = {
    "type": "function",
    "function": {
        "name": "collect_vitals",
        "description": "REQUIRED: Collect real-time health vitals from the user's webcam. Use this tool when user asks to: check vitals, scan health, measure heart rate, check stress, see how they're doing, or any request about their current physical state. This captures heart rate, breathing rate, HRV, stress levels, posture, and overall health score in 10 seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why vitals collection is needed"
                }
            },
            "required": ["reason"]
        }
    }
}

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
    
    hr = pv.get('heart_rate', {})
    br = pv.get('breathing_rate', {})
    hrv = pv.get('hrv', {})
    blink = vitals.get('eye_attention', {}).get('blink_rate', {})
    
    html = f"""
<div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 15px;">
    <h2 style="margin: 0;">{emoji} Health Score: {score}/100 - {status_text}</h2>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 15px;">
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #e74c3c;">
        <h4 style="margin: 0 0 8px 0; color: #e74c3c;">❤️ Heart Rate</h4>
        <p style="font-size: 24px; font-weight: bold; margin: 0;">{hr.get('average', 'N/A')} BPM</p>
    </div>
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #3498db;">
        <h4 style="margin: 0 0 8px 0; color: #3498db;">🫁 Breathing</h4>
        <p style="font-size: 24px; font-weight: bold; margin: 0;">{br.get('average', 'N/A')} BPM</p>
    </div>
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #9b59b6;">
        <h4 style="margin: 0 0 8px 0; color: #9b59b6;">💓 HRV</h4>
        <p style="font-size: 18px; font-weight: bold; margin: 0;">SDNN: {hrv.get('sdnn', 'N/A')}ms</p>
    </div>
    <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #f39c12;">
        <h4 style="margin: 0 0 8px 0; color: #f39c12;">👁️ Blinks</h4>
        <p style="font-size: 24px; font-weight: bold; margin: 0;">{blink.get('average', 'N/A')}/min</p>
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

def collect_vitals_with_progress():
    """Collect vitals with progress UI"""
    global latest_vitals
    
    import threading
    
    result_holder = {'vitals': None}
    
    def collect():
        collector = LiveVitalsCollector(duration=10, headless=True)
        result_holder['vitals'] = collector.collect()
    
    collection_thread = threading.Thread(target=collect)
    collection_thread.start()
    
    # Progress display
    vitals_steps = [
        "❤️ Heart Rate", "🫁 Breathing Rate", "👁️ Blink Detection",
        "👀 Gaze Tracking", "🧭 Head Pose", "🧍 Posture Analysis",
        "🤸 Movement Detection", "😊 Emotion Recognition",
        "💓 HRV Analysis", "📊 Final Metrics"
    ]
    
    start_time = time.time()
    
    while time.time() - start_time < 10:
        elapsed = time.time() - start_time
        remaining = 10 - int(elapsed)
        progress = int((elapsed / 10) * 100)
        step_index = min(int((elapsed / 10) * len(vitals_steps)), len(vitals_steps) - 1)
        
        progress_html = f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white;">
    <h3 style="margin: 0 0 15px 0;">📹 Collecting Vitals from Camera</h3>
    <div style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 3px; margin-bottom: 15px;">
        <div style="background: #28a745; height: 25px; border-radius: 6px; width: {progress}%; transition: width 0.3s;">
            <div style="text-align: center; line-height: 25px; font-weight: bold;">{progress}%</div>
        </div>
    </div>
    <div style="font-size: 24px; margin-bottom: 10px;">⏱️ {remaining} seconds remaining</div>
    <div style="font-size: 14px; opacity: 0.9;">Camera is active - please look at your webcam</div>
</div>

<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px;">
    <h4 style="margin: 0 0 12px 0; color: #333;">🔬 Vitals Being Collected:</h4>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
"""
        for i, vital in enumerate(vitals_steps):
            if i < step_index:
                status = "✅"
                opacity = "1"
            elif i == step_index:
                status = "⏳"
                opacity = "1"
            else:
                status = "⏸️"
                opacity = "0.4"
            
            progress_html += f'<div style="opacity: {opacity}; padding: 8px; background: white; border-radius: 6px;">{status} {vital}</div>'
        
        progress_html += "</div></div>"
        yield progress_html
        time.sleep(0.5)
    
    collection_thread.join()
    latest_vitals = result_holder['vitals']
    
    # Analysis progress
    for i in range(6):
        progress = int(((i + 1) / 6) * 100)
        yield f"""
<div style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); padding: 20px; border-radius: 12px; color: white;">
    <h3 style="margin: 0 0 15px 0;">🔬 Analyzing Vitals Data</h3>
    <div style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 3px;">
        <div style="background: #ffc107; height: 25px; border-radius: 6px; width: {progress}%;">
            <div style="text-align: center; line-height: 25px; font-weight: bold; color: #333;">{progress}%</div>
        </div>
    </div>
</div>
"""
        time.sleep(0.3)
    
    return format_vitals_summary(latest_vitals)

def handle_file_upload(files):
    """Handle uploaded documents"""
    global uploaded_docs
    
    if not files:
        uploaded_docs = []
        return ""
    
    uploaded_docs = []
    file_list = files if isinstance(files, list) else [files]
    
    for file in file_list:
        try:
            content = doc_processor.process_file(file.name)
            uploaded_docs.append({
                'name': Path(file.name).name,
                'content': content
            })
        except Exception as e:
            return f"**❌ Error:** {Path(file.name).name} - {str(e)}"
    
    names = [doc['name'] for doc in uploaded_docs]
    return f"**✅ Uploaded:** {', '.join(names)}"

def chat_with_agentic_vitals(message, history):
    """Agentic chat with intelligent vitals collection"""
    global latest_vitals, uploaded_docs
    
    # If documents are uploaded, pass directly to agent with vision
    if uploaded_docs:
        content = [{"type": "text", "text": message}]
        for doc in uploaded_docs:
            content.extend(doc['content'])
        
        # Stream response from agent with documents
        thinking_text = ""
        answer_text = ""
        
        for thinking, answer in agent.chat_with_vision(content):
            thinking_text = thinking
            answer_text = answer
            
            if thinking_text:
                full_response = f"""
<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #764ba2;">
    <summary style="color: #fff; font-weight: bold; cursor: pointer;">🤔 Analyzing Document (click to expand)</summary>
    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking_text}</div>
</details>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745;">
    <div style="color: #28a745; font-weight: bold; margin-bottom: 8px;">📄 Document Analysis</div>
    <div style="color: #333;">{answer_text}</div>
</div>
"""
            else:
                full_response = answer_text
            
            yield full_response
        return
    
    # Build message for tool checking
    messages = [{"role": "user", "content": message}]
    
    response = llm_client.chat(messages, stream=False, tools=[VITALS_TOOL])
    
    # Check if tool was called
    if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        
        if tool_call.function.name == "collect_vitals":
            # AI decided to collect vitals
            args = json.loads(tool_call.function.arguments)
            reason = args.get('reason', 'To answer your question')
            
            yield f"🤖 **{reason}**\n\nStarting vitals collection..."
            time.sleep(1)
            
            # Run collection with progress
            for progress in collect_vitals_with_progress():
                yield progress
            
            # Now get AI analysis with vitals
            mood_prompt = get_mood_prompt(latest_vitals)
            vitals_json = json.dumps(latest_vitals.get('session_summary', {}), indent=2)
            
            analysis_prompt = f"""{mood_prompt}

User asked: {message}

Here are their vitals:
{vitals_json}

Provide a personalized response to their question using the vitals data."""
            
            # LLM processing progress
            for i in range(5):
                progress = int(((i + 1) / 5) * 100)
                yield format_vitals_summary(latest_vitals) + f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white;">
    <h3 style="margin: 0 0 15px 0;">🤖 AI Processing</h3>
    <div style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 3px;">
        <div style="background: #e74c3c; height: 25px; border-radius: 6px; width: {progress}%;">
            <div style="text-align: center; line-height: 25px; font-weight: bold;">{progress}%</div>
        </div>
    </div>
</div>
"""
                time.sleep(0.4)
            
            # Stream AI response
            thinking_text = ""
            answer_text = ""
            
            for thinking, answer in agent.chat(analysis_prompt):
                thinking_text = thinking
                answer_text = answer
                
                if thinking_text:
                    full_response = format_vitals_summary(latest_vitals) + f"""
<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #764ba2;">
    <summary style="color: #fff; font-weight: bold; cursor: pointer;">🤔 AI Thinking (click to expand)</summary>
    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking_text}</div>
</details>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">🤖 AI Health Analysis</div>
    <div style="color: #333; line-height: 1.6;">{answer_text}</div>
</div>
"""
                else:
                    full_response = format_vitals_summary(latest_vitals) + f"""
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">🤖 AI Health Analysis</div>
    <div style="color: #333; line-height: 1.6;">{answer_text}</div>
</div>
"""
                
                yield full_response
            return
    
    # Regular chat without vitals
    if latest_vitals and any(word in message.lower() for word in ['vitals', 'health', 'heart', 'breathing']):
        vitals_summary = json.dumps(latest_vitals.get('session_summary', {}), indent=2)
        message = f"{message}\n\nMy vitals:\n{vitals_summary}"
    
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
    gr.Markdown("🤖 **Agentic AI** - Ask any health question, AI will collect vitals if needed")
    
    chatbot = gr.Chatbot(label="Chat", height=500)
    
    with gr.Row():
        msg = gr.Textbox(
            label="Message", 
            placeholder="Ask about your health or upload medical documents...",
            scale=9
        )
        file_upload = gr.UploadButton("Upload", file_count="multiple", file_types=[".pdf", ".jpg", ".jpeg", ".png", ".webp"], scale=1, size="sm", variant="primary")
    
    file_status = gr.Markdown("", visible=True, elem_classes="upload-status")
    
    gr.Examples(
        examples=[
            "🎥 Check my vitals now",
            "How am I doing today? Scan my health",
            "Measure my heart rate and stress levels",
            "Am I stressed right now? What can I do about it?",
            "Why is my heart rate elevated?",
            "What's a healthy breathing rate?",
            "How can I improve my posture?",
            "Analyze my blood test report - are my values normal?",
            "What does my cholesterol level mean?",
            "Explain my CBC results in simple terms",
            "Is my vitamin D level concerning?",
            "What does this X-ray show? Any abnormalities?",
            "Explain the findings in my MRI report",
            "What should I know about this ultrasound?",
            "Explain my prescription - what are these medications for?",
            "What are the side effects I should watch for?",
            "When and how should I take these medications?",
            "Can these medications interact with each other?",
            "Compare my current vitals with this medical report",
            "How do my vitals match what my doctor said?",
            "Should I be concerned based on my vitals and this report?",
            "What lifestyle changes can improve my health?",
                    "How can I reduce my stress naturally?",
                    "Tips for better sleep and recovery"
                ],
                inputs=msg
            )
    
    def submit_and_clear(message, chat_history):
        if chat_history is None:
            chat_history = []
        
        new_history = chat_history + [{"role": "user", "content": message}]
        
        for response in chat_with_agentic_vitals(message, chat_history):
            yield "", new_history + [{"role": "assistant", "content": response}]
    
    file_upload.upload(handle_file_upload, inputs=[file_upload], outputs=[file_status])
    
    msg.submit(submit_and_clear, [msg, chatbot], [msg, chatbot], queue=True)

if __name__ == "__main__":
    from config import get_model_config
    config = get_model_config()
    
    print("🏥 PixelCare AI - Agentic Health Companion")
    print("=" * 50)
    print(f"📍 http://localhost:7860")
    print(f"🤖 {config['name']}")
    print("🧠 Agentic vitals collection enabled")
    print("=" * 50)
    
    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)
