"""
Tool system for NexaFlow agents
Agents can use these tools to interact with the real world
"""

import json
import math
import os
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ToolResult:
    """Result from a tool execution"""
    success: bool
    output: str
    error: Optional[str] = None


@dataclass
class Tool:
    """Represents a tool that an agent can use"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None
    
    def to_openai_format(self) -> Dict:
        """Convert to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments"""
        if self.function is None:
            return ToolResult(
                success=False, 
                output="", 
                error="No function attached to tool"
            )
        try:
            result = self.function(**kwargs)
            return ToolResult(success=True, output=str(result))
        except Exception as e:
            return ToolResult(
                success=False, 
                output="", 
                error=str(e)
            )


# ============================================================
# Built-in Tools
# ============================================================

def calculator(expression: str) -> str:
    """Safe mathematical calculator"""
    allowed_names = {
        "abs": abs, "round": round,
        "min": min, "max": max,
        "sum": sum, "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin, "cos": math.cos,
        "tan": math.tan, "pi": math.pi,
        "e": math.e, "log": math.log,
        "log10": math.log10,
    }
    
    try:
        # Safety: only allow math operations
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                return f"Error: '{name}' is not allowed"
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def read_file(filepath: str) -> str:
    """Read content from a file"""
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' not found"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Limit output size
        if len(content) > 5000:
            content = content[:5000] + "\n... (truncated)"
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """Write content to a file"""
    try:
        # Create directories if needed
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def get_datetime() -> str:
    """Get current date and time"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def web_search(query: str) -> str:
    """
    Simulated web search
    In production, connect to real search API
    """
    return (
        f"Search results for '{query}':\n"
        f"Note: Web search requires API setup.\n"
        f"Supported APIs: Google, DuckDuckGo, Searx\n"
        f"Run: pip install duckduckgo-search"
    )


def list_directory(path: str = ".") -> str:
    """List files and folders in a directory"""
    try:
        items = os.listdir(path)
        if not items:
            return f"Directory '{path}' is empty"
        
        files = []
        dirs = []
        for item in sorted(items):
            full = os.path.join(path, item)
            if os.path.isdir(full):
                dirs.append(f"  [DIR]  {item}/")
            else:
                size = os.path.getsize(full)
                files.append(f"  [FILE] {item} ({size} bytes)")
        
        result = f"Contents of '{path}':\n"
        result += "\n".join(dirs + files)
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def text_analysis(text: str) -> str:
    """Analyze text - word count, char count, etc."""
    words = text.split()
    lines = text.split('\n')
    chars = len(text)
    
    return (
        f"Text Analysis:\n"
        f"  Characters: {chars}\n"
        f"  Words: {len(words)}\n"
        f"  Lines: {len(lines)}\n"
        f"  Avg word length: {sum(len(w) for w in words) / max(len(words), 1):.1f}"
    )


# ============================================================
# Tool Registry
# ============================================================

class ToolRegistry:
    """Manages available tools for agents"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtins()
    
    def _register_builtins(self):
        """Register all built-in tools"""
        
        self.register(Tool(
            name="calculator",
            description="Calculate mathematical expressions. Supports +, -, *, /, sqrt, sin, cos, etc.",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate, e.g., '2 + 2' or 'sqrt(16)'"
                    }
                },
                "required": ["expression"]
            },
            function=calculator
        ))
        
        self.register(Tool(
            name="read_file",
            description="Read the contents of a file",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["filepath"]
            },
            function=read_file
        ))
        
        self.register(Tool(
            name="write_file",
            description="Write content to a file",
            parameters={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["filepath", "content"]
            },
            function=write_file
        ))
        
        self.register(Tool(
            name="get_datetime",
            description="Get current date and time",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            function=get_datetime
        ))
        
        self.register(Tool(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            },
            function=web_search
        ))
        
        self.register(Tool(
            name="list_directory",
            description="List files and folders in a directory",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list"
                    }
                },
                "required": []
            },
            function=list_directory
        ))
        
        self.register(Tool(
            name="text_analysis",
            description="Analyze text - count words, characters, lines",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze"
                    }
                },
                "required": ["text"]
            },
            function=text_analysis
        ))
    
    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False, 
                output="", 
                error=f"Tool '{name}' not found"
            )
        return tool.execute(**kwargs)
    
    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys())
    
    def to_openai_format(self) -> List[Dict]:
        """Convert all tools to OpenAI format for LLM"""
        return [tool.to_openai_format() for tool in self.tools.values()]
    
    def get_tools_description(self) -> str:
        """Get human-readable description of all tools"""
        lines = ["Available Tools:"]
        for name, tool in self.tools.items():
            lines.append(f"  - {name}: {tool.description}")
        return "\n".join(lines)
