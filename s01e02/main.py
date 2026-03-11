import sys
import os
import json
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.hub_client import verify, get_data, HUB_KEY

SUSPECTS_PATH = os.path.join(os.path.dirname(__file__), "../s01e01/data/transport_people.json")


def fetch_power_plants() -> list:
    response = get_data(f"/data/{HUB_KEY}/findhim_locations.json")
    plants = response.json()["power_plants"]
    return [{"city": city, **info} for city, info in plants.items()]


def main():
    # 1. Fetch power plants
    power_plants = fetch_power_plants()


if __name__ == "__main__":
    main()
