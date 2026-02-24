"""
Orchestrator - Coordinates multiple agents working together.
"""

from nexaflow.agent import Agent


class Orchestrator:
    """
    Coordinates multiple agents to solve complex tasks.
    
    Example:
        orch = Orchestrator()
        orch.add_agent(Agent(name="Researcher", role="Research topics"))
        orch.add_agent(Agent(name="Writer", role="Write content"))
        result = orch.run("Write an article about AI")
    """
    
    def __init__(self, verbose: bool = True):
        self.agents: dict = {}
        self.verbose = verbose
    
    def add_agent(self, agent: Agent) -> None:
        """Add a new agent."""
        self.agents[agent.name] = agent
        if self.verbose:
            print(f"  + Agent '{agent.name}' added (role: {agent.role})")
    
    def run(self, task: str, strategy: str = "sequential") -> str:
        """
        Run a task across multiple agents.
        
        Strategies:
            - sequential: one after another (output of each feeds into next)
            - debate: agents discuss and reach consensus
        """
        if not self.agents:
            return "No agents registered!"
        
        if self.verbose:
            print(f"\n{'='*50}")
            print(f"  Task: {task}")
            print(f"  Strategy: {strategy}")
            print(f"  Agents: {len(self.agents)}")
            print(f"{'='*50}\n")
        
        if strategy == "sequential":
            return self._run_sequential(task)
        elif strategy == "debate":
            return self._run_debate(task)
        else:
            return self._run_sequential(task)
    
    def _run_sequential(self, task: str) -> str:
        """Sequential execution - output of each agent feeds into next."""
        current_input = task
        result = ""
        
        for i, (name, agent) in enumerate(self.agents.items()):
            if self.verbose:
                print(f"\n{'─'*40}")
                print(f"  Stage {i+1}: Agent '{name}'")
                print(f"{'─'*40}")
            
            result = agent.run(current_input)
            
            current_input = (
                f"Original task: {task}\n\n"
                f"Previous stage result ({name}): {result}\n\n"
                f"Continue based on your role."
            )
        
        return result
    
    def _run_debate(self, task: str, rounds: int = 3) -> str:
        """Debate execution - agents discuss the topic."""
        agent_list = list(self.agents.values())
        
        if len(agent_list) < 2:
            return agent_list[0].run(task) if agent_list else "No agents!"
        
        conversation = f"Topic: {task}\n\n"
        
        for round_num in range(rounds):
            if self.verbose:
                print(f"\n{'='*40}")
                print(f"  Round {round_num + 1}/{rounds}")
                print(f"{'='*40}")
            
            for agent in agent_list:
                prompt = (
                    f"{conversation}\n"
                    f"You are {agent.name} ({agent.role}). "
                    f"Share your perspective. "
                    f"{'If you disagree with someone, explain why.' if round_num > 0 else ''}"
                )
                
                response = agent.chat(prompt)
                conversation += f"\n{agent.name}: {response}\n"
                
                if self.verbose:
                    print(f"  {agent.name}: {response[:150]}...")
        
        summary_prompt = (
            f"{conversation}\n\n"
            f"Please provide a final summary based on all the discussion."
        )
        
        return agent_list[0].chat(summary_prompt)
