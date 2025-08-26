import uuid, re

END_KEYWORDS = {"exit", "quit", "done", "bye", "stop"}

def is_end_signal(text: str) -> bool:
    t = (text or "").strip().lower()
    return any(k in t.split() for k in END_KEYWORDS)

def new_session_id() -> str:
    return str(uuid.uuid4())

