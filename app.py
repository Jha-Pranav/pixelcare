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

def clear_documents():
    """Clear uploaded documents"""
    global uploaded_docs
    uploaded_docs = []
    return "Documents cleared"

def chat_fn(message, history):
    """Chat with document support"""
    global uploaded_docs
    
    if not message:
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
    
    ⚠️ **Cloud Limitation:** Camera vitals not working in HuggingFace (working on fix). All features work locally!
    
    ✅ **Working:** Document analysis, health Q&A | 📥 **Full features:** [Run locally](https://github.com/Jha-Pranav/pixelcare)
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
