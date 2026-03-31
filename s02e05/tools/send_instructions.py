from shared.hub_client import verify


class SendInstructionsTool:
    name = "send_instructions"

    def run(self, instructions: list) -> dict:
        return verify("drone", {"instructions": instructions})

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Send a sequence of drone instructions to the hub API. "
                "The API returns precise error messages — read them carefully and adjust. "
                "When the response contains {FLG:...}, the mission is complete. "
                "To reset corrupted configuration, send ['hardReset'] as the only instruction."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "instructions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Ordered list of drone instructions, e.g. "
                            "['setDestinationObject(PWR6132PL)', 'set(2,3)', 'set(destroy)', 'flyToLocation']"
                        ),
                    }
                },
                "required": ["instructions"],
            },
        }
