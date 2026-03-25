import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.hub_client import verify
from tools.count_tokens import count

TASK = "failure"


def schema() -> dict:
    return {
        "name": "submit_logs",
        "description": (
            "Submit compressed logs to the Hub for verification. "
            "Returns feedback from technicians or a flag if successful. "
            "Only call this after confirming token count is within 1500."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "logs": {
                    "type": "string",
                    "description": "Newline-separated log entries. Each line: timestamp, severity, component ID, short description.",
                }
            },
            "required": ["logs"],
            "additionalProperties": False,
        },
    }


def run(logs: str) -> dict:
    token_count = count(logs)
    if token_count > 1500:
        return {
            "error": f"Token count {token_count} exceeds limit of 1500. Compress further before submitting.",
            "token_count": token_count,
        }

    result = verify(TASK, {"logs": logs})
    return result
