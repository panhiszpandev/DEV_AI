import os
import sys
import json
import time
import re
import requests
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.ai_client import client
from dotenv import load_dotenv

load_dotenv()

HUB_URL = "https://hub.ag3nts.org/verify"
API_KEY = os.getenv("HUB_API_KEY")
TASK = "railway"
ROUTE = "X-01"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

MAX_RETRIES = 10
INITIAL_BACKOFF = 2  # seconds


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def load_file(path: str) -> str:
    with open(path) as f:
        return f.read()


def call_api(answer: dict) -> tuple[dict, dict]:
    """
    Calls the railway API with retry on 503 and rate limit handling.
    Returns (response_json, headers).
    """
    payload = {"apikey": API_KEY, "task": TASK, "answer": answer}
    log(f"→ POST {json.dumps(answer)}")

    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        resp = requests.post(HUB_URL, json=payload, timeout=15)
        log(f"← HTTP {resp.status_code}")

        # Log rate limit headers
        rl_remaining = resp.headers.get("X-RateLimit-Remaining")
        rl_reset = resp.headers.get("X-RateLimit-Reset") or resp.headers.get("Retry-After")
        if rl_remaining is not None:
            log(f"   Rate limit remaining: {rl_remaining}, reset: {rl_reset}")

        if resp.status_code == 503:
            if rl_reset:
                wait = max(1, int(rl_reset) - int(time.time()))
            else:
                wait = backoff
            log(f"   503 received, retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait)
            backoff = min(backoff * 2, 60)
            continue

        if resp.status_code == 429:
            if rl_reset:
                wait = max(1, int(rl_reset) - int(time.time()))
            else:
                wait = backoff
            log(f"   Rate limited, waiting {wait}s (reset at {rl_reset})")
            time.sleep(wait)
            continue

        data = resp.json()
        log(f"   Response: {json.dumps(data)}")
        return data, dict(resp.headers)

    raise RuntimeError(f"API call failed after {MAX_RETRIES} retries")


def parse_action_sequence(help_json: str) -> list[dict]:
    """Uses LLM to parse API help and return ordered list of actions to open route."""
    system_prompt = load_file(os.path.join(PROMPTS_DIR, "system.md"))

    schema = {
        "type": "object",
        "properties": {
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "params": {"type": "object", "additionalProperties": {"type": "string"}},
                    },
                    "required": ["action", "params"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["actions"],
        "additionalProperties": False,
    }

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"API help:\n{help_json}\n\nDetermine the sequence of actions to OPEN route {ROUTE}."},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "actions", "schema": schema},
        },
    )
    result = json.loads(response.choices[0].message.content)
    return result["actions"]


def check_for_flag(data: dict) -> str:
    """Searches response for a flag in format {FLG:...}."""
    text = json.dumps(data)
    match = re.search(r"\{FLG:[^}]+\}", text)
    return match.group(0) if match else None


def main():
    # 1. Load saved help response
    log("=== Loading API help ===")
    help_json = load_file(os.path.join(DATA_DIR, "api_help.json"))
    log(f"Help loaded ({len(help_json)} chars)")

    # 2. Ask LLM to determine action sequence
    log("\n=== Parsing action sequence (LLM) ===")
    actions = parse_action_sequence(help_json)
    for i, a in enumerate(actions, 1):
        log(f"  Step {i}: {a['action']} {a['params']}")

    # 3. Execute actions in order
    log("\n=== Executing action sequence ===")
    for step in actions:
        answer = {"action": step["action"], **step["params"]}
        data, _ = call_api(answer)

        flag = check_for_flag(data)
        if flag:
            log(f"\n=== FLAG FOUND: {flag} ===")
            return

        if not data.get("ok"):
            log(f"   WARNING: action returned ok=false, stopping")
            return

    log("\n=== All actions completed, no flag in responses ===")


if __name__ == "__main__":
    main()
