import os
import sys
import base64
import requests
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shared.ai_client import client, ask_json
from shared.hub_client import verify

DOC_BASE = "https://hub.ag3nts.org/dane/doc"
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_prompt(filename: str) -> str:
    with open(os.path.join(PROMPTS_DIR, filename)) as f:
        return f.read()


def load_data(filename: str) -> str:
    with open(os.path.join(DATA_DIR, filename)) as f:
        return f.read()


def fetch_doc(filename: str) -> str:
    url = f"{DOC_BASE}/{filename}"
    print(f"  GET {filename}")
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        return f"[ACCESS DENIED: HTTP {resp.status_code}]"
    return resp.text


def fetch_image_b64(filename: str) -> str:
    url = f"{DOC_BASE}/{filename}"
    print(f"  GET {filename} (image)")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return base64.standard_b64encode(resp.content).decode()


def extract_file_lists(index_content: str) -> tuple[list[str], list[str]]:
    """Asks LLM to extract text and image file references from index.md."""
    schema = {
        "type": "object",
        "properties": {
            "text_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of text files (.md) referenced in index.md",
            },
            "image_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of image files (.png, .jpg, etc.) referenced in index.md",
            },
        },
        "required": ["text_files", "image_files"],
        "additionalProperties": False,
    }
    result = ask_json(
        system_prompt="Extract all file references from the provided document. Return text files and image files as separate lists. Include only filenames, not full URLs.",
        user_message=index_content,
        schema=schema,
    )
    return result["text_files"], result["image_files"]


def fill_declaration(docs: str, images: list[tuple[str, str]]) -> str:
    """Asks LLM (with vision) to fill the declaration based on all docs."""
    system_prompt = load_prompt("system.md")
    shipment = load_data("shipment.md").format(date=date.today().isoformat())

    content = [
        {"type": "text", "text": f"SPK documentation:\n\n{docs}"},
    ]
    for filename, b64 in images:
        content.append({"type": "text", "text": f"\nImage attachment: {filename}"})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })
    content.append({"type": "text", "text": f"\n---\n{shipment}"})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
    )
    return response.choices[0].message.content.strip()


def main():
    # 1. Fetch index.md and extract file references via LLM
    print("=== Fetching index.md ===")
    index_content = fetch_doc("index.md")

    print("\n=== Extracting file list from index.md (LLM) ===")
    text_files, image_files = extract_file_lists(index_content)
    print(f"  Text files: {text_files}")
    print(f"  Image files: {image_files}")

    # 2. Fetch all referenced files
    print("\n=== Fetching documentation ===")
    all_docs = f"=== index.md ===\n{index_content}"
    for filename in text_files:
        content = fetch_doc(filename)
        all_docs += f"\n\n=== {filename} ===\n{content}"

    images = []
    for filename in image_files:
        b64 = fetch_image_b64(filename)
        images.append((filename, b64))

    # 3. Ask LLM to fill the declaration
    print("\n=== Generating declaration (LLM + vision) ===")
    declaration = fill_declaration(all_docs, images)
    print(declaration)

    # 4. Submit to Hub
    print("\n=== Submitting to Hub ===")
    result = verify("sendit", {"declaration": declaration})
    print(result)


if __name__ == "__main__":
    main()
