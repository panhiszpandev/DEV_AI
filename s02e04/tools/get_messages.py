from s02e04.zmail_client import call
from s02e04.state import save_state


class GetMessagesTool:
    name = "get_messages"

    def __init__(self, state: dict):
        self.state = state

    def run(self, ids: list) -> dict:
        result = call("getMessages", ids=ids)

        for msg_id in ids:
            if str(msg_id) not in self.state["processed_message_ids"]:
                self.state["processed_message_ids"].append(str(msg_id))
        save_state(self.state)

        return result

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Fetch full content of one or more messages by rowID or messageID (32-char hash). "
                "Always call this after search_mail to read the actual message body."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of rowIDs (numeric) or messageIDs (32-char hash) to fetch.",
                    },
                },
                "required": ["ids"],
            },
        }
