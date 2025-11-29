import os
import toml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ModelConfig:
    name: str = "qwen3:4b"
    url: str = "http://localhost:11434/v1"
    api_key: str = "ollama"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path(__file__).parent / "config.toml")
        self.config = self._load_config()
    
    def _load_config(self) -> ModelConfig:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = toml.load(f)
                return ModelConfig(**data.get('model', {}))
        return ModelConfig()
    
    def get_model_config(self) -> Dict[str, Any]:
        return {
            'name': self.config.name,
            'url': self.config.url,
            'api_key': self.config.api_key,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens
        }

_config_manager = None

def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_model_config() -> Dict[str, Any]:
    return get_config_manager().get_model_config()
