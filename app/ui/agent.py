from typing import List, Dict, Generator, Tuple
from llm import LLMClient

SYSTEM_PROMPT = """You are PixelCare AI, a health companion assistant. You help users understand their health vitals, 
provide wellness advice, and explain medical information in simple terms. Be empathetic, clear, and supportive."""

class HealthAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    def chat(self, message: str) -> Generator[Tuple[str, str], None, None]:
        """Returns (thinking, response) tuples"""
        self.history.append({"role": "user", "content": message})
        
        response = self.llm.chat(self.history, stream=True)
        full_response = ""
        thinking = ""
        answer = ""
        in_think_tag = False
        
        for chunk in response:
            if chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                
                # Handle reasoning field (native model thinking)
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    thinking += delta.reasoning
                    yield (thinking, answer)
                
                # Handle content with <think> tags
                if hasattr(delta, 'content') and delta.content:
                    content = delta.content
                    full_response += content
                    
                    # Parse <think> tags
                    if '<think>' in content:
                        in_think_tag = True
                        parts = content.split('<think>')
                        if parts[0]:
                            answer += parts[0]
                        if len(parts) > 1:
                            thinking += parts[1]
                        yield (thinking, answer)
                        continue
                    
                    if '</think>' in content:
                        in_think_tag = False
                        parts = content.split('</think>')
                        if parts[0]:
                            thinking += parts[0]
                        if len(parts) > 1:
                            answer += parts[1]
                        yield (thinking, answer)
                        continue
                    
                    # Regular content
                    if in_think_tag:
                        thinking += content
                    else:
                        answer += content
                    
                    yield (thinking, answer)
        
        self.history.append({"role": "assistant", "content": full_response})
    
    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
