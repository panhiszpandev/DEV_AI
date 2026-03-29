from s02e04.zmail_client import call


class GetThreadTool:
    name = "get_thread"

    def run(self, thread_id: int) -> dict:
        return call("getThread", threadID=thread_id)

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Fetch all message IDs in a thread by threadID. "
                "Returns rowIDs and messageIDs without body. "
                "Use get_messages afterwards to read the full content."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "integer",
                        "description": "Numeric thread identifier from inbox or search results.",
                    },
                },
                "required": ["thread_id"],
            },
        }
