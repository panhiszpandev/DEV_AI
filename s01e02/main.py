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


def fetch_locations(name: str, surname: str) -> list:
    response = requests.post(
        "https://hub.ag3nts.org/api/location",
        json={"apikey": HUB_KEY, "name": name, "surname": surname},
    )
    return response.json()


def fetch_access_level(name: str, surname: str, birth_year: int) -> int:
    response = requests.post(
        "https://hub.ag3nts.org/api/accesslevel",
        json={"apikey": HUB_KEY, "name": name, "surname": surname, "birthYear": birth_year},
    )
    return response.json()


def main():
    # 1. Fetch power plants
    power_plants = fetch_power_plants()

    # 2. Load suspects from s01e01
    with open(SUSPECTS_PATH) as f:
        suspects = json.load(f)

    # 3. Fetch locations and access level for each suspect
    suspects_with_data = []
    for person in suspects:
        locations = fetch_locations(person["name"], person["surname"])
        access_level = fetch_access_level(person["name"], person["surname"], person["born"])
        suspects_with_data.append({**person, "locations": locations, "accessLevel": access_level})
        print(f"{person['name']} {person['surname']}: locations={locations}, accessLevel={access_level}")


if __name__ == "__main__":
    main()
