import sys
import os
import json
import math
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.hub_client import verify, get_data, HUB_KEY

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


def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def find_closest(suspects_with_data: list, power_plants: list) -> dict:
    best = None
    best_dist = float("inf")
    for person in suspects_with_data:
        for loc in person["locations"]:
            for plant in power_plants:
                coords = PLANT_COORDS[plant["city"]]
                dist = haversine(loc["latitude"], loc["longitude"], coords["lat"], coords["lon"])
                if dist < best_dist:
                    best_dist = dist
                    best = {"person": person, "plant": plant, "distanceKm": dist}
    return best


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

    # 4. Find closest suspect-plant pair using haversine
    match = find_closest(suspects_with_data, power_plants)
    person = match["person"]
    plant = match["plant"]
    print(f"Closest: {person['name']} {person['surname']} near {plant['city']} ({match['distanceKm']:.2f} km)")
    print(f"Access level: {person['accessLevel']['accessLevel']}, Power plant: {plant['code']}")

    # 5. Send answer to Hub
    verify("findhim", {
        "name": person["name"],
        "surname": person["surname"],
        "accessLevel": person["accessLevel"]["accessLevel"],
        "powerPlant": plant["code"],
    })


if __name__ == "__main__":
    main()
