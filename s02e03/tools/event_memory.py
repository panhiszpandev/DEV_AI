import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from pathlib import Path

MEMORY_FILE = Path(__file__).parent.parent / "data" / "collected.log"


def _read_lines() -> list:
    if not MEMORY_FILE.exists():
        return []
    return [l for l in MEMORY_FILE.read_text().splitlines() if l.strip()]


def schema() -> dict:
    return {
        "name": "event_memory",
        "description": (
            "Manage the in-progress log collection stored on disk. "
            "Use action='save' to append selected log lines (keeps context small). "
            "Use action='read' to see what has been collected so far and its token count. "
            "Use action='clear' to reset and start fresh."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["save", "read", "clear"],
                    "description": "'save' appends lines, 'read' returns current contents, 'clear' resets.",
                },
                "lines": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Log lines to save. Required when action='save'.",
                },
            },
            "required": ["action"],
            "additionalProperties": False,
        },
    }


def run(action: str, lines: list = None) -> dict:
    MEMORY_FILE.parent.mkdir(exist_ok=True)

    if action == "clear":
        MEMORY_FILE.write_text("")
        return {"status": "cleared"}

    if action == "save":
        if not lines:
            return {"error": "lines required for action='save'"}
        existing = set(_read_lines())
        new_lines = [l for l in lines if l.strip() and l not in existing]
        if new_lines:
            with MEMORY_FILE.open("a") as f:
                f.write("\n".join(new_lines) + "\n")
        return {"saved": len(new_lines), "skipped_duplicates": len(lines) - len(new_lines), "total_saved": len(existing) + len(new_lines)}

    if action == "read":
        from tools.count_tokens import count
        current = _read_lines()
        text = "\n".join(current)
        return {"line_count": len(current), "token_count": count(text), "within_limit": count(text) <= 1500}

    return {"error": f"Unknown action: {action}"}
