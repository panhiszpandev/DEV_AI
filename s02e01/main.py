import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from shared.agent import run_agent
from tools.fetch_items import FetchItemsTool
from tools.reset_budget import ResetBudgetTool
from tools.classify_all import ClassifyAllTool

PROMPTS_DIR = Path(__file__).parent / "prompts"


def main():
    system_prompt = (PROMPTS_DIR / "system.md").read_text()

    instances = [FetchItemsTool(), ResetBudgetTool(), ClassifyAllTool()]
    tools = [{"schema": t.schema(), "callback": t.run} for t in instances]

    task = (PROMPTS_DIR / "task.md").read_text()

    result = run_agent(
        system_prompt=system_prompt,
        task=task,
        tools=tools,
        model="anthropic/claude-sonnet-4-6",
    )

    print(f"\n=== Result ===\n{result}")


if __name__ == "__main__":
    main()
