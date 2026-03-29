from shared.hub_client import verify
from s02e04.state import save_state


class SubmitAnswerTool:
    name = "submit_answer"

    def __init__(self, state: dict):
        self.state = state

    def run(self, date: str = None, password: str = None, confirmation_code: str = None) -> dict:
        answer = {}
        if date:
            answer["date"] = date
        if password:
            answer["password"] = password
        if confirmation_code:
            answer["confirmation_code"] = confirmation_code

        result = verify("mailbox", answer)

        for key, value in answer.items():
            self.state["found"][key] = value
        self.state["last_feedback"] = result.get("message") or result.get("note") or str(result)
        self.state["missing"] = [k for k, v in self.state["found"].items() if v is None]
        save_state(self.state)

        return result

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Submit found values to the hub for verification. "
                "You can submit partial answers — the hub will tell you which values are still missing or incorrect. "
                "When all three values are correct the hub returns a flag {FLG:...}."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Planned attack date in YYYY-MM-DD format.",
                    },
                    "password": {
                        "type": "string",
                        "description": "Employee system password found in the mailbox.",
                    },
                    "confirmation_code": {
                        "type": "string",
                        "description": "Security ticket confirmation code, format: SEC- followed by 32 characters (36 total).",
                    },
                },
                "required": [],
            },
        }
