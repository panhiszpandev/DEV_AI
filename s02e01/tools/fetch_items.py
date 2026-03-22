import csv
import io

from shared.hub_client import get_data, HUB_KEY


class FetchItemsTool:
    name = "fetch_items"

    def run(self) -> list[dict]:
        resp = get_data(f"/data/{HUB_KEY}/categorize.csv")
        reader = csv.DictReader(io.StringIO(resp.text))
        items = [{"id": row["id"], "description": row["description"]} for row in reader]
        print(f"  Fetched {len(items)} items")
        for item in items:
            print(f"    [{item['id']}] {item['description']}")
        return items

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Downloads fresh CSV from hub. Returns list of {id, description} dicts. "
                "Call first to inspect items before designing your prompt."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
