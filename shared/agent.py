import json
from shared.ai_client import client


def run_agent(system_prompt: str, task: str, tools: list, model: str = "gpt-4o") -> str:
    """
    Runs a function calling loop until the model stops calling tools.

    Each tool in the list must have:
    - "schema": dict with name, description, parameters (OpenAI function schema)
    - "callback": callable that executes the tool and returns a result
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]
    tool_definitions = [{"type": "function", "function": t["schema"]} for t in tools]
    tool_map = {t["schema"]["name"]: t["callback"] for t in tools}

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"  → calling {name}({args})")
            result = tool_map[name](**args)
            print(f"  ← {name} returned: {str(result)[:120]}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })
