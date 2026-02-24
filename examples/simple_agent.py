"""
NexaFlow - Usage Examples
Shows how to use agents, tools, memory, and orchestrator

Run with: python examples/simple_agent.py
"""

from nexaflow import Agent, Tool, Memory, Orchestrator
from nexaflow.llm import LLMClient
from nexaflow.tools import ToolRegistry
from nexaflow.memory import MemoryManager


def divider(title: str):
    """Print a nice section divider"""
    print(f"\n{'='*60}")
    print(f"  🔹 {title}")
    print(f"{'='*60}\n")


# ============================================================
# Example 1: Simple Agent (No API needed!)
# ============================================================

def example_basic_agent():
    divider("Example 1: Basic Agent")
    
    # Create LLM client in mock mode (no API key needed)
    llm = LLMClient(provider="mock")
    
    # Create a simple agent
    agent = Agent(
        name="Assistant",
        role="A helpful AI assistant that answers questions clearly",
        llm=llm,
        tools=ToolRegistry(),
        memory=MemoryManager()
    )
    
    # Ask the agent something
    response = agent.run("What is artificial intelligence?")
    print(f"Agent says: {response}")
    
    # Ask another question (agent remembers context!)
    response = agent.run("Can you explain more about machine learning?")
    print(f"\nAgent says: {response}")
    
    print("\n✅ Basic agent works!")


# ============================================================
# Example 2: Agent with Tools
# ============================================================

def example_agent_with_tools():
    divider("Example 2: Agent with Tools")
    
    # Create tools registry and add built-in tools
    tools = ToolRegistry()
    tools.register_defaults()
    
    # Show available tools
    print("Available tools:")
    for name, tool in tools.list_tools().items():
        print(f"  🔧 {name}: {tool.description}")
    
    # Create agent with tools
    llm = LLMClient(provider="mock")
    agent = Agent(
        name="ToolUser",
        role="An agent that uses tools to solve problems",
        llm=llm,
        tools=tools,
        memory=MemoryManager()
    )
    
    # Use calculator tool directly
    print("\n--- Direct Tool Use ---")
    calc_result = tools.execute("calculator", expression="15 * 24 + 100")
    print(f"Calculator: 15 * 24 + 100 = {calc_result}")
    
    # Use datetime tool
    time_result = tools.execute("datetime", format="%Y-%m-%d %H:%M")
    print(f"Current time: {time_result}")
    
    # Let agent decide which tools to use
    print("\n--- Agent with Tools ---")
    response = agent.run("Calculate the result of 42 * 58")
    print(f"Agent says: {response}")
    
    print("\n✅ Tools working!")


# ============================================================
# Example 3: Memory System
# ============================================================

def example_memory():
    divider("Example 3: Memory System")
    
    memory = MemoryManager()
    
    # Store some memories
    memory.remember("User's name is Diego", importance=1.0)
    memory.remember("User likes Python programming", importance=0.8)
    memory.remember("User is building AI projects", importance=0.9)
    memory.remember("The weather is nice today", importance=0.2)
    memory.remember("User wants to learn about agents", importance=0.7)
    
    # Recall relevant memories
    print("Searching for 'programming' memories:")
    results = memory.recall("programming", top_k=3)
    for mem in results:
        print(f"  💭 {mem}")
    
    # Get memory stats
    stats = memory.get_stats()
    print(f"\nMemory stats: {stats}")
    
    # Get important memories
    print("\nMost important memories:")
    important = memory.get_important(top_k=3)
    for mem in important:
        print(f"  ⭐ {mem}")
    
    print("\n✅ Memory system works!")


# ============================================================
# Example 4: Custom Tools
# ============================================================

def example_custom_tools():
    divider("Example 4: Custom Tools")
    
    tools = ToolRegistry()
    
    # Create a custom tool using decorator-style
    def word_counter(text: str = "") -> str:
        """Count words in a text"""
        words = len(text.split())
        chars = len(text)
        return f"Words: {words}, Characters: {chars}"
    
    def text_reverser(text: str = "") -> str:
        """Reverse a text string"""
        return text[::-1]
    
    def number_facts(number: str = "7") -> str:
        """Get a fun fact about a number"""
        facts = {
            "7": "7 is considered lucky in many cultures",
            "42": "42 is the Answer to the Ultimate Question of Life",
            "100": "100 is called 'century' and is the basis of percentages",
            "0": "0 was invented in India around the 5th century",
            "13": "13 is considered unlucky in Western culture",
        }
        return facts.get(str(number), f"{number} is a number!")
    
    # Register custom tools
    tools.register(
        name="word_counter",
        description="Count words and characters in text",
        function=word_counter
    )
    tools.register(
        name="text_reverser",
        description="Reverse a text string",
        function=text_reverser
    )
    tools.register(
        name="number_facts",
        description="Get fun facts about numbers",
        function=number_facts
    )
    
    # Use custom tools
    print("Custom tools registered:")
    for name in tools.list_tools():
        print(f"  🔧 {name}")
    
    print(f"\nWord count: {tools.execute('word_counter', text='Hello world from NexaFlow AI framework')}")
    print(f"Reversed: {tools.execute('text_reverser', text='NexaFlow')}")
    print(f"Number fact: {tools.execute('number_facts', number='42')}")
    
    print("\n✅ Custom tools work!")


