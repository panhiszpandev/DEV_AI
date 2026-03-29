from s02e04.zmail_client import call
from s02e04.state import save_state


class CheckNewMailTool:
    name = "check_new_mail"

    def __init__(self, state: dict):
        self.state = state

    def run(self) -> dict:
        data = call("getInbox", page=1, perPage=20)
        items = data.get("items", [])

        new_items = []
        for item in items:
            row_id = str(item["rowID"])
            modify_hash = item["modifyHash"]
            if self.state["inbox_snapshot"].get(row_id) != modify_hash:
                new_items.append(item)
                self.state["inbox_snapshot"][row_id] = modify_hash

        save_state(self.state)

        return {
            "new_count": len(new_items),
            "items": new_items,
            "message": f"{len(new_items)} new or updated message(s) found." if new_items else "No new messages since last check.",
        }

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Check the inbox for new or updated messages since the last poll. "
                "Returns messages not yet seen. Call this when you have processed all "
                "available messages and need to wait for new ones to arrive."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
