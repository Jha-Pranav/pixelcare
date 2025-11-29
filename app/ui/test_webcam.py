#!/usr/bin/env -S uv run
import gradio as gr

def test_webcam(image):
    if image is None:
        return "No image captured"
    return f"Image captured! Shape: {image.shape}"

with gr.Blocks() as demo:
    gr.Markdown("# Webcam Test")
    
    img = gr.Image(sources=["webcam"], label="Webcam", type="numpy")
    output = gr.Textbox(label="Result")
    btn = gr.Button("Test")
    
    btn.click(test_webcam, inputs=[img], outputs=[output])

demo.launch(debug=True)
