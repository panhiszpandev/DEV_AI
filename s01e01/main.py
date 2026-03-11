import sys
import os
import csv
import io
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.ai_client import ask_json
from shared.hub_client import verify, get_data, HUB_KEY

# --- Load system prompt from .md file ---
with open(os.path.join(os.path.dirname(__file__), "prompts/tagger.md")) as f:
    SYSTEM_PROMPT = f.read()

# --- JSON schema for Structured Output (batch: list of results) ---
TAGS_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["IT", "transport", "edukacja", "medycyna", "praca z ludźmi", "praca z pojazdami", "praca fizyczna"],
                        },
                    },
                },
                "required": ["index", "tags"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def get_tags_batch(people: list) -> dict:
    # Build numbered list of job descriptions for the model
    jobs_list = "\n".join(f"{i}. {p['job']}" for i, p in enumerate(people))
    result = ask_json(SYSTEM_PROMPT, jobs_list, TAGS_SCHEMA)
    # Return a dict: index -> tags
    return {item["index"]: item["tags"] for item in result["results"]}


def calculate_age(birth_date: str) -> int:
    birth_year = int(birth_date.split("-")[0])
    return date.today().year - birth_year


def main():
    # 1. Fetch data from hub
    print("Fetching data...")
    response = get_data(f"/data/{HUB_KEY}/people.csv")
    reader = csv.DictReader(io.StringIO(response.text))
    people = list(reader)
    print(f"Fetched {len(people)} people")

    # 2. Filter: male, born in Grudziądz, age 20-40
    filtered = [
        p for p in people
        if p.get("gender", "").upper() == "M"
        and p.get("birthPlace", "").lower() == "grudziądz"
        and 20 <= calculate_age(p["birthDate"]) <= 40
    ]
    print(f"After filtering: {len(filtered)} people")

    # 3. Tag all jobs in a single API call
    print("Classifying jobs (1 API call)...")
    tagged = get_tags_batch(filtered)

    # 4. Keep only people tagged with 'transport'
    results = []
    for i, person in enumerate(filtered):
        tags = tagged.get(i, [])
        if "transport" in tags:
            results.append({
                "name": person["name"],
                "surname": person["surname"],
                "gender": person["gender"].upper(),
                "born": int(person["birthDate"].split("-")[0]),
                "city": person["birthPlace"],
                "tags": tags,
            })

    print(f"Found {len(results)} people with 'transport' tag")
    print(results)

    # 5. Send answer to Hub
    verify("people", results)


if __name__ == "__main__":
    main()
