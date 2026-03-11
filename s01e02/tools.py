import os
import sys
import json
import math
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.hub_client import HUB_KEY, get_data, verify

SUSPECTS_PATH = os.path.join(os.path.dirname(__file__), "../s01e01/data/transport_people.json")

PLANT_COORDS = {
    "Zabrze":               {"lat": 50.3249, "lon": 18.7857},
    "Piotrków Trybunalski": {"lat": 51.4050, "lon": 19.7030},
    "Grudziądz":            {"lat": 53.4837, "lon": 18.7536},
    "Tczew":                {"lat": 54.0921, "lon": 18.7784},
    "Radom":                {"lat": 51.4027, "lon": 21.1471},
    "Chelmno":              {"lat": 53.3498, "lon": 18.4301},
    "Żarnowiec":            {"lat": 54.8569, "lon": 18.1590},
}


# --- Callbacks ---

def get_suspects() -> list:
    with open(SUSPECTS_PATH) as f:
        return json.load(f)


def get_power_plants() -> list:
    response = get_data(f"/data/{HUB_KEY}/findhim_locations.json")
    plants = response.json()["power_plants"]
    return [
        {"city": city, **info, **PLANT_COORDS[city]}
        for city, info in plants.items()
    ]


def get_locations(name: str, surname: str) -> list:
    response = requests.post(
        "https://hub.ag3nts.org/api/location",
        json={"apikey": HUB_KEY, "name": name, "surname": surname},
    )
    return response.json()


def get_access_level(name: str, surname: str, birth_year: int) -> dict:
    response = requests.post(
        "https://hub.ag3nts.org/api/accesslevel",
        json={"apikey": HUB_KEY, "name": name, "surname": surname, "birthYear": birth_year},
    )
    return response.json()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return round(R * 2 * math.asin(math.sqrt(a)), 2)


def submit_answer(name: str, surname: str, access_level: int, power_plant_code: str) -> dict:
    return verify("findhim", {
        "name": name,
        "surname": surname,
        "accessLevel": access_level,
        "powerPlant": power_plant_code,
    })


# --- Tool definitions (schema + callback) ---

TOOLS = [
    {
        "schema": {
            "name": "get_suspects",
            "description": "Returns the list of suspects from task s01e01 (name, surname, born).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        "callback": get_suspects,
    },
    {
        "schema": {
            "name": "get_power_plants",
            "description": "Returns the list of power plants with city name, code, and GPS coordinates (lat, lon).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        "callback": get_power_plants,
    },
    {
        "schema": {
            "name": "get_locations",
            "description": "Returns GPS coordinates of all locations where a suspect was spotted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "surname": {"type": "string"},
                },
                "required": ["name", "surname"],
            },
        },
        "callback": get_locations,
    },
    {
        "schema": {
            "name": "get_access_level",
            "description": "Returns the access level of a suspect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "surname": {"type": "string"},
                    "birth_year": {"type": "integer"},
                },
                "required": ["name", "surname", "birth_year"],
            },
        },
        "callback": get_access_level,
    },
    {
        "schema": {
            "name": "calculate_distance",
            "description": "Calculates the distance in km between two GPS coordinates using the haversine formula.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat1": {"type": "number"},
                    "lon1": {"type": "number"},
                    "lat2": {"type": "number"},
                    "lon2": {"type": "number"},
                },
                "required": ["lat1", "lon1", "lat2", "lon2"],
            },
        },
        "callback": calculate_distance,
    },
    {
        "schema": {
            "name": "submit_answer",
            "description": "Submits the final answer to the Hub. Call this once you have identified the correct suspect and power plant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "surname": {"type": "string"},
                    "access_level": {"type": "integer"},
                    "power_plant_code": {"type": "string", "description": "Power plant code in format PWR0000PL"},
                },
                "required": ["name", "surname", "access_level", "power_plant_code"],
            },
        },
        "callback": submit_answer,
    },
]
