"""CLI entry point for the Multi-Agent Research & Writing Crew."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

import litellm
import copy

# ==============================================================================
# MONKEY-PATCH: Fix CrewAI 1.14.x Bug with Groq (Strip cache_breakpoint)
# ==============================================================================
original_completion = litellm.completion

def patched_completion(*args, **kwargs):
    # 1. Check if messages are passed via kwargs
    if "messages" in kwargs:
        kwargs["messages"] = [
            {k: v for k, v in msg.items() if k != "cache_breakpoint"} 
            for msg in kwargs["messages"]
        ]
    # 2. Check if messages are passed as the 2nd positional argument
    elif len(args) > 1 and isinstance(args[1], list):
        args_list = list(args)
        args_list[1] = [
            {k: v for k, v in msg.items() if k != "cache_breakpoint"} 
            for msg in args_list[1]
        ]
        args = tuple(args_list)
        
    return original_completion(*args, **kwargs)

# Apply the patch
litellm.completion = patched_completion
# ==============================================================================

# Ensure root directory is discoverable in PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.crew import HierarchicalResearchCrew


def main() -> None:
    # Load environment variables from the project root
    load_dotenv(ROOT_DIR / ".env")

    print("\n" + "=" * 65)
    print("  PRODUCTION HIERARCHICAL MULTI-AGENT RESEARCH & WRITING CREW")
    print("=" * 65)

    # Determine the configured LLM provider (Ollama, Gemini, or Groq)
    provider = os.getenv("LLM_PROVIDER", "ollama").lower().strip()
    print(f"[*] Configured LLM Engine: {provider.upper()}")

    # Collect topic from command-line arguments or prompt the user
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("\nEnter technical topic to research & draft: ").strip()

    if not topic:
        print("[!] Error: Topic cannot be empty. Aborting.")
        sys.exit(1)

    print(f"\n[*] Initiating hierarchical crew on topic: '{topic}'")
    print("[*] Assembling Manager, Senior Researcher, Writer, and Editor...\n")

    # Initialize the hierarchical crew orchestrator
    crew_runner = HierarchicalResearchCrew(base_dir=ROOT_DIR)

    try:
        # Execute the run and unpack the auto-generated filename
        result, final_file = crew_runner.run(topic=topic)

        print("\n" + "=" * 65)
        print("  WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 65)
        print(f"[✓] Final article saved to: {final_file}")
        print(f"[✓] Detailed execution trace logged to: {ROOT_DIR / 'output' / 'crew_execution.log'}\n")

    except Exception as exc:
        print(f"\n[!] Crew execution encountered an error: {str(exc)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()