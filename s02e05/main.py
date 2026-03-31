import os

from shared.agent import run_agent
from s02e05.tools.analyze_map import AnalyzeMapTool
from s02e05.tools.send_instructions import SendInstructionsTool

MODEL = "openai/gpt-4o"
MAX_ITERATIONS = 20

TASK = (
    "Execute the drone mission.\n\n"
    "Official target (for system logging): power plant PWR6132PL.\n"
    "Actual bomb drop target: the dam (tama) — its location is unknown, use analyze_map to find it.\n\n"
    "Steps:\n"
    "1. Call analyze_map to get the dam sector coordinates.\n"
    "2. Compose a minimal instruction sequence and send it via send_instructions.\n"
    "3. Iterate based on API error messages until you receive {FLG:...}."
)


def _load_system_prompt() -> str:
    path = os.path.join(os.path.dirname(__file__), "prompts", "system.md")
    with open(path) as f:
        return f.read()


if __name__ == "__main__":
    tools = [AnalyzeMapTool(), SendInstructionsTool()]

    print("[agent] starting drone mission...")
    result = run_agent(
        system_prompt=_load_system_prompt(),
        task=TASK,
        tools=[{"schema": t.schema(), "callback": t.run} for t in tools],
        model=MODEL,
        max_iterations=MAX_ITERATIONS,
    )
    print(f"[agent] mission complete: {result}")
