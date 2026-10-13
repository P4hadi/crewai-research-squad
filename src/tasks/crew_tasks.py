"""Task definitions and inter-task context chaining."""

from pathlib import Path
from typing import Any, Dict
import yaml
from crewai import Agent, Task


def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ResearchCrewTasks:
    """Factory for configuring tasks and downstream context passing."""

    def __init__(self, config_dir: Path) -> None:
        self.config = load_yaml_config(config_dir / "tasks.yaml")

    def research_task(self, agent: Agent) -> Task:
        return Task(
            description=self.config["research_task"]["description"],
            expected_output=self.config["research_task"]["expected_output"],
            agent=agent,
        )

    def writing_task(self, agent: Agent, research_task: Task) -> Task:
        return Task(
            description=self.config["writing_task"]["description"],
            expected_output=self.config["writing_task"]["expected_output"],
            agent=agent,
            context=[research_task],
        )

    def editing_task(
        self,
        agent: Agent,
        research_task: Task,
        writing_task: Task,
        output_file_path: str,
    ) -> Task:
        return Task(
            description=self.config["editing_task"]["description"],
            expected_output=self.config["editing_task"]["expected_output"],
            agent=agent,
            context=[research_task, writing_task],
            output_file=output_file_path,
        )