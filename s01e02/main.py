import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.agent import run_agent
from tools import TOOLS

with open(os.path.join(os.path.dirname(__file__), "prompts/agent.md")) as f:
    SYSTEM_PROMPT = f.read()


def main():
    print("Starting agent...")
    result = run_agent(
        system_prompt=SYSTEM_PROMPT,
        task="Find which suspect was located near a nuclear power plant and submit the answer to the Hub.",
        tools=TOOLS,
    )
    print(f"\nAgent finished: {result}")


if __name__ == "__main__":
    main()
