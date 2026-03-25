import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from pathlib import Path
from shared.hub_client import verify
from tools.count_tokens import count
from tools.event_memory import MEMORY_FILE, _read_lines

TASK = "failure"


def _sort_chronologically(lines: list) -> list:
    """Sort log lines by full timestamp extracted from [YYYY-MM-DD HH:MM] or [YYYY-MM-DD HH:MM:SS]."""
    pattern = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}(?::\d{2})?)\]")

    def sort_key(line):
        m = pattern.match(line.strip())
        return m.group(1) if m else line

    return sorted(lines, key=sort_key)


def schema() -> dict:
    return {
        "name": "submit_logs",
        "description": (
            "Submit the collected events from memory to the Hub for verification. "
            "Reads from the on-disk memory (populated via event_memory save), "
            "sorts chronologically, checks the 1500-token limit, then submits. "
            "Returns feedback from technicians or a flag if successful."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    }


def run() -> dict:
    lines = _read_lines()
    if not lines:
        return {"error": "Memory is empty. Use event_memory save to collect events first."}

    lines = _sort_chronologically(lines)
    logs = "\n".join(lines)

    token_count = count(logs)
    if token_count > 1500:
        return {
            "error": f"Token count {token_count} exceeds limit of 1500. Use event_memory read to review, then remove less important entries.",
            "token_count": token_count,
            "line_count": len(lines),
        }

    result = verify(TASK, {"logs": logs})
    return result
