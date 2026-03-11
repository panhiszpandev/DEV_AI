import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUB_KEY = os.getenv("HUB_API_KEY")
HUB_URL = "https://hub.ag3nts.org"


def verify(task: str, answer) -> dict:
    """Sends the answer to the Hub and returns the flag or error."""
    resp = requests.post(
        f"{HUB_URL}/verify",
        json={
            "apikey": HUB_KEY,
            "task": task,
            "answer": answer,
        },
    )
    result = resp.json()
    print(f"Hub response: {result}")
    return result


def get_data(path: str) -> requests.Response:
    """Fetches data from the hub. path e.g. '/data/people.csv'"""
    url = f"{HUB_URL}{path}".replace("tutaj-twój-klucz", HUB_KEY)
    return requests.get(url)
