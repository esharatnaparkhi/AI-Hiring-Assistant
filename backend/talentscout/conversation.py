"""
Interview state machine.

Stages: GREETING → PROFILE → TECHNICAL → EVALUATION → COMPLETE
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from typing import Optional

from .llm import LLMClient
from .prompts import EVALUATION_PROMPT, IMPROVEMENT_PROMPT
from .utils import is_end_signal


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class Message:
    role: str   # "user" | "assistant"
    content: str


@dataclass
class CandidateProfile:
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    years_of_experience: Optional[str] = None
    location: Optional[str] = None
    desired_role: Optional[str] = None
    key_skills: list = field(default_factory=list)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def is_complete(self) -> bool:
        return bool(
            self.full_name and self.email and self.years_of_experience and self.key_skills
        )

    def completeness_pct(self) -> int:
        tracked = [
            self.full_name,
            self.email,
            self.phone,
            self.years_of_experience,
            self.location,
            self.key_skills,
        ]
        filled = sum(1 for f in tracked if f)
        return int((filled / len(tracked)) * 100)

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "years_of_experience": self.years_of_experience,
            "location": self.location,
            "desired_role": self.desired_role,
            "key_skills": self.key_skills,
        }


# ── Interview Session ─────────────────────────────────────────────────────────

_STAGES = ["Greeting", "Profile", "Technical", "Evaluation", "Complete"]

_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_INLINE_PROFILE_RE = re.compile(r'\{[^{}]*"profile_update"[^{}]*\}', re.DOTALL)


class InterviewSession:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.history: list[Message] = []
        self.profile = CandidateProfile()
        self.evaluation: dict = {}
        self.improvements: list[dict] = []
        self.is_complete: bool = False
        self._stage_idx: int = 0
        self._llm = LLMClient()
        self._initialized: bool = False
        self._ended_at: Optional[int] = None

    # ── Stage helpers ─────────────────────────────────────────────────────────

    @property
    def stage(self) -> str:
        return _STAGES[self._stage_idx]

    @property
    def stage_index(self) -> int:
        return self._stage_idx

    @property
    def stage_progress(self) -> float:
        """0.0 – 1.0 progress through all stages."""
        return self._stage_idx / (len(_STAGES) - 1)

    # ── Public API ────────────────────────────────────────────────────────────

    async def initialize(self) -> str:
        """Return the opening greeting from the AI (called once)."""
        if self._initialized:
            return self.history[0].content if self.history else ""

        self._initialized = True
        greeting = await self._llm.chat([
            {
                "role": "user",
                "content": (
                    "Start the interview. Greet the candidate warmly and begin collecting their information."
                ),
            }
        ])
        clean = self._strip_json(greeting)
        self.history.append(Message("assistant", clean))
        self._stage_idx = 1  # move to PROFILE
        return clean

    async def process_message(self, user_text: str) -> str:
        """Handle a user message and return the AI reply."""
        self.history.append(Message("user", user_text))

        # End-of-interview signal
        if is_end_signal(user_text) and self._stage_idx >= 2:
            return await self._close_interview()

        # Build full message list for LLM
        messages = [{"role": m.role, "content": m.content} for m in self.history]
        raw = await self._llm.chat(messages)

        # Extract and apply any profile update embedded in the response
        updates = self._extract_profile_update(raw)
        if updates:
            self._apply_profile(updates)
            if self.profile.is_complete() and self._stage_idx < 2:
                self._stage_idx = 2  # advance to TECHNICAL

        clean = self._strip_json(raw)
        self.history.append(Message("assistant", clean))
        return clean

    # ── Private helpers ───────────────────────────────────────────────────────

    def _extract_profile_update(self, text: str) -> dict:
        m = _JSON_BLOCK_RE.search(text)
        if not m:
            m = _INLINE_PROFILE_RE.search(text)
        if m:
            raw_json = m.group(1) if "```" in m.group(0) else m.group(0)
            try:
                data = json.loads(raw_json)
                return data.get("profile_update", {})
            except json.JSONDecodeError:
                pass
        return {}

    def _apply_profile(self, updates: dict) -> None:
        for key, value in updates.items():
            if value is not None and hasattr(self.profile, key):
                setattr(self.profile, key, value)

    def _strip_json(self, text: str) -> str:
        """Remove embedded JSON blocks from the displayed message."""
        text = _JSON_BLOCK_RE.sub("", text)
        text = _INLINE_PROFILE_RE.sub("", text)
        return text.strip()

    async def _close_interview(self) -> str:
        self._stage_idx = 3  # EVALUATION
        await self._evaluate()
        self._stage_idx = 4  # COMPLETE
        self.is_complete = True
        self._ended_at = int(time.time())

        farewell = (
            "Thank you for your time today! Your interview has been recorded and our "
            "team will review your responses carefully. Best of luck! 🌟"
        )
        self.history.append(Message("assistant", farewell))
        return farewell

    async def _evaluate(self) -> None:
        transcript = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in self.history
        )
        eval_prompt = EVALUATION_PROMPT.format(
            profile=json.dumps(self.profile.to_dict(), ensure_ascii=False),
            history=transcript,
        )
        improve_prompt = IMPROVEMENT_PROMPT.format(
            skills=", ".join(self.profile.key_skills) or "Not specified",
            history=transcript,
        )

        # Run both LLM calls concurrently
        eval_raw, improve_raw = await asyncio.gather(
            self._llm.complete(eval_prompt),
            self._llm.complete(improve_prompt),
        )

        self.evaluation = self._parse_json_block(eval_raw) or {"rank": 3, "comments": eval_raw[:300]}
        improve_data = self._parse_json_block(improve_raw) or {}
        self.improvements = improve_data.get("improvements", [])

    @staticmethod
    def _parse_json_block(text: str) -> Optional[dict]:
        m = _JSON_BLOCK_RE.search(text)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        return None

    async def process_message_stream(self, user_text: str):
        """
        Public async generator for SSE streaming.
        Yields (token: str, done: bool, meta: dict).
        meta is populated only on the final (done=True) yield.
        """
        self.history.append(Message("user", user_text))

        if is_end_signal(user_text) and self._stage_idx >= 2:
            reply = await self._close_interview()
            for word in reply.split(" "):
                yield word + " ", False, {}
                await asyncio.sleep(0.03)
            yield "", True, {
                "stage": self.stage,
                "profile": self.profile.to_dict(),
                "profile_pct": self.profile.completeness_pct(),
                "evaluation": self.evaluation,
                "improvements": self.improvements,
            }
            return

        messages = [{"role": m.role, "content": m.content} for m in self.history]
        full_reply = ""
        async for token in self._llm.chat_stream(messages):
            full_reply += token
            yield token, False, {}

        updates = self._extract_profile_update(full_reply)
        if updates:
            self._apply_profile(updates)
            if self.profile.is_complete() and self._stage_idx < 2:
                self._stage_idx = 2

        clean = self._strip_json(full_reply)
        self.history.append(Message("assistant", clean))

        yield "", True, {
            "stage": self.stage,
            "profile": self.profile.to_dict(),
            "profile_pct": self.profile.completeness_pct(),
        }

    # ── Class-method constructor ───────────────────────────────────────────────

    @classmethod
    def from_record(cls, session_id: str, doc: dict) -> "InterviewSession":
        """Reconstruct a session from a stored MongoDB document."""
        session = cls(session_id)
        for role, content in doc.get("history", []):
            session.history.append(Message(role, content))
        p = doc.get("profile", {})
        session.profile = CandidateProfile(
            full_name=p.get("full_name"),
            email=p.get("email"),
            phone=p.get("phone"),
            years_of_experience=p.get("years_of_experience"),
            location=p.get("location"),
            desired_role=p.get("desired_role"),
            key_skills=p.get("key_skills", []),
        )
        session.evaluation = p.get("evaluation", {})
        session.improvements = doc.get("improvements", [])
        session.is_complete = doc.get("stage", "") == "Complete"
        session._initialized = True
        return session

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_record(self) -> dict:
        return {
            "session_id": self.session_id,
            "stage": self.stage,
            "profile": {**self.profile.to_dict(), "evaluation": self.evaluation},
            "improvements": self.improvements,
            "history": [[m.role, m.content] for m in self.history],
            "ended_at": self._ended_at or int(time.time()),
        }
