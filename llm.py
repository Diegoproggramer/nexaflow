"""
LLM Connection Module.
Handles communication with language models (Groq, OpenAI, Ollama).
"""

import os
import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class Message:
    """A single message in a conversation."""
    role: str
    content: str


@dataclass
class LLMConfig:
    """Configuration for LLM connection."""
    provider: str = "groq"
    model: str = "llama-3.3-70b-versatile"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


class LLM:
    """Interface for communicating with language models."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        
        if self.config.api_key is None:
            self.config.api_key = os.environ.get("NEXAFLOW_API_KEY", "")
        
        self._urls = {
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "openai": "https://api.openai.com/v1/chat/completions",
            "ollama": "http://localhost:11434/v1/chat/completions",
        }
    
    def chat(self, messages: list) -> str:
        """Send messages and get a response."""
        import urllib.request
        
        url = self.config.base_url or self._urls.get(self.config.provider, "")
        
        data = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
            },
            method="POST",
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error connecting to model: {e}"
    
    def simple_ask(self, question: str, system_prompt: str = "") -> str:
        """Simplest way to ask a question."""
        messages = []
        if system_prompt:
            messages.append(Message("system", system_prompt))
        messages.append(Message("user", question))
        return self.chat(messages)
