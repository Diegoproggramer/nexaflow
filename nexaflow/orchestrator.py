"""
NexaFlow Orchestrator
Manages multiple agents working together on complex tasks
Like a conductor leading an orchestra of AI agents
"""

import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .agent import Agent
from .llm import LLMClient
from .tools import ToolRegistry
from .memory import MemoryManager


class TaskStatus(Enum):
    """Status of a task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """A task to be executed by an agent"""
    id: str
    description: str
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "agent": self.assigned_agent,
            "status": self.status.value,
            "result": self.result,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }


@dataclass
class WorkflowResult:
    """Result of a complete workflow"""
    success: bool
    tasks_completed: int
    tasks_failed: int
    total_tasks: int
    results: Dict[str, str]
    summary: str
    duration_seconds: float = 0.0


class Orchestrator:
    """
    Manages multi-agent workflows
    
    Patterns supported:
    1. Sequential - agents work one after another
    2. Parallel - agents work independently
    3. Pipeline - output of one feeds into next
    4. Hierarchical - manager agent delegates to workers
    """
    
    def __init__(self, verbose: bool = True):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.verbose = verbose
        self.shared_memory = MemoryManager()
        self.workflow_history: List[WorkflowResult] = []
    
    def _log(self, message: str):
        """Print if verbose"""
        if self.verbose:
            print(message)
    
    # ========================================================
    # Agent Management
    # ========================================================
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the orchestra"""
        self.agents[agent.name] = agent
        self._log(f"  ✅ Agent '{agent.name}' added")
    
    def create_agent(
        self,
        name: str,
        role: str,
        llm: Optional[LLMClient] = None,
        tools: Optional[ToolRegistry] = None
    ) -> Agent:
        """Create and register a new agent"""
        agent = Agent(
            name=name,
            role=role,
            llm=llm or LLMClient(),
            tools=tools or ToolRegistry(),
            memory=MemoryManager()
        )
        self.add_agent(agent)
        return agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())
    
    def remove_agent(self, name: str) -> bool:
        """Remove an agent"""
        if name in self.agents:
            del self.agents[name]
            return True
        return False
    
    # ========================================================
    # Task Management
    # ========================================================
    
    def add_task(
        self,
        task_id: str,
        description: str,
        agent_name: Optional[str] = None,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """Add a task to the workflow"""
        task = Task(
            id=task_id,
            description=description,
            assigned_agent=agent_name,
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        return task
    
    def _can_run_task(self, task: Task) -> bool:
        """Check if all dependencies are completed"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _get_dependency_context(self, task: Task) -> str:
        """Get results from dependency tasks"""
        if not task.dependencies:
            return ""
        
        context_parts = ["Previous results:"]
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task and dep_task.result:
                context_parts.append(
                    f"- [{dep_id}]: {dep_task.result[:500]}"
                )
        
        return "\n".join(context_parts)
    
    def _run_task(self, task: Task) -> bool:
        """Execute a single task"""
        agent_name = task.assigned_agent
        
        if not agent_name or agent_name not in self.agents:
            # Use first available agent
            if self.agents:
                agent_name = list(self.agents.keys())[0]
            else:
                task.status = TaskStatus.FAILED
                task.result = "No agents available"
                return False
        
        agent = self.agents[agent_name]
        task.status = TaskStatus.RUNNING
        task.assigned_agent = agent_name
        
        self._log(f"\n  🔄 Running task '{task.id}' with agent '{agent_name}'")
        
        try:
            # Build task with dependency context
            dep_context = self._get_dependency_context(task)
            full_task = task.description
            if dep_context:
                full_task = f"{task.description}\n\n{dep_context}"
            
            # Execute
            result = agent.run(full_task)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now().isoformat()
            
            # Store in shared memory
            self.shared_memory.remember(
                f"Task '{task.id}' completed: {result[:200]}",
                importance=0.8
            )
            
            self._log(f"  ✅ Task '{task.id}' completed")
            return True
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = f"Error: {str(e)}"
            self._log(f"  ❌ Task '{task.id}' failed: {str(e)}")
            return False
    
    # ========================================================
    # Workflow Patterns
    # ========================================================
    
    def run_sequential(self, tasks: Optional[List[str]] = None) -> WorkflowResult:
        """
        Run tasks one after another
        Each task can use results from previous tasks
        """
        start_time = datetime.now()
        
        self._log(f"\n{'='*60}")
        self._log(f"  🎼 Sequential Workflow Starting")
        self._log(f"  Agents: {self.list_agents()}")
        self._log(f"{'='*60}")
        
        task_ids = tasks or list(self.tasks.keys())
        completed = 0
        failed = 0
        results = {}
        
        for task_id in task_ids:
            task = self.tasks.get(task_id)
            if not task:
                self._log(f"  ⚠️  Task '{task_id}' not found")
                failed += 1
                continue
            
            # Check dependencies
            if not self._can_run_task(task):
                self._log(f"  ⏳ Task '{task_id}' waiting for dependencies")
                task.status = TaskStatus.FAILED
                task.result = "Dependencies not met"
                failed += 1
                continue
            
            if self._run_task(task):
                completed += 1
                results[task_id] = task.result or ""
            else:
                failed += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Generate summary
        summary = self._generate_summary(results)
        
        workflow_result = WorkflowResult(
            success=failed == 0,
            tasks_completed=completed,
            tasks_failed=failed,
            total_tasks=len(task_ids),
            results=results,
            summary=summary,
            duration_seconds=duration
        )
        
        self.workflow_history.append(workflow_result)
        
        self._log(f"\n{'='*60}")
        self._log(f"  🏁 Workflow Complete")
        self._log(f"  Completed: {completed} | Failed: {failed}")
        self._log(f"  Duration: {duration:.1f}s")
        self._log(f"{'='*60}\n")
        
        return workflow_result
    
    def run_pipeline(
        self,
        task_descriptions: List[str],
        agent_names: Optional[List[str]] = None
    ) -> WorkflowResult:
        """
        Run tasks in a pipeline
        Output of task N becomes input context for task N+1
        """
        self._log(f"\n{'='*60}")
        self._log(f"  🔗 Pipeline Workflow Starting")
        self._log(f"{'='*60}")
        
        # Create tasks with dependencies
        self.tasks.clear()
        
        for i, desc in enumerate(task_descriptions):
            task_id = f"step_{i+1}"
            agent_name = None
            
            if agent_names and i < len(agent_names):
                agent_name = agent_names[i]
            
            deps = [f"step_{i}"] if i > 0 else []
            
            self.add_task(
                task_id=task_id,
                description=desc,
                agent_name=agent_name,
                dependencies=deps
            )
        
        return self.run_sequential()
    
    def run_single(
        self,
        task: str,
        agent_name: Optional[str] = None
    ) -> str:
        """Run a single task with a specific agent"""
        self.tasks.clear()
        self.add_task("main", task, agent_name)
        result = self.run_sequential(["main"])
        return result.results.get("main", "No result")
    
    def run_debate(
        self,
        question: str,
        agent_names: Optional[List[str]] = None,
        rounds: int = 2
    ) -> WorkflowResult:
        """
        Multiple agents debate a topic
        Each agent sees previous arguments and responds
        """
        self._log(f"\n{'='*60}")
        self._log(f"  🗣️  Debate Mode Starting")
        self._log(f"  Question: {question}")
        self._log(f"{'='*60}")
        
        names = agent_names or self.list_agents()
        
        if len(names) < 2:
            return WorkflowResult(
                success=False,
                tasks_completed=0,
                tasks_failed=1,
                total_tasks=1,
                results={},
                summary="Need at least 2 agents for debate"
            )
        
        self.tasks.clear()
        prev_task_id = None
        task_count = 0
        
        for round_num in range(1, rounds + 1):
            for name in names:
                task_count += 1
                task_id = f"round{round_num}_{name}"
                
                if round_num == 1 and prev_task_id is None:
                    desc = (
                        f"Share your perspective on: {question}\n"
                        f"You are starting the debate."
                    )
                    deps = []
                else:
                    desc = (
                        f"Continue the debate on: {question}\n"
                        f"Respond to the previous arguments. "
                        f"Add new insights or respectfully counter."
                    )
                    deps = [prev_task_id] if prev_task_id else []
                
                self.add_task(task_id, desc, name, deps)
                prev_task_id = task_id
        
        return self.run_sequential()
    
    # ========================================================
    # Utilities
    # ========================================================
    
    def _generate_summary(self, results: Dict[str, str]) -> str:
        """Generate a summary of all results"""
        if not results:
            return "No results to summarize"
        
        parts = ["Workflow Summary:"]
        for task_id, result in results.items():
            short_result = result[:200] if result else "No output"
            parts.append(f"  [{task_id}]: {short_result}")
        
        return "\n".join(parts)
    
    def get_status(self) -> Dict:
        """Get current status of all tasks"""
        return {
            "agents": self.list_agents(),
            "tasks": {
                tid: task.to_dict() 
                for tid, task in self.tasks.items()
            },
            "workflows_completed": len(self.workflow_history)
        }
    
    def reset(self):
        """Reset all tasks"""
        self.tasks.clear()
        for agent in self.agents.values():
            agent.reset()
    
    def __repr__(self):
        return (
            f"Orchestrator("
            f"agents={self.list_agents()}, "
            f"tasks={len(self.tasks)})"
        )
