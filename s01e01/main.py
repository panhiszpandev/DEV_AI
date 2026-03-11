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

# --- JSON schema for Structured Output ---
TAGS_SCHEMA = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["IT", "transport", "edukacja", "medycyna", "praca z ludźmi", "praca z pojazdami", "praca fizyczna"],
            },
        }
    },
    "required": ["tags"],
    "additionalProperties": False,
}


def get_tags(job_description: str) -> list[str]:
    result = ask_json(SYSTEM_PROMPT, job_description, TAGS_SCHEMA)
    return result["tags"]


def calculate_age(birth_year: int) -> int:
    return date.today().year - birth_year


def main():
    # 1. Fetch data from hub
    print("Fetching data...")
    response = get_data(f"/data/{HUB_KEY}/people.csv")
    reader = csv.DictReader(io.StringIO(response.text))
    people = list(reader)
    print(f"Fetched {len(people)} people")

    # 2. Filter: male, born in Grudziądz, age 20-40 in 2026
    filtered = [
        p for p in people
        if p.get("gender", "").upper() == "M"
        and p.get("city", "").lower() == "grudziądz"
        and 20 <= calculate_age(int(p["born"])) <= 40
    ]
    print(f"After filtering: {len(filtered)} people")

    # 3. Tag each person's job using the model
    results = []
    for person in filtered:
        tags = get_tags(person["job"])
        if "transport" in tags:
            results.append({
                "name": person["name"],
                "surname": person["surname"],
                "gender": person["gender"].upper(),
                "born": int(person["born"]),
                "city": person["city"],
                "tags": tags,
            })

    print(f"Found {len(results)} people with 'transport' tag")
    print(results)

    # 4. Send answer to Hub
    verify("people", results)


if __name__ == "__main__":
    main()
