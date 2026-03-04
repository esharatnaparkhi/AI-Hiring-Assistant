import uuid

END_KEYWORDS = {"exit", "quit", "done", "bye", "stop", "goodbye", "end"}


def is_end_signal(text: str) -> bool:
    """Return True if the user's message signals the end of the interview."""
    words = (text or "").strip().lower().split()
    return any(k in words for k in END_KEYWORDS)


def new_session_id() -> str:
    return str(uuid.uuid4())


def run_async(coro):
    """Run an async coroutine from synchronous Streamlit context."""
    import asyncio
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Fallback: create a fresh loop (handles some edge cases)
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
