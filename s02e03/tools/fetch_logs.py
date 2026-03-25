import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from pathlib import Path
from shared.hub_client import get_data, HUB_KEY

DATA_DIR = Path(__file__).parent.parent / "data"
LOG_FILE = DATA_DIR / "failure.log"
LOG_URL = f"/data/{HUB_KEY}/failure.log"

SEVERITY_LEVELS = {"CRIT", "ERRO", "WARN", "INFO", "DEBUG"}


def download_logs() -> Path:
    """Download failure.log and cache it in data/. Returns path to local file."""
    DATA_DIR.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        print("Downloading failure.log...")
        resp = get_data(LOG_URL)
        resp.raise_for_status()
        LOG_FILE.write_bytes(resp.content)
        print(f"Saved to {LOG_FILE} ({LOG_FILE.stat().st_size} bytes)")
    else:
        print(f"Using cached {LOG_FILE} ({LOG_FILE.stat().st_size} bytes)")
    return LOG_FILE


def search_logs(keywords: list[str] = None, severities: list[str] = None) -> list[str]:
    """
    Filter log lines by keywords (case-insensitive OR match) and/or severity levels.
    Returns matching lines as a list of strings.
    """
    download_logs()
    lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()

    results = []
    kw_lower = [k.lower() for k in keywords] if keywords else []
    sev_set = set(s.upper() for s in severities) if severities else None

    for line in lines:
        line_lower = line.lower()

        if sev_set:
            matched_sev = any(f"[{s}]" in line for s in sev_set)
            if not matched_sev:
                continue

        if kw_lower:
            matched_kw = any(kw in line_lower for kw in kw_lower)
            if not matched_kw:
                continue

        results.append(line)

    return results


def log_stats() -> dict:
    """Return basic stats: total lines, lines per severity level."""
    download_logs()
    lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    stats = {"total_lines": len(lines)}
    for level in SEVERITY_LEVELS:
        stats[level] = sum(1 for l in lines if f"[{level}]" in l)
    return stats


def schema() -> dict:
    return {
        "name": "search_logs",
        "description": (
            "Search the power plant failure log file. Filter by severity levels "
            "(CRIT, ERRO, WARN, INFO) and/or keywords. Returns matching log lines. "
            "Use keywords to narrow results — avoid fetching hundreds of lines at once."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Case-insensitive keywords to filter lines (OR logic). E.g. ['pump', 'coolant', 'reactor']",
                },
                "severities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Severity levels to include. E.g. ['CRIT', 'ERRO', 'WARN']",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of lines to return (default: 100). Use smaller values to avoid overloading context.",
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    }


def run(keywords=None, severities=None, limit=100) -> dict:
    lines = search_logs(keywords=keywords, severities=severities)
    truncated = len(lines) > limit
    return {
        "total_matched": len(lines),
        "returned": min(len(lines), limit),
        "truncated": truncated,
        "lines": lines[:limit],
    }
