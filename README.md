# 🚀 NexaFlow

**Next-generation AI Agent Framework**

Build autonomous AI agents that can think, use tools, and collaborate.

## ✨ Features

- 🤖 **Smart Agents** — Agents that think step-by-step using ReAct pattern
- 🔧 **Tool System** — Give agents abilities (search, calculate, read/write files)
- 🧠 **Memory** — Agents remember past interactions (short-term & long-term)
- 👥 **Multi-Agent Orchestration** — Multiple agents working together
- 🆓 **Zero Dependencies** — Only Python standard library needed
- ⚡ **Works with any LLM** — Groq (free), OpenAI, Ollama (local)

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/Diegoproggramer/nexaflow.git
cd nexaflow
pip install -e .

### Get a FREE API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create an API key
4. Set it as environment variable:

bash
export NEXAFLOW_API_KEY="your-key-here"

### Usage

python
from nexaflow import Agent

agent = Agent(name="My Assistant")
answer = agent.run("What is 2+2? Use the calculator.")
print(answer)

### Multi-Agent Example

python
from nexaflow import Agent, Orchestrator

orch = Orchestrator()
orch.add_agent(Agent(name="Researcher", role="Research and gather information"))
orch.add_agent(Agent(name="Writer", role="Write clear and engaging content"))

result = orch.run("Write a short paragraph about the future of AI")
print(result)

## 🏗️ Architecture


Agent = Brain (LLM) + Memory + Tools

┌─────────────────────────────────┐
│            Agent                │
│  ┌─────┐ ┌──────┐ ┌─────────┐  │
│  │ LLM │ │Memory│ │  Tools  │  │
│  └─────┘ └──────┘ └─────────┘  │
└─────────────────────────────────┘
▲
│
┌─────────────────────────────────┐
│        Orchestrator             │
│  Agent1 ←→ Agent2 ←→ Agent3    │
└─────────────────────────────────┘

## 📁 Project Structure


nexaflow/
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
├── nexaflow/
│   ├── __init__.py
│   ├── agent.py          # Core agent logic
│   ├── llm.py            # LLM connection
│   ├── memory.py         # Memory system
│   ├── tools.py          # Tool system
│   └── orchestrator.py   # Multi-agent orchestration
├── tests/
│   └── test_agent.py
└── examples/
└── simple_agent.py

## 🗺️ Roadmap

- [x] Core Agent with ReAct loop
- [x] Memory system (short-term & long-term)
- [x] Built-in tools (calculator, web search, file I/O)
- [x] Multi-agent orchestrator
- [ ] RAG (Retrieval Augmented Generation)
- [ ] Code execution tool
- [ ] Web UI
- [ ] Plugin system

## 📄 License

MIT License — Free for everyone.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.


### مرحله ۳: ذخیره
روی دکمه سبز **"Commit changes..."** بزن. یه پنجره باز میشه، بنویس:

Add README.md


بعد **"Commit changes"** رو بزن.

---

## 📁 فایل دوم: `nexaflow/__init__.py`

### مرحله ۱: برگرد به صفحه اصلی ریپو
روی **"nexaflow"** بالای صفحه کلیک کن

### مرحله ۲: فایل جدید بساز
روی دکمه **"Add file"** → **"Create new file"** کلیک کن

### مرحله ۳: اسم فایل
توی باکس اسم بنویس:

nexaflow/__init__.py


> **نکته مهم:** وقتی `/` رو بزنی، خودش یه فولدر `nexaflow` می‌سازه

### مرحله ۴: محتوا

```python
"""
NexaFlow - Next-generation AI Agent Framework
Build autonomous AI agents that can think, use tools, and collaborate.
"""

from nexaflow.agent import Agent
from nexaflow.tools import Tool
from nexaflow.memory import Memory
from nexaflow.orchestrator import Orchestrator

__version__ = "0.1.0"
__all__ = ["Agent", "Tool", "Memory", "Orchestrator"]
