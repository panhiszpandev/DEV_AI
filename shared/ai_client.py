import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def ask(system_prompt: str, user_message: str, model: str = "gpt-4o-mini") -> str:
    """Sends a request to the model and returns the response as text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


def ask_vision(system_prompt: str, image_b64: str, user_message: str, model: str = "google/gemini-2.0-flash-001") -> str:
    """Sends an image (base64) and a text message to a vision model and returns the response as text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                    {"type": "text", "text": user_message},
                ],
            },
        ],
    )
    return response.choices[0].message.content


def ask_json(system_prompt: str, user_message: str, schema: dict, model: str = "gpt-4o-mini") -> dict:
    """Sends a request and returns the response as JSON (Structured Output)."""
    import json
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": schema,
            },
        },
    )
    return json.loads(response.choices[0].message.content)
