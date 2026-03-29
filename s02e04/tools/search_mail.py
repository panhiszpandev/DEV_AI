from s02e04.zmail_client import call
from s02e04.state import save_state


class SearchMailTool:
    name = "search_mail"

    def __init__(self, state: dict):
        self.state = state

    def run(self, query: str, page: int = 1, per_page: int = 20) -> dict:
        result = call("search", query=query, page=page, perPage=per_page)

        if query not in self.state["searched_queries"]:
            self.state["searched_queries"].append(query)
            save_state(self.state)

        return result

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Search the mailbox using Gmail-style operators. "
                "Supports: from:, to:, subject:, OR, AND, \"phrase\", -exclude. "
                "Returns list of messages with metadata (no body). "
                "Use get_messages to fetch full content by rowID or messageID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query, e.g. 'from:proton.me' or 'subject:hasło OR subject:password'",
                    },
                    "page": {"type": "integer", "description": "Page number, default 1"},
                    "per_page": {"type": "integer", "description": "Results per page, between 5 and 20, default 20"},
                },
                "required": ["query"],
            },
        }
