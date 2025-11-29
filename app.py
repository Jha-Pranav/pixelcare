#!/usr/bin/env python3
"""PixelCare - Cloud Demo (Chat + Document Analysis)"""
import gradio as gr
import sys
from pathlib import Path

# Add paths
root = Path(__file__).parent
sys.path.insert(0, str(root / "app" / "ui"))
sys.path.insert(0, str(root / "app"))

from agent import HealthAgent
from document_processor import DocumentProcessor

agent = HealthAgent()
doc_processor = DocumentProcessor()
uploaded_docs = []

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

def chat_response(message, history):
    """Chat with document support"""
    global uploaded_docs
    
    if history is None:
        history = []
    
    # If documents uploaded, use vision
    if uploaded_docs:
        content = [{"type": "text", "text": message}]
        for doc in uploaded_docs:
            content.extend(doc['content'])
        
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
            
            yield "", history + [{"role": "user", "content": message}, {"role": "assistant", "content": full_response}]
        return
    
    # Regular chat
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
        
        yield "", history + [{"role": "user", "content": message}, {"role": "assistant", "content": full_response}]

with gr.Blocks(title="PixelCare AI") as demo:
    gr.Markdown("# 🏥 PixelCare - AI Health Companion")
    gr.Markdown("""
    ⚠️ **Cloud Demo Mode** - Camera-based vitals collection requires local installation. 
    
    ✅ **Available**: Chat, Document Analysis (upload blood tests, X-rays, prescriptions)
    
    📥 **To use vitals collection**: Run locally with `./run_ui.sh` - [See README](https://github.com/Jha-Pranav/pixelcare)
    """)
    
    chatbot = gr.Chatbot(label="Chat", height=500)
    
    with gr.Row():
        msg = gr.Textbox(
            label="Message",
            placeholder="Ask health questions or upload medical documents...",
            scale=9
        )
        file_upload = gr.UploadButton("Upload", file_count="multiple", file_types=[".pdf", ".jpg", ".jpeg", ".png", ".webp"], scale=1, size="sm", variant="primary")
    
    file_status = gr.Markdown("", visible=True)
    
    gr.Examples(
        examples=[
            "What is a normal heart rate?",
            "How can I reduce stress naturally?",
            "Explain blood pressure readings",
            "What does high cholesterol mean?",
            "Tips for better sleep",
            "Analyze my blood test report",
            "What does this X-ray show?",
            "Explain my prescription medications"
        ],
        inputs=msg
    )
    
    file_upload.upload(handle_file_upload, inputs=[file_upload], outputs=[file_status])
    
    msg.submit(chat_response, [msg, chatbot], [msg, chatbot], queue=True)

if __name__ == "__main__":
    demo.launch()