# ============================================================
# Example 5: Multi-Agent Orchestration
# ============================================================

def example_orchestration():
    divider("Example 5: Multi-Agent Orchestration")
    
    # Create orchestrator
    orch = Orchestrator(verbose=True)
    
    # Create specialized agents
    llm = LLMClient(provider="mock")
    tools = ToolRegistry()
    tools.register_defaults()
    
    researcher = Agent(
        name="Researcher",
        role="Research topics thoroughly and gather information",
        llm=llm,
        tools=tools,
        memory=MemoryManager()
    )
    
    writer = Agent(
        name="Writer",
        role="Write clear and engaging content based on research",
        llm=llm,
        tools=ToolRegistry(),
        memory=MemoryManager()
    )
    
    reviewer = Agent(
        name="Reviewer",
        role="Review content for quality and suggest improvements",
        llm=llm,
        tools=ToolRegistry(),
        memory=MemoryManager()
    )
    
    # Add agents to orchestrator
    orch.add_agent(researcher)
    orch.add_agent(writer)
    orch.add_agent(reviewer)
    
    print(f"Agents: {orch.list_agents()}")
    
    # --- Sequential workflow ---
    print("\n--- Sequential Workflow ---")
    orch.add_task("research", "Research the topic: AI Agents", "Researcher")
    orch.add_task("write", "Write an article about AI Agents", "Writer", ["research"])
    orch.add_task("review", "Review the article for quality", "Reviewer", ["write"])
    
    result = orch.run_sequential()
    print(f"\nSuccess: {result.success}")
    print(f"Tasks completed: {result.tasks_completed}/{result.total_tasks}")
    
    # --- Pipeline workflow ---
    print("\n--- Pipeline Workflow ---")
    pipeline_result = orch.run_pipeline(
        task_descriptions=[
            "Research: What are the benefits of AI agents?",
            "Write a summary of the research findings",
            "Review and provide final recommendations"
        ],
        agent_names=["Researcher", "Writer", "Reviewer"]
    )
    print(f"Pipeline success: {pipeline_result.success}")
    
    print("\n✅ Orchestration works!")


# ============================================================
# Example 6: Agent with Real LLM (when you have API key)
# ============================================================

def example_real_llm():
    divider("Example 6: Real LLM (API Key Required)")
    
    print("To use a real LLM, set your API key:")
    print()
    print("  Option 1 - Together AI (Free tier):")
    print("    llm = LLMClient(")
    print("        provider='together',")
    print("        api_key='your-key-here'")
    print("    )")
    print()
    print("  Option 2 - OpenRouter (Free models):")
    print("    llm = LLMClient(")
    print("        provider='openrouter',")
    print("        api_key='your-key-here'")
    print("    )")
    print()
    print("  Option 3 - OpenAI:")
    print("    llm = LLMClient(")
    print("        provider='openai',")
    print("        api_key='your-key-here'")
    print("    )")
    print()
    print("  Then create agent:")
    print("    agent = Agent(")
    print("        name='SmartAgent',")
    print("        role='Helpful assistant',")
    print("        llm=llm,")
    print("        tools=ToolRegistry(),")
    print("        memory=MemoryManager()")
    print("    )")
    print("    response = agent.run('Hello!')")
    print()
    print("  🔑 Get free API keys:")
    print("    Together AI: https://api.together.xyz/")
    print("    OpenRouter: https://openrouter.ai/")
    
    print("\n✅ See README.md for more details!")


# ============================================================
# Main - Run all examples
# ============================================================

if __name__ == "__main__":
    print()
    print("  ███╗   ██╗███████╗██╗  ██╗ █████╗ ███████╗██╗      ██████╗ ██╗    ██╗")
    print("  ████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██║     ██╔═══██╗██║    ██║")
    print("  ██╔██╗ ██║█████╗   ╚███╔╝ ███████║█████╗  ██║     ██║   ██║██║ █╗ ██║")
    print("  ██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██╔══╝  ██║     ██║   ██║██║███╗██║")
    print("  ██║ ╚████║███████╗██╔╝ ██╗██║  ██║██║     ███████╗╚██████╔╝╚███╔███╔╝")
    print("  ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝")
    print()
    print("  🚀 NexaFlow Examples - Lightweight AI Agent Framework")
    print("  📦 Version 0.1.0")
    print()
    
    examples = [
        ("Basic Agent", example_basic_agent),
        ("Agent with Tools", example_agent_with_tools),
        ("Memory System", example_memory),
        ("Custom Tools", example_custom_tools),
        ("Multi-Agent Orchestration", example_orchestration),
        ("Real LLM Guide", example_real_llm),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n  ❌ Example '{name}' error: {e}")
            print(f"     This is normal if running outside the package")
    
    print(f"\n{'='*60}")
    print(f"  🎉 All examples completed!")
    print(f"  📖 Read README.md for more information")
    print(f"  ⭐ Star the repo if you like it!")
    print(f"  🔗 https://github.com/Diegoproggramer/nexaflow")
    print(f"{'='*60}\n")
