import sys
import os
import re
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from shared.agent import run_agent
from tools.fetch_logs import schema as fetch_schema, run as fetch_run, log_stats
from tools.count_tokens import schema as tokens_schema, run as tokens_run
from tools.event_memory import schema as memory_schema, run as memory_run
from tools.submit_logs import schema as submit_schema, run as submit_run

MODEL = "gpt-4o-mini"
PROMPTS_DIR = Path(__file__).parent / "prompts"

TOOLS = [
    {"schema": fetch_schema(), "callback": fetch_run},
    {"schema": tokens_schema(), "callback": tokens_run},
    {"schema": memory_schema(), "callback": memory_run},
    {"schema": submit_schema(), "callback": submit_run},
]


def extract_flag(text: str):
    match = re.search(r"\{FLG:[^}]+\}", text or "")
    return match.group(0) if match else None


def main():
    parser = argparse.ArgumentParser(description="S02E03: Power plant log compression agent")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Max LLM calls in the agent loop (default: 20). Increase if feedback loop needs more rounds.",
    )
    args = parser.parse_args()

    memory_run(action="clear")
    stats = log_stats()
    print(f"Log stats: {stats}\n")

    system_prompt = (PROMPTS_DIR / "system.md").read_text()
    task_prompt = (PROMPTS_DIR / "task.md").read_text()

    result = run_agent(system_prompt, task_prompt, TOOLS, model=MODEL, max_iterations=args.max_iterations)

    if not result:
        print("\nAgent stopped without a response.")
        return

    flag = extract_flag(result)
    if flag:
        print(f"\n=== FLAG: {flag} ===")
    else:
        print(f"\nAgent response: {result}")


if __name__ == "__main__":
    main()
