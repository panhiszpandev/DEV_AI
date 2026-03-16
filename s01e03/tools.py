import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.hub_client import HUB_KEY

PACKAGES_URL = "https://hub.ag3nts.org/api/packages"


# --- Callbacks ---

def check_package(packageid: str) -> dict:
    response = requests.post(PACKAGES_URL, json={"apikey": HUB_KEY, "action": "check", "packageid": packageid})
    return response.json()


def redirect_package(packageid: str, destination: str, code: str) -> dict:
    response = requests.post(PACKAGES_URL, json={
        "apikey": HUB_KEY,
        "action": "redirect",
        "packageid": packageid,
        "destination": destination,
        "code": code,
    })
    return response.json()


# --- Tool definitions (schema + callback) ---

TOOLS = [
    {
        "schema": {
            "name": "check_package",
            "description": "Checks the current status and details of a package by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "packageid": {"type": "string", "description": "The package ID to check"},
                },
                "required": ["packageid"],
            },
        },
        "callback": check_package,
    },
    {
        "schema": {
            "name": "redirect_package",
            "description": "Redirects a package to a new destination. Requires the package ID, destination code, and a security code provided by the operator.",
            "parameters": {
                "type": "object",
                "properties": {
                    "packageid": {"type": "string", "description": "The package ID to redirect"},
                    "destination": {"type": "string", "description": "Destination code (e.g. WAW2137PL)"},
                    "code": {"type": "string", "description": "Security code provided by the operator"},
                },
                "required": ["packageid", "destination", "code"],
            },
        },
        "callback": redirect_package,
    },
]
