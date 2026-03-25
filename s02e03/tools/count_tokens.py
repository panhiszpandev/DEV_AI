import tiktoken

ENCODING = tiktoken.get_encoding("cl100k_base")


def count(text: str) -> int:
    """Count tokens in text using cl100k_base encoding."""
    return len(ENCODING.encode(text))


def schema() -> dict:
    return {
        "name": "count_tokens",
        "description": "Count the number of tokens in a text string using cl100k_base encoding. Use this before submitting logs to verify the 1500 token limit.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count tokens for.",
                }
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    }


def run(text: str) -> dict:
    n = count(text)
    return {
        "token_count": n,
        "within_limit": n <= 1500,
        "limit": 1500,
    }
