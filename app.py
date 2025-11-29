#!/usr/bin/env python3
"""PixelCare - Cloud Demo (Chat + Document Analysis)"""
import gradio as gr
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add paths
root = Path(__file__).parent
sys.path.insert(0, str(root / "app" / "ui"))
sys.path.insert(0, str(root / "app"))

# Import with absolute imports
import agent
import document_processor

health_agent = agent.HealthAgent()
doc_processor = document_processor.DocumentProcessor()
uploaded_docs = []

# Rate limiting
user_requests = defaultdict(list)
MAX_REQUESTS_PER_HOUR = 20
MAX_REQUESTS_PER_MINUTE = 5

def check_rate_limit(session_id):
    """Check if user exceeded rate limit"""
    now = datetime.now()
    
    # Clean old requests
    user_requests[session_id] = [
        req_time for req_time in user_requests[session_id]
        if now - req_time < timedelta(hours=1)
    ]
    
    # Check limits
    recent_requests = [
        req_time for req_time in user_requests[session_id]
        if now - req_time < timedelta(minutes=1)
    ]
    
    if len(recent_requests) >= MAX_REQUESTS_PER_MINUTE:
        return False, "⚠️ Rate limit: Max 5 requests per minute. Please wait."
    
    if len(user_requests[session_id]) >= MAX_REQUESTS_PER_HOUR:
        return False, "⚠️ Rate limit: Max 20 requests per hour. Please try again later."
    
    user_requests[session_id].append(now)
    return True, None

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

def clear_documents():
    """Clear uploaded documents"""
    global uploaded_docs
    uploaded_docs = []
    return "Documents cleared"

def chat_fn(message, history):
    """Chat with document support and rate limiting"""
    global uploaded_docs
    
    if not message:
        return history
    
    # Rate limiting (use a default session if request not available)
    try:
        import inspect
        frame = inspect.currentframe()
        session_id = str(id(frame))
    except:
        session_id = "default"
    
    allowed, error_msg = check_rate_limit(session_id)
    if not allowed:
        history.append((message, error_msg))
        return history
    
    # If documents uploaded, use vision
    if uploaded_docs:
        content = [{"type": "text", "text": message}]
        for doc in uploaded_docs:
            content.extend(doc['content'])
        
        response = ""
        for thinking, answer in health_agent.chat_with_vision(content):
            response = answer if not thinking else f"**Thinking:** {thinking}\n\n{answer}"
        
        history.append((message, response))
        return history
    
    # Regular chat
    response = ""
    for thinking, answer in health_agent.chat(message):
        response = answer if not thinking else f"**Thinking:** {thinking}\n\n{answer}"
    
    history.append((message, response))
    return history

with gr.Blocks(title="PixelCare AI") as demo:
    gr.Markdown("# 🏥 PixelCare - AI Health Companion")
    gr.Markdown("""
    **🤖 AI Health Assistant** - Upload medical documents and get expert insights!
    
    ✅ **Working Now:** Document analysis (PDFs, X-rays, prescriptions), Health Q&A
    
    🚧 **Coming Soon:** Video-based vitals (upload 10-sec video for basic vitals)
    
    📥 **Full Features:** [Install locally](https://github.com/Jha-Pranav/pixelcare) for real-time camera vitals (heart rate, breathing, HRV, stress in 10 seconds)
    
    🔒 **Rate Limits:** 5 requests/minute, 20 requests/hour
    """)
    
    chatbot = gr.Chatbot(label="Chat", height=500)
    
    msg = gr.Textbox(
        label="Message", 
        placeholder="Ask about your health or upload medical documents..."
    )
    
    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary")
        file_upload = gr.UploadButton("Upload", file_count="multiple", file_types=[".pdf", ".jpg", ".jpeg", ".png", ".webp"])
        clear_btn = gr.Button("Clear Docs", variant="secondary")
    
    file_status = gr.Markdown("")
    
    gr.Examples(
        examples=[
            "What is a normal heart rate?",
            "How can I reduce stress naturally?",
            "Explain blood pressure readings",
            "What does high cholesterol mean?",
            "Analyze my blood test report",
            "What does this X-ray show?"
        ],
        inputs=msg
    )
    
    file_upload.upload(handle_file_upload, inputs=[file_upload], outputs=[file_status])
    clear_btn.click(clear_documents, outputs=[file_status])
    
    msg.submit(chat_fn, [msg, chatbot], [chatbot]).then(lambda: "", None, [msg])
    submit_btn.click(chat_fn, [msg, chatbot], [chatbot]).then(lambda: "", None, [msg])

if __name__ == "__main__":
    demo.launch()
