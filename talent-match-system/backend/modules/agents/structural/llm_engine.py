from utils.qwen_client import get_qwen_client
import json
from typing import Dict, Any, Optional, List

class LLMEngine:
    """核心LLM引擎 - Structural层核心组件"""
    
    def __init__(self):
        self.client = get_qwen_client()
        self.max_tokens = 4096
        self.temperature = 0.3
    
    def generate