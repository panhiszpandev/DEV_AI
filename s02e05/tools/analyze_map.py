import base64
import os

import requests
from dotenv import load_dotenv

from shared.ai_client import ask_json

load_dotenv()

HUB_KEY = os.getenv("HUB_API_KEY")
MAP_URL = f"https://hub.ag3nts.org/data/{HUB_KEY}/drone.png"

VISION_MODEL = "openai/gpt-4o"

SYSTEM_PROMPT = (
    "You are an image analyst. You will receive an aerial photo of an area near a nuclear power plant. "
    "The image is divided into a grid by red lines.\n\n"
    "Step 1: Count the number of vertical red lines to determine columns, and horizontal red lines for rows. "
    "Be precise — count the internal lines only, then add 1.\n\n"
    "Step 2: Find the dam (tama). It is marked with an INTENSIFIED, VERY BRIGHT cyan/teal color — "
    "much brighter than any natural water in the image. Look carefully at every sector.\n\n"
    "Step 3: Report the exact column (left=1) and row (top=1) of the dam sector.\n\n"
    "Be extremely careful when counting. Describe each sector briefly before giving the final answer."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "grid_cols": {"type": "integer", "description": "Total number of columns in the grid"},
        "grid_rows": {"type": "integer", "description": "Total number of rows in the grid"},
        "dam_col": {"type": "integer", "description": "Column index of the dam sector (1-indexed)"},
        "dam_row": {"type": "integer", "description": "Row index of the dam sector (1-indexed)"},
        "reasoning": {"type": "string", "description": "Brief explanation of how the dam was identified"},
    },
    "required": ["grid_cols", "grid_rows", "dam_col", "dam_row", "reasoning"],
    "additionalProperties": False,
}


class AnalyzeMapTool:
    name = "analyze_map"

    def _query_vision(self, image_b64: str) -> dict:
        from shared.ai_client import client
        import json

        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                        {"type": "text", "text": "Analyze the grid and locate the dam sector."},
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "map_analysis",
                    "strict": True,
                    "schema": SCHEMA,
                },
            },
        )
        import json
        return json.loads(response.choices[0].message.content)

    def run(self) -> dict:
        from collections import Counter

        print(f"  [analyze_map] fetching map from {MAP_URL}")
        resp = requests.get(MAP_URL, timeout=30)
        resp.raise_for_status()
        image_b64 = base64.b64encode(resp.content).decode()

        results = []
        for i in range(3):
            r = self._query_vision(image_b64)
            print(f"  [analyze_map] attempt {i+1}: {r}")
            results.append(r)

        # majority vote on dam coordinates
        coords = Counter((r["dam_col"], r["dam_row"]) for r in results)
        best_col, best_row = coords.most_common(1)[0][0]

        grid_cols = Counter(r["grid_cols"] for r in results).most_common(1)[0][0]
        grid_rows = Counter(r["grid_rows"] for r in results).most_common(1)[0][0]

        final = {
            "grid_cols": grid_cols,
            "grid_rows": grid_rows,
            "dam_col": best_col,
            "dam_row": best_row,
            "reasoning": f"Majority vote from 3 attempts: {coords.most_common()}",
        }
        print(f"  [analyze_map] final (majority): {final}")
        return final

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": (
                "Fetches the area map and uses a vision model to locate the dam (tama) on the grid. "
                "Returns the grid dimensions and the dam sector column and row (1-indexed). "
                "Call this first before programming the drone."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
