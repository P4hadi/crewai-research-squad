"""Custom search and extraction tools utilizing free search providers."""

from typing import Any, Dict, List
from crewai.tools import tool
from crewai_tools import ScrapeWebsiteTool

# UPDATE: Import from the new ddgs library
from ddgs import DDGS

@tool("Free Web Search")
def free_web_search(query: str) -> str:
    """Search the web for up-to-date facts, benchmarks, and technical references."""
    try:
        ddgs = DDGS()
        results: List[Dict[str, Any]] = list(ddgs.text(query, max_results=3))
        if not results:
            return f"No results found for query: '{query}'."

        formatted_results: List[str] = []
        for i, item in enumerate(results, start=1):
            title = item.get("title", "No Title")
            url = item.get("href", "")
            body = item.get("body", "No description available.")[:150]
            formatted_results.append(
                f"### Result {i}: {title}\n- **URL:** {url}\n- **Summary:** {body}...\n"
            )

        return "\n".join(formatted_results)
    except Exception as exc:
        return f"Error executing DuckDuckGo search: {str(exc)}"

scrape_tool = ScrapeWebsiteTool()