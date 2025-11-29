from typing import List, Dict, Any, Optional
from openai import OpenAI
from .config import get_model_config
import base64

class LLMClient:
    def __init__(self, model: Optional[str] = None):
        config = get_model_config()
        self.model = model or config['name']
        self.client = OpenAI(
            base_url=config['url'],
            api_key=config['api_key']
        )
        self.temperature = config['temperature']
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def chat(self, messages: List[Dict], stream: bool = True, tools: Optional[List[Dict]] = None) -> Any:
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": stream
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        return self.client.chat.completions.create(**params)
