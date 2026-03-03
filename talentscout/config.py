import os
from dotenv import load_dotenv

load_dotenv()

# ── OpenAI (LLM) ──────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── ElevenLabs (STT + TTS) ────────────────────────────────────────────────────
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel
ELEVENLABS_TTS_MODEL: str = "eleven_multilingual_v2"
ELEVENLABS_STT_MODEL: str = "scribe_v1"

# ── Storage ───────────────────────────────────────────────────────────────────
DATA_PATH: str = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "candidates.jsonl"
)

# ── Interview Settings ─────────────────────────────────────────────────────────
MIN_TECH_QUESTIONS: int = 3
MAX_TECH_QUESTIONS: int = 5
