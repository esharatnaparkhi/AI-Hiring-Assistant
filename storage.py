import json, hashlib, time, os
from typing import Dict, Any

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "candidates.jsonl")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

def hash_candidate(record: Dict[str, Any]) -> None:
    safe = dict(record)
    safe["stored_at"] = int(time.time())
    with open(DATA_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(safe, ensure_ascii=False) + "\n")


