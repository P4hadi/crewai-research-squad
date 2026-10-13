"""Agent definitions and LLM runtime configurations."""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from crewai import Agent, LLM

from src.tools.search_tools import free_web_search, scrape_tool

def get_configured_llm() -> LLM:
    """Instantiate the unified LLM wrapper according to active environment settings."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

    if provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from .env")
        return LLM(model=model, api_key=api_key, temperature=0.3)

    elif provider == "groq":
        model = os.getenv("GROQ_MODEL", "groq/openai/gpt-oss-20b")
        api_key = os.getenv("GROQ_API_KEY")
        return LLM(model=model, api_key=api_key, temperature=0.3)

    elif provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "ollama/llama3.1:8b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return LLM(model=model, base_url=base_url, temperature=0.3)

    raise ValueError(f"Unsupported LLM provider '{provider}'.")

def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class ResearchCrewAgents:
    """Factory for initializing specialized agents."""

    def __init__(self, config_dir: Path) -> None:
        self.config = load_yaml_config(config_dir / "agents.yaml")
        self.llm = get_configured_llm()

    def senior_researcher(self) -> Agent:
        return Agent(
            role=self.config["senior_researcher"]["role"],
            goal=self.config["senior_researcher"]["goal"],
            backstory=self.config["senior_researcher"]["backstory"],
            tools=[free_web_search, scrape_tool],
            llm=self.llm,
            allow_delegation=False,
            verbose=False,
            memory=False,
        )


    def technical_writer(self) -> Agent:
        return Agent(
            role=self.config["technical_writer"]["role"],
            goal=self.config["technical_writer"]["goal"],
            backstory=self.config["technical_writer"]["backstory"],
            tools=[],
            llm=self.llm,
            allow_delegation=False,
            verbose=False,  # <-- Disabled verbose UI
            memory=False,
        )

    def editorial_reviewer(self) -> Agent:
        return Agent(
            role=self.config["editorial_reviewer"]["role"],
            goal=self.config["editorial_reviewer"]["goal"],
            backstory=self.config["editorial_reviewer"]["backstory"],
            tools=[],
            llm=self.llm,
            allow_delegation=False,
            verbose=False,  # <-- Disabled verbose UI
            memory=False,
        )

    def content_coordinator(self) -> Agent:
        return Agent(
            role=self.config["content_coordinator"]["role"],
            goal=self.config["content_coordinator"]["goal"],
            backstory=self.config["content_coordinator"]["backstory"],
            llm=self.llm,
            allow_delegation=True,
            verbose=False,  # <-- Disabled verbose UI
            memory=False,
        )