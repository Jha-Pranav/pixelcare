#!/usr/bin/env python3
"""
PixelCare - AI Health Companion
Hugging Face Space Entry Point
"""
import sys
from pathlib import Path

# Add directories to path
root = Path(__file__).parent
sys.path.insert(0, str(root / "app" / "ui"))
sys.path.insert(0, str(root / "app" / "vitals"))

# Import and launch
from main import demo

if __name__ == "__main__":
    demo.launch()
