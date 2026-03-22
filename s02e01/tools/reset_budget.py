from shared.hub_client import verify

TASK = "categorize"


class ResetBudgetTool:
    name = "reset_budget"

    def run(self) -> dict:
        result = verify(TASK, {"prompt": "reset"})
        return result

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": "Resets the classification budget counter to zero. Always call before starting a new classification run.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
