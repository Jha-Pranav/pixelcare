#!/usr/bin/env python3
"""PixelCare - Cloud Demo (Chat + Document Analysis)"""
import gradio as gr
import sys
from pathlib import Path

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

def submit_and_clear(message, chat_history):
    """Submit message and clear input"""
    global uploaded_docs
    
    if chat_history is None:
        chat_history = []
    
    # If documents uploaded, use vision
    if uploaded_docs:
        content = [{"type": "text", "text": message}]
        for doc in uploaded_docs:
            content.extend(doc['content'])
        
        for thinking, answer in health_agent.chat_with_vision(content):
            if thinking:
                response = f"""
<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #764ba2;">
    <summary style="color: #fff; font-weight: bold; cursor: pointer;">🤔 Analyzing Document (click to expand)</summary>
    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking}</div>
</details>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745;">
    <div style="color: #28a745; font-weight: bold; margin-bottom: 8px;">📄 Document Analysis</div>
    <div style="color: #333;">{answer}</div>
</div>
"""
            else:
                response = answer
            
            yield "", chat_history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]
        return
    
    # Regular chat
    for thinking, answer in health_agent.chat(message):
        if thinking:
            response = f"""
<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #764ba2;">
    <summary style="color: #fff; font-weight: bold; cursor: pointer;">🤔 Thinking (click to expand)</summary>
    <div style="color: #f0f0f0; font-family: monospace; white-space: pre-wrap; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3);">{thinking}</div>
</details>
<div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745;">
    <div style="color: #28a745; font-weight: bold; margin-bottom: 8px;">💬 Answer</div>
    <div style="color: #333;">{answer}</div>
</div>
"""
        else:
            response = answer
        
        yield "", chat_history + [{"role": "assistant", "content": response}]

with gr.Blocks(title="PixelCare AI") as demo:
    gr.Markdown("# 🏥 PixelCare - AI Health Companion")
    gr.Markdown("""
    **🤖 Agentic AI** - I can analyze medical documents and answer health questions.
    
    💡 **Try:** Upload blood test/X-ray • "What does this mean?" • "Explain my results"
    
    ⚠️ **Note:** Camera vitals require [local installation](https://github.com/Jha-Pranav/pixelcare)
    """)
    
    chatbot = gr.Chatbot(label="Chat", height=650)
    
    msg = gr.Textbox(
        label="Message", 
        placeholder="Ask about your health or upload medical documents..."
    )
    
    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary", scale=1)
        file_upload = gr.UploadButton("Upload", file_count="multiple", file_types=[".pdf", ".jpg", ".jpeg", ".png", ".webp"], scale=1, size="sm", variant="secondary")
    
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
    
    msg.submit(submit_and_clear, [msg, chatbot], [msg, chatbot], queue=True)
    submit_btn.click(submit_and_clear, [msg, chatbot], [msg, chatbot], queue=True)

if __name__ == "__main__":
    demo.launch()
