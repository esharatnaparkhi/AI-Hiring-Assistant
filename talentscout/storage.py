import json
import os
import time
from typing import Any

from .config import DATA_PATH

os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def save_candidate(record: dict[str, Any]) -> None:
    """Append a candidate record to the JSONL store."""
    record = {**record, "stored_at": int(time.time())}
    with open(DATA_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_all_candidates() -> list[dict[str, Any]]:
    """Return all stored candidate records."""
    if not os.path.exists(DATA_PATH):
        return []
    records: list[dict] = []
    with open(DATA_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records
