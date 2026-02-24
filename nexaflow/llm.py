"""
LLM integration module for NexaFlow
Supports multiple LLM providers with a focus on free/local options
"""

import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class Message:
    """Represents a chat message"""
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    tool_calls: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict:
        data = {"role": self.role, "content": self.content}
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        return data

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str = "groq"  # groq, openai, local
    model: str = "mixtral-8x7b-32768"  # Free Groq model
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    base_url: Optional[str] = None

class LLM:
    """Unified interface for different LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the appropriate LLM client"""
        if self.config.provider == "groq":
            try:
                from groq import Groq
                self.client = Groq(api_key=self.config.api_key)
            except ImportError:
                print("Warning: groq not installed. Run: pip install groq")
                self.client = None
        elif self.config.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.base_url
                )
            except ImportError:
                print("Warning: openai not installed. Run: pip install openai")
                self.client = None
        else:
            # Fallback to mock for testing
            self.client = MockLLM()
    
    def chat(self, messages: List[Message], tools: Optional[List[Dict]] = None) -> Message:
        """Send chat request to LLM"""
        if not self.client:
            return Message(role="assistant", content="LLM client not initialized.")
        
        # Convert messages to dict format
        message_dicts = [msg.to_dict() for msg in messages]
        
        try:
            if self.config.provider in ["groq", "openai"]:
                kwargs = {
                    "model": self.config.model,
                    "messages": message_dicts,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                }
                
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"
                
                response = self.client.chat.completions.create(**kwargs)
                msg = response.choices[0].message
                
                tool_calls = None
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_calls = [
                        {
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                
                return Message(
                    role="assistant",
                    content=msg.content or "",
                    tool_calls=tool_calls
                )
            else:
                return self.client.chat(messages)
                
        except Exception as e:
            return Message(role="assistant", content=f"Error: {str(e)}")

class MockLLM:
    """Mock LLM for testing without API"""
    
    def chat(self, messages: List[Message]) -> Message:
        last_msg = messages[-1].content if messages else ""
        if "hello" in last_msg.lower():
            return Message(role="assistant", content="Hello! How can I help you?")
        return Message(role="assistant", content=f"Mock response to: {last_msg[:50]}...")
