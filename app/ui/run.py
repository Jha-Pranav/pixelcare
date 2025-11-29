#!/usr/bin/env -S uv run
"""Run PixelCare AI Gradio UI"""

from app import demo

if __name__ == "__main__":
    print("🏥 Starting PixelCare AI...")
    print("📍 Access at: http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
