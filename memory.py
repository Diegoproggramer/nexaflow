"""
Memory System for Agents.
Provides short-term, long-term, and working memory.
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemoryItem:
    """A single memory entry."""
    content: str
    category: str = "general"
    importance: float = 0.5
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )


class Memory:
    """
    Agent memory system with three types:
    - short_term: current conversation (like RAM)
    - long_term: important facts to remember (like hard drive)
    - working: what the agent is currently working on
    """
    
    def __init__(self, max_short_term: int = 50):
        self.short_term: list = []
        self.long_term: list = []
        self.working: list = []
        self.max_short_term = max_short_term
    
    def remember(self, content: str, category: str = "general",
                 importance: float = 0.5) -> None:
        """Store something in memory."""
        item = MemoryItem(
            content=content,
            category=category,
            importance=importance,
        )
        
        if importance >= 0.7:
            self.long_term.append(item)
        else:
            self.short_term.append(item)
            if len(self.short_term) > self.max_short_term:
                self.short_term.pop(0)
    
    def recall(self, query: str, limit: int = 5) -> list:
        """Search memory for relevant items."""
        results = []
        
        for item in self.long_term:
            if query.lower() in item.content.lower():
                results.append(item)
        
        for item in self.short_term:
            if query.lower() in item.content.lower():
                results.append(item)
        
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    def get_context(self) -> str:
        """Get memory summary for the LLM."""
        context_parts = []
        
        if self.long_term:
            context_parts.append("=== Important Information ===")
            for item in self.long_term[-10:]:
                context_parts.append(f"- {item.content}")
        
        if self.working:
            context_parts.append("\n=== Current Task ===")
            for item in self.working:
                context_parts.append(f"- {item.content}")
        
        if self.short_term:
            context_parts.append("\n=== Recent Conversation ===")
            for item in self.short_term[-5:]:
                context_parts.append(f"- {item.content}")
        
        return "\n".join(context_parts)
    
    def save_to_file(self, filepath: str) -> None:
        """Save memory to a JSON file."""
        data = {
            "short_term": [
                {"content": m.content, "category": m.category,
                 "importance": m.importance, "timestamp": m.timestamp}
                for m in self.short_term
            ],
            "long_term": [
                {"content": m.content, "category": m.category,
                 "importance": m.importance, "timestamp": m.timestamp}
                for m in self.long_term
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str) -> None:
        """Load memory from a JSON file."""
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item_data in data.get("short_term", []):
            self.short_term.append(MemoryItem(**item_data))
        for item_data in data.get("long_term", []):
            self.long_term.append(MemoryItem(**item_data))
    
    def clear(self) -> None:
        """Clear all memory."""
        self.short_term.clear()
        self.long_term.clear()
        self.working.clear()
