import copy
import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "state.json")

DEFAULT_STATE = {
    "found": {
        "date": None,
        "password": None,
        "confirmation_code": None,
    },
    "missing": ["date", "password", "confirmation_code"],
    "last_feedback": None,
    "searched_queries": [],
    "processed_message_ids": [],
    "inbox_snapshot": {},
}


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return copy.deepcopy(DEFAULT_STATE)


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
