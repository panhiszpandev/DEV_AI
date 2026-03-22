import json

from shared.hub_client import verify
from tools.fetch_items import FetchItemsTool

TASK = "categorize"


class ClassifyAllTool:
    name = "classify_all"

    def __init__(self):
        self._fetcher = FetchItemsTool()

    def run(self, prompt_template: str) -> dict:
        items = self._fetcher.run()
        results = []

        for item in items:
            prompt = prompt_template.replace("{id}", item["id"]).replace(
                "{description}", item["description"]
            )
            print(f"  [{item['id']}] {prompt[:80]}...")
            data = verify(TASK, {"prompt": prompt})
            results.append({"id": item["id"], "description": item["description"], "hub": data})

            response_str = json.dumps(data)
            if "{FLG:" in response_str:
                return {"status": "flag_found", "flag": response_str, "results": results}
            if data.get("code") == 429 or "budget" in response_str.lower():
                return {"status": "budget_exceeded", "results": results}

        return {"status": "completed", "results": results}

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Sends a prompt template to the hub for all 10 items. "
                "Substitutes {id} and {description} with real item data before each request. "
                "Returns hub responses per item. On success returns status='flag_found' with the flag. "
                "Prompt must be under 100 tokens after substitution for every item."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_template": {
                        "type": "string",
                        "description": "Prompt with {id} and {description} placeholders placed at the end.",
                    }
                },
                "required": ["prompt_template"],
            },
        }
