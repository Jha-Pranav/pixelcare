import gradio as gr
from agent import HealthAgent

agent = HealthAgent()

def chat_fn(message, history):
    """Chat function with collapsible colored thinking display"""
    thinking_text = ""
    answer_text = ""
    
    for thinking, answer in agent.chat(message):
        thinking_text = thinking
        answer_text = answer
        
        # Build response with collapsible colored thinking
        if thinking_text:
            thinking_display = f"""<details style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 15px; border-radius: 10px; margin-bottom: 15px; 
                                    border-left: 4px solid #764ba2;">
                <summary style="color: #fff; font-weight: bold; cursor: pointer; user-select: none;">
                    🤔 Thinking Process (click to expand)
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
    gr.Markdown("# 🏥 PixelCare AI Health Companion")
    gr.Markdown("Chat with your AI health assistant. Watch the AI think in real-time! 🧠")
    
    gr.ChatInterface(
        fn=chat_fn,
        examples=[
            "What is a normal heart rate?",
            "How can I improve my sleep?",
            "Explain blood pressure readings"
        ]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)
