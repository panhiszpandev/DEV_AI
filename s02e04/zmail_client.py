import os
import requests
from dotenv import load_dotenv

load_dotenv()

_URL = "https://hub.ag3nts.org/api/zmail"
_API_KEY = os.getenv("HUB_API_KEY")


def call(action: str, **kwargs) -> dict:
    return requests.post(_URL, json={"apikey": _API_KEY, "action": action, **kwargs}).json()
