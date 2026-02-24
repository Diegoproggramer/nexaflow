"""
NexaFlow - Setup Configuration
Install with: pip install .
Or from PyPI (future): pip install nexaflow
"""

from setuptools import setup, find_packages

# Read README for long description
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "NexaFlow - Lightweight AI Agent Framework"

setup(
    name="nexaflow",
    version="0.1.0",
    author="Diegoproggramer",
    author_email="",
    description="Lightweight AI Agent Framework - Build intelligent agents that think, use tools, and collaborate",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Diegoproggramer/nexaflow",
    project_urls={
        "Bug Reports": "https://github.com/Diegoproggramer/nexaflow/issues",
        "Source": "https://github.com/Diegoproggramer/nexaflow",
        "Documentation": "https://github.com/Diegoproggramer/nexaflow#readme",
    },
    
    # Find packages automatically
    packages=find_packages(),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "requests>=2.28.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "requests>=2.28.0",
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for searchability
    keywords=[
        "ai", "agent", "llm", "framework",
        "artificial-intelligence", "multi-agent",
        "tool-use", "react", "orchestrator",
        "chatbot", "autonomous-agents"
    ],
    
    # License
    license="MIT",
    
    # Include package data
    include_package_data=True,
    zip_safe=False,
)
