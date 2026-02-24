"""
Simple example of using NexaFlow.

Before running:
1. Install: pip install -e .
2. Get free API key from groq.com
3. export NEXAFLOW_API_KEY="your-key-here"
"""

from nexaflow import Agent, Tool, Orchestrator
from nexaflow.llm import LLMConfig


def example_1_simple():
    """Simplest example - ask a question."""
    print("\n Example 1: Simple Question")
    print("=" * 40)
    
    agent = Agent(name="Assistant")
    answer = agent.run("What is 2 to the power of 10? Use the calculator.")
    print(f"\nFinal answer: {answer}")


def example_2_custom_tool():
    """Create a custom tool."""
    print("\n Example 2: Custom Tool")
    print("=" * 40)
    
    import datetime
    
    date_tool = Tool(
        name="get_date",
        description="Returns the current date and time",
        function=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    
    agent = Agent(
        name="Time Assistant",
        role="Help with date and time questions",
        tools=[date_tool],
    )
    
    answer = agent.run("What is the current date and time?")
    print(f"\nAnswer: {answer}")


def example_3_multi_agent():
    """Multiple agents working together."""
    print("\n Example 3: Multi-Agent")
    print("=" * 40)
    
    orch = Orchestrator()
    
    orch.add_agent(Agent(
        name="Researcher",
        role="Research and gather information",
    ))
    
    orch.add_agent(Agent(
        name="Writer",
        role="Write clear and engaging content",
    ))
    
    result = orch.run(
        "Write a short paragraph about the future of AI",
        strategy="sequential",
    )
    
    print(f"\nFinal result:\n{result}")


if __name__ == "__main__":
    print("NexaFlow - Usage Examples")
    print("=" * 50)
    
    example_1_simple()
    # example_2_custom_tool()
    # example_3_multi_agent()
