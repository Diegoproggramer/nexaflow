"""
Memory system for NexaFlow agents
Provides short-term and long-term memory with persistence
"""

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class MemoryItem:
    """Single memory entry"""
    content: str
    memory_type: str  # 'conversation', 'fact', 'task', 'learning'
    timestamp: str = ""
    importance: float = 0.5  # 0.0 to 1.0
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []


class ShortTermMemory:
    """
    Short-term memory - keeps recent conversation context
    Like human working memory, limited capacity
    """
    
    def __init__(self, max_items: int = 20):
        self.max_items = max_items
        self.items: List[MemoryItem] = []
    
    def add(self, content: str, memory_type: str = "conversation", 
            importance: float = 0.5, tags: List[str] = None):
        """Add item to short-term memory"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance,
            tags=tags or []
        )
        self.items.append(item)
        
        # Remove oldest low-importance items if over capacity
        if len(self.items) > self.max_items:
            self.items.sort(key=lambda x: x.importance)
            self.items = self.items[1:]  # Remove least important
    
    def get_recent(self, count: int = 5) -> List[MemoryItem]:
        """Get most recent memories"""
        return self.items[-count:]
    
    def get_by_type(self, memory_type: str) -> List[MemoryItem]:
        """Get memories by type"""
        return [item for item in self.items if item.memory_type == memory_type]
    
    def search(self, keyword: str) -> List[MemoryItem]:
        """Simple keyword search in memories"""
        keyword_lower = keyword.lower()
        return [
            item for item in self.items 
            if keyword_lower in item.content.lower()
        ]
    
    def clear(self):
        """Clear all short-term memory"""
        self.items = []
    
    def to_context_string(self, max_items: int = 10) -> str:
        """Convert recent memories to a context string for LLM"""
        recent = self.get_recent(max_items)
        if not recent:
            return "No previous context."
        
        lines = ["Previous context:"]
        for item in recent:
            lines.append(f"  [{item.memory_type}] {item.content}")
        return "\n".join(lines)


class LongTermMemory:
    """
    Long-term memory with file-based persistence
    Stores important facts, learnings, and user preferences
    """
    
    def __init__(self, storage_path: str = "memory_store"):
        self.storage_path = storage_path
        self.memories: Dict[str, List[MemoryItem]] = {
            "facts": [],
            "learnings": [],
            "preferences": [],
            "tasks": []
        }
        self._load()
    
    def add(self, content: str, category: str = "facts", 
            importance: float = 0.5, tags: List[str] = None):
        """Add item to long-term memory"""
        if category not in self.memories:
            self.memories[category] = []
        
        item = MemoryItem(
            content=content,
            memory_type=category,
            importance=importance,
            tags=tags or []
        )
        
        # Avoid duplicates
        existing_contents = [m.content for m in self.memories[category]]
        if content not in existing_contents:
            self.memories[category].append(item)
            self._save()
    
    def get_category(self, category: str) -> List[MemoryItem]:
        """Get all memories in a category"""
        return self.memories.get(category, [])
    
    def search(self, keyword: str) -> List[MemoryItem]:
        """Search across all categories"""
        keyword_lower = keyword.lower()
        results = []
        for category_items in self.memories.values():
            for item in category_items:
                if keyword_lower in item.content.lower():
                    results.append(item)
        return results
    
    def get_important(self, min_importance: float = 0.7) -> List[MemoryItem]:
        """Get high-importance memories"""
        results = []
        for category_items in self.memories.values():
            for item in category_items:
                if item.importance >= min_importance:
                    results.append(item)
        return sorted(results, key=lambda x: x.importance, reverse=True)
    
    def _save(self):
        """Save memories to file"""
        os.makedirs(self.storage_path, exist_ok=True)
        filepath = os.path.join(self.storage_path, "long_term.json")
        
        data = {}
        for category, items in self.memories.items():
            data[category] = [asdict(item) for item in items]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """Load memories from file"""
        filepath = os.path.join(self.storage_path, "long_term.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for category, items in data.items():
                    self.memories[category] = [
                        MemoryItem(**item) for item in items
                    ]
            except (json.JSONDecodeError, TypeError):
                pass  # Start fresh if file is corrupted
    
    def clear_category(self, category: str):
        """Clear a specific category"""
        if category in self.memories:
            self.memories[category] = []
            self._save()


class MemoryManager:
    """
    Unified memory manager combining short-term and long-term memory
    """
    
    def __init__(self, storage_path: str = "memory_store"):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage_path)
    
    def remember(self, content: str, importance: float = 0.5, 
                 tags: List[str] = None):
        """Smart memory - stores in appropriate location based on importance"""
        # Always add to short-term
        self.short_term.add(content, importance=importance, tags=tags)
        
        # High importance items also go to long-term
        if importance >= 0.7:
            self.long_term.add(
                content, 
                category="facts",
                importance=importance, 
                tags=tags
            )
    
    def recall(self, query: str, max_results: int = 5) -> List[MemoryItem]:
        """Search both memory systems"""
        short_results = self.short_term.search(query)
        long_results = self.long_term.search(query)
        
        # Combine and deduplicate
        all_results = short_results + long_results
        seen = set()
        unique = []
        for item in all_results:
            if item.content not in seen:
                seen.add(item.content)
                unique.append(item)
        
        # Sort by importance
        unique.sort(key=lambda x: x.importance, reverse=True)
        return unique[:max_results]
    
    def get_context(self) -> str:
        """Get formatted context string for LLM prompts"""
        return self.short_term.to_context_string()

