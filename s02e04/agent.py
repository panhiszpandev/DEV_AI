"""Agent that searches the mailbox and extracts three target values."""

import os

from shared.agent import run_agent
from s02e04.state import load_state
from s02e04.tools.search_mail import SearchMailTool
from s02e04.tools.get_messages import GetMessagesTool
from s02e04.tools.get_thread import GetThreadTool
from s02e04.tools.submit_answer import SubmitAnswerTool
from s02e04.tools.check_new_mail import CheckNewMailTool

MODEL = "google/gemini-3-flash-preview"
MAX_ITERATIONS = 100


def _load_system_prompt() -> str:
    path = os.path.join(os.path.dirname(__file__), "prompts", "system.md")
    with open(path) as f:
        return f.read()


def _build_task(state: dict) -> str:
    found = state["found"]
    lines = ["Investigate the mailbox and find all three values.\n"]
    lines.append("## Current state")
    lines.append(f"- date: {'FOUND: ' + found['date'] if found['date'] else 'NOT FOUND'}")
    lines.append(f"- password: {'FOUND: ' + found['password'] if found['password'] else 'NOT FOUND'}")
    lines.append(f"- confirmation_code: {'FOUND: ' + found['confirmation_code'] if found['confirmation_code'] else 'NOT FOUND'}")

    if state["last_feedback"]:
        lines.append(f"\n## Last hub feedback\n{state['last_feedback']}")

    if state["searched_queries"]:
        lines.append("\n## Already searched queries\n" + "\n".join(f"- {q}" for q in state["searched_queries"]))

    if state["processed_message_ids"]:
        lines.append("\n## Already processed message IDs\n" + ", ".join(state["processed_message_ids"]))

    if state["missing"]:
        lines.append(f"\n## Still missing: {', '.join(state['missing'])}")
        lines.append("Continue searching. Do not repeat queries that have already been searched.")
    else:
        lines.append("\nAll values found. Submit the final answer.")

    return "\n".join(lines)


def run() -> None:
    state = load_state()
    system_prompt = _load_system_prompt()
    task = _build_task(state)

    tools = [
        SearchMailTool(state),
        GetMessagesTool(state),
        GetThreadTool(),
        SubmitAnswerTool(state),
        CheckNewMailTool(state),
    ]

    print("[agent] starting...")
    try:
        result = run_agent(
            system_prompt=system_prompt,
            task=task,
            tools=[{"schema": t.schema(), "callback": t.run} for t in tools],
            model=MODEL,
            max_iterations=MAX_ITERATIONS,
        )
        print(f"[agent] finished: {result}")
    except RuntimeError as e:
        print(f"[agent] exceeded max iterations: {e}")
        print("[agent] state saved — restart to continue from where we left off")
