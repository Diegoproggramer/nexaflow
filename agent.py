"""
Core Agent Module - The heart of NexaFlow.
An Agent that can think, use tools, and respond intelligently.
"""

import json
from typing import Optional
from nexaflow.llm import LLM, LLMConfig, Message
from nexaflow.memory import Memory
from nexaflow.tools import Tool, ToolRegistry, BUILTIN_TOOLS


class Agent:
    """
    An intelligent AI Agent.
    
    Example:
        agent = Agent(name="Assistant")
        answer = agent.run("What is 2+2? Use the calculator.")
        print(answer)
    """
    
    def __init__(
        self,
        name: str = "NexaAgent",
        role: str = "A helpful and intelligent assistant",
        llm_config: Optional[LLMConfig] = None,
        tools: Optional[list] = None,
        use_builtin_tools: bool = True,
        max_steps: int = 10,
        verbose: bool = True,
    ):
        self.name = name
        self.role = role
        self.verbose = verbose
        self.max_steps = max_steps
        
        self.llm = LLM(llm_config)
        self.memory = Memory()
        self.tool_registry = ToolRegistry()
        
        if use_builtin_tools:
            for tool in BUILTIN_TOOLS:
                self.tool_registry.register(tool)
        
        if tools:
            for tool in tools:
                self.tool_registry.register(tool)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        tools_desc = self.tool_registry.get_tools_description()
        memory_context = self.memory.get_context()
        
        prompt = f"""You are an AI Agent named "{self.name}".
Your role: {self.role}

You have access to these tools:
{tools_desc}

To use a tool, respond with EXACTLY this JSON format:
{{"action": "tool", "tool_name": "tool_name_here", "parameters": {{"param1": "value1"}}}}

When you have the final answer:
{{"action": "answer", "content": "your final answer here"}}

When you need to think:
{{"action": "think", "content": "your thought process"}}

Rules:
1. Always respond with valid JSON
2. Think before answering
3. If you don't know, say so honestly
4. Use tools when they can help
"""
        
        if memory_context:
            prompt += f"\n\nMemory context:\n{memory_context}"
        
        return prompt
    
    def _parse_response(self, response: str) -> dict:
        """Parse LLM response into a structured dict."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        try:
            start = response.index("{")
            end = response.rindex("}") + 1
            return json.loads(response[start:end])
        except (ValueError, json.JSONDecodeError):
            pass
        
        return {"action": "answer", "content": response}
    
    def _log(self, emoji: str, message: str) -> None:
        """Print log message if verbose mode is on."""
        if self.verbose:
            print(f"  {emoji} {message}")
    
    def run(self, task: str) -> str:
        """
        Run the agent on a task.
        The agent will think, use tools, and return an answer.
        """
        self._log("🎯", f"Task: {task}")
        self._log("🤖", f"Agent '{self.name}' started...")
        
        messages = [
            Message("system", self._build_system_prompt()),
            Message("user", task),
        ]
        
        self.memory.remember(f"Task: {task}", category="task", importance=0.8)
        
        for step in range(self.max_steps):
            self._log("💭", f"Step {step + 1}/{self.max_steps}...")
            
            response = self.llm.chat(messages)
            parsed = self._parse_response(response)
            action = parsed.get("action", "answer")
            
            if action == "think":
                thought = parsed.get("content", "")
                self._log("🧠", f"Thinking: {thought}")
                messages.append(Message("assistant", response))
                messages.append(Message("user", "Good, continue."))
            
            elif action == "tool":
                tool_name = parsed.get("tool_name", "")
                params = parsed.get("parameters", {})
                
                self._log("🔧", f"Tool: {tool_name}({params})")
                
                tool = self.tool_registry.get(tool_name)
                if tool:
                    result = tool.run(**params)
                    self._log("📋", f"Result: {result[:200]}")
                    
                    messages.append(Message("assistant", response))
                    messages.append(Message("user",
                        f"Tool {tool_name} result: {result}\n"
                        f"Now continue based on this result."
                    ))
                    
                    self.memory.remember(
                        f"Tool {tool_name}: {result[:500]}",
                        category="tool_result"
                    )
                else:
                    messages.append(Message("assistant", response))
                    messages.append(Message("user",
                        f"Tool '{tool_name}' not found. Available: "
                        f"{[t.name for t in self.tool_registry.list_tools()]}"
                    ))
            
            elif action == "answer":
                answer = parsed.get("content", response)
                self._log("✅", f"Answer: {answer[:200]}")
                
                self.memory.remember(
                    f"Answer: {answer[:500]}",
                    category="answer",
                    importance=0.7
                )
                
                return answer
        
        return "Sorry, I couldn't reach an answer. Please try a simpler question."
    
    def chat(self, message: str) -> str:
        """Simple chat without tools."""
        return self.llm.simple_ask(message,
            system_prompt=f"You are {self.name}. {self.role}.")
