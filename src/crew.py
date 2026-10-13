"""Crew assembly module coordinating sequential execution without delegation leaks."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple
from crewai import Crew, Process

from src.agents.crew_agents import ResearchCrewAgents
from src.tasks.crew_tasks import ResearchCrewTasks


class HierarchicalResearchCrew:
    """Coordinates the multi-agent pipeline sequentially with clean context passing."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.config_dir = base_dir / "config"
        self.output_dir = base_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.agents_factory = ResearchCrewAgents(self.config_dir)
        self.tasks_factory = ResearchCrewTasks(self.config_dir)

    def run(self, topic: str) -> Tuple[Any, str]:
        """Execute the crew on the target topic.

        Args:
            topic: The domain or technical subject to research and write about.

        Returns:
            Tuple containing the CrewOutput and the dynamic path where the file was saved.
        """
        # 1. Instantiate specialized worker agents
        researcher = self.agents_factory.senior_researcher()
        writer = self.agents_factory.technical_writer()
        editor = self.agents_factory.editorial_reviewer()

        # 2. Generate a dynamic, unique filename based on the topic and timestamp
        safe_topic = re.sub(r'[^a-z0-9]+', '_', topic.lower()).strip('_')
        if not safe_topic:
            safe_topic = "research_article"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dynamic_filename = f"{safe_topic}_{timestamp}.md"
        final_output_path = str(self.output_dir / dynamic_filename)

        # 3. Instantiate tasks with explicit context chaining
        t_research = self.tasks_factory.research_task(researcher)
        t_writing = self.tasks_factory.writing_task(writer, t_research)
        t_editing = self.tasks_factory.editing_task(
            editor, t_research, t_writing, final_output_path
        )

        # 4. Assemble Crew in Sequential Mode (Eliminates Manager JSON Leaks)
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[t_research, t_writing, t_editing],
            process=Process.sequential,
            verbose=False,
            output_log_file=str(self.output_dir / "crew_execution.log"),
        )

        result = crew.kickoff(inputs={"topic": topic})
        return result, final_output_path