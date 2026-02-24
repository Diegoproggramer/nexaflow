"""
Tool System for Agents.
Tools give agents the ability to interact with the world.
"""

import json
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """
    A tool that an agent can use.
    
    Example:
        tool = Tool(
            name="calculator",
            description="Solves math expressions",
            function=lambda expression: str(eval(expression))
        )
    """
    name: str
    description: str
    function: Callable
    parameters: dict = None
    
    def run(self, **kwargs) -> str:
        """Execute the tool."""
        try:
            result = self.function(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error in tool {self.name}: {e}"


class ToolRegistry:
    """Registry that holds all available tools."""
    
    def __init__(self):
        self._tools: dict = {}
    
    def register(self, tool: Tool) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list:
        """List all registered tools."""
        return list(self._tools.values())
    
    def get_tools_description(self) -> str:
        """Get description of all tools for the LLM."""
        descriptions = []
        for tool in self._tools.values():
            desc = f"- {tool.name}: {tool.description}"
            if tool.parameters:
                params = json.dumps(tool.parameters, ensure_ascii=False)
                desc += f"\n  Parameters: {params}"
            descriptions.append(desc)
        return "\n".join(descriptions)


# ===== Built-in Tools =====

def _calculator(expression: str = "0") -> str:
    """Safe calculator."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Only math operations are allowed"
    return str(eval(expression))


def _read_file(filepath: str = "") -> str:
    """Read a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"File {filepath} not found"


def _write_file(filepath: str = "", content: str = "") -> str:
    """Write to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File {filepath} saved successfully"


def _web_search(query: str = "") -> str:
    """Simple web search using DuckDuckGo."""
    import urllib.request
    import urllib.parse
    
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NexaFlow/0.1"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = []
            if data.get("Abstract"):
                results.append(data["Abstract"])
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(topic["Text"])
            return "\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Search error: {e}"


BUILTIN_TOOLS = [
    Tool(
        name="calculator",
        description="Calculator - solves math expressions like '2+2' or '100*5.5'",
        function=lambda expression="0": _calculator(expression),
        parameters={"expression": "math expression"},
    ),
    Tool(
        name="read_file",
        description="Reads the content of a file",
        function=lambda filepath="": _read_file(filepath),
        parameters={"filepath": "path to file"},
    ),
    Tool(
        name="write_file",
        description="Writes content to a file",
        function=lambda filepath="", content="": _write_file(filepath, content),
        parameters={"filepath": "path to file", "content": "content to write"},
    ),
    Tool(
        name="web_search",
        description="Searches the internet and returns results",
        function=lambda query="": _web_search(query),
        parameters={"query": "search query"},
    ),
]
