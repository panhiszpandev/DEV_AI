import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify
from shared.ai_client import client
from tools import TOOLS

app = Flask(__name__)

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts/system.md")
with open(SYSTEM_PROMPT_PATH) as f:
    SYSTEM_PROMPT = f.read()

TOOL_DEFINITIONS = [{"type": "function", "function": t["schema"]} for t in TOOLS]
TOOL_MAP = {t["schema"]["name"]: t["callback"] for t in TOOLS}

sessions: dict[str, list] = {}


def run_agent(messages: list) -> str:
    max_iterations = 5
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  → {name}({args})")
            result = TOOL_MAP[name](**args)
            print(f"  ← {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    raise RuntimeError("Agent exceeded max iterations")


@app.route("/", methods=["POST"])
def handle():
    data = request.get_json()
    session_id = data.get("sessionID")
    msg = data.get("msg")

    if not session_id or not msg:
        return jsonify({"error": "Missing sessionID or msg"}), 400

    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    sessions[session_id].append({"role": "user", "content": msg})

    reply = run_agent(sessions[session_id])

    return jsonify({"msg": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
