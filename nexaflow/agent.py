"""
NexaFlow Agent Core
The brain of the system - implements ReAct (Reasoning + Acting) pattern
"""

import json
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .llm import LLMClient
from .memory import MemoryManager, MemoryItem
from .tools import ToolRegistry, ToolResult


@dataclass
class AgentStep:
    """One step in agent's reasoning chain"""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict] = None
    observation: Optional[str] = None
    is_final: bool = False
    final_answer: Optional[str] = None


class Agent:
    """
    NexaFlow AI Agent
    Uses ReAct pattern: Think -> Act -> Observe -> Repeat
    
    This is where the magic happens!
    """
    
    def __init__(
        self,
        name: str = "NexaAgent",
        role: str = "A helpful AI assistant",
        llm: Optional[LLMClient] = None,
        tools: Optional[ToolRegistry] = None,
        memory: Optional[MemoryManager] = None,
        max_steps: int = 10,
        verbose: bool = True
    ):
        self.name = name
        self.role = role
        self.llm = llm or LLMClient()
        self.tools = tools or ToolRegistry()
        self.memory = memory or MemoryManager()
        self.max_steps = max_steps
        self.verbose = verbose
        self.history: List[AgentStep] = []
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with tools info"""
        tools_desc = self.tools.get_tools_description()
        
        return f"""You are {self.name}, {self.role}.

You operate using the ReAct pattern (Reasoning and Acting).

{tools_desc}

## How to respond:

For EACH step, you MUST use this EXACT format:

THOUGHT: [Your reasoning about what to do next]
ACTION: [tool_name]
ACTION_INPUT: {{"param": "value"}}

After getting results, continue thinking:

THOUGHT: [Your reasoning about the observation]
ACTION: [next_tool or FINISH]
ACTION_INPUT: {{"param": "value"}}

When you have the final answer, use:

THOUGHT: [Your final reasoning]
ACTION: FINISH
ACTION_INPUT: {{"answer": "Your complete final answer here"}}

## Rules:
1. ALWAYS start with THOUGHT
2. Use tools when you need real data
3. You can use multiple tools in sequence
4. ALWAYS end with ACTION: FINISH
5. Be thorough but efficient
6. If a tool fails, try a different approach
"""
    
    def _build_user_prompt(self, task: str) -> str:
        """Build user prompt with context"""
        context = self.memory.get_context()
        
        prompt = f"""Task: {task}

{context}

Begin your reasoning. Remember: THOUGHT -> ACTION -> observe result -> repeat until done."""
        
        return prompt
    
    def _parse_response(self, response: str, step_num: int) -> AgentStep:
        """Parse LLM response into structured step"""
        step = AgentStep(step_number=step_num, thought="")
        
        # Extract THOUGHT
        thought_match = re.search(
            r'THOUGHT:\s*(.+?)(?=ACTION:|$)', 
            response, 
            re.DOTALL | re.IGNORECASE
        )
        if thought_match:
            step.thought = thought_match.group(1).strip()
        
        # Extract ACTION
        action_match = re.search(
            r'ACTION:\s*(\w+)', 
            response, 
            re.IGNORECASE
        )
        if action_match:
            step.action = action_match.group(1).strip()
        
        # Extract ACTION_INPUT
        input_match = re.search(
            r'ACTION_INPUT:\s*(\{.*?\})', 
            response, 
            re.DOTALL | re.IGNORECASE
        )
        if input_match:
            try:
                step.action_input = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                step.action_input = {"raw": input_match.group(1)}
        
        # Check if this is the final step
        if step.action and step.action.upper() == "FINISH":
            step.is_final = True
            if step.action_input and "answer" in step.action_input:
                step.final_answer = step.action_input["answer"]
            else:
                step.final_answer = step.thought
        
        return step
    
    def _execute_action(self, step: AgentStep) -> str:
        """Execute the action from a step"""
        if not step.action or step.is_final:
            return ""
        
        tool_name = step.action.lower()
        params = step.action_input or {}
        
        result = self.tools.execute(tool_name, **params)
        
        if result.success:
            return f"Result: {result.output}"
        else:
            return f"Error: {result.error}"
    
    def _log(self, message: str):
        """Print if verbose mode is on"""
        if self.verbose:
            print(message)
    
    def run(self, task: str) -> str:
        """
        Run the agent on a task
        
        This is the main loop:
        1. Think about the task
        2. Choose an action
        3. Execute it
        4. Observe the result
        5. Repeat until done
        """
        self._log(f"\n{'='*60}")
        self._log(f"  Agent: {self.name}")
        self._log(f"  Task: {task}")
        self._log(f"{'='*60}\n")
        
        # Store task in memory
        self.memory.remember(f"Task: {task}", importance=0.8)
        
        # Build initial messages
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": self._build_user_prompt(task)}
        ]
        
        self.history = []
        
        for step_num in range(1, self.max_steps + 1):
            self._log(f"--- Step {step_num} ---")
            
            # Get LLM response
            response = self.llm.chat(messages)
            
            if not response:
                self._log("  [ERROR] No response from LLM")
                break
            
            # Parse response
            step = self._parse_response(response, step_num)
            self.history.append(step)
            
            self._log(f"  Thought: {step.thought[:100]}...")
            
            # If final answer, we're done
            if step.is_final:
                self._log(f"\n  ✅ Final Answer: {step.final_answer[:200]}")
                
                # Store result in memory
                self.memory.remember(
                    f"Completed: {task} -> {step.final_answer}",
                    importance=0.9
                )
                
                return step.final_answer or step.thought
            
            # Execute action
            if step.action:
                self._log(f"  Action: {step.action}")
                observation = self._execute_action(step)
                step.observation = observation
                self._log(f"  Observation: {observation[:100]}...")
                
                # Add to conversation for next iteration
                messages.append({
                    "role": "assistant", 
                    "content": response
                })
                messages.append({
                    "role": "user", 
                    "content": f"OBSERVATION: {observation}\n\nContinue your reasoning."
                })
            else:
                # No action found, ask LLM to try again
                messages.append({
                    "role": "assistant", 
                    "content": response
                })
                messages.append({
                    "role": "user", 
                    "content": "Please follow the format: THOUGHT, ACTION, ACTION_INPUT"
                })
        
        # Max steps reached
        self._log(f"\n  ⚠️  Max steps ({self.max_steps}) reached")
        
        if self.history:
            last = self.history[-1]
            return last.final_answer or last.thought or "Could not complete the task"
        
        return "No result"
    
    def chat(self, message: str) -> str:
        """
        Simple chat mode - no tools, just conversation
        """
        self.memory.short_term.add(
            f"User: {message}", 
            memory_type="conversation"
        )
        
        context = self.memory.get_context()
        
        messages = [
            {
                "role": "system", 
                "content": f"You are {self.name}, {self.role}.\n{context}"
            },
            {"role": "user", "content": message}
        ]
        
        response = self.llm.chat(messages)
        
        if response:
            self.memory.short_term.add(
                f"Assistant: {response}",
                memory_type="conversation"
            )
        
        return response or "I couldn't generate a response."
    
    def get_history(self) -> List[Dict]:
        """Get execution history as list of dicts"""
        history = []
        for step in self.history:
            history.append({
                "step": step.step_number,
                "thought": step.thought,
                "action": step.action,
                "input": step.action_input,
                "observation": step.observation,
                "is_final": step.is_final,
                "answer": step.final_answer
            })
        return history
    
    def reset(self):
        """Reset agent state"""
        self.history = []
        self.memory.short_term.clear()
    
    def __repr__(self):
        return f"Agent(name='{self.name}', tools={self.tools.list_tools()})"
