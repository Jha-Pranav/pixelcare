"""
PixelCare - Hugging Face Space Entry Point
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and launch the main UI
from app.ui.main import demo

if __name__ == "__main__":
    demo.launch()
