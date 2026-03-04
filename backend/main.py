"""
TalentScout — FastAPI backend.

Run with:
    python3.11 -m uvicorn main:app --reload --port 8000
"""

import json

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from talentscout.conversation import InterviewSession
from talentscout.storage import upsert_session, get_session, list_sessions, delete_session
from talentscout.voice import VoiceClient
from talentscout.utils import new_session_id

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="TalentScout API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_sessions: dict[str, InterviewSession] = {}
_voice = VoiceClient()


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_session(session_id: str) -> InterviewSession:
    """Return in-memory session, loading from MongoDB if needed."""
    if session_id in _sessions:
        return _sessions[session_id]

    doc = await get_session(session_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session = InterviewSession.from_record(session_id, doc)
    _sessions[session_id] = session
    return session


def _snapshot(session: InterviewSession) -> dict:
    return {
        "session_id": session.session_id,
        "stage": session.stage,
        "stage_index": session.stage_index,
        "profile": session.profile.to_dict(),
        "profile_pct": session.profile.completeness_pct(),
        "is_complete": session.is_complete,
        "history": [{"role": m.role, "content": m.content} for m in session.history],
        "evaluation": session.evaluation,
        "improvements": session.improvements,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def health():
    return {"status": "ok", "service": "TalentScout API"}


@app.post("/api/sessions")
async def create_session():
    session_id = new_session_id()
    session = InterviewSession(session_id)
    greeting = await session.initialize()
    _sessions[session_id] = session
    await upsert_session(session.to_record())
    return {"session_id": session_id, "greeting": greeting}


@app.get("/api/sessions")
async def list_recent_sessions(limit: int = 20):
    records = await list_sessions(limit)
    return [
        {
            "session_id": r.get("session_id"),
            "name": (r.get("profile") or {}).get("full_name") or "Anonymous",
            "stage": r.get("stage", ""),
            "stored_at": r.get("stored_at"),
        }
        for r in records
    ]


@app.get("/api/sessions/{session_id}")
async def get_session_state(session_id: str):
    session = await _get_session(session_id)
    return _snapshot(session)


@app.delete("/api/sessions/{session_id}")
async def delete_session_route(session_id: str):
    deleted = await delete_session(session_id)
    _sessions.pop(session_id, None)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True}


# ── Chat (SSE streaming) ──────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


@app.post("/api/sessions/{session_id}/chat")
async def chat(session_id: str, req: ChatRequest):
    """
    Stream AI response tokens via Server-Sent Events.
    Each chunk: data: {"token": "...", "done": false}
    Final chunk: data: {"token": "", "done": true, "stage": "...", "profile": {...}}
    """
    session = await _get_session(session_id)

    async def event_stream():
        async for token, done, meta in session.process_message_stream(req.message):
            if done:
                await upsert_session(session.to_record())
                yield f"data: {json.dumps({'token': '', 'done': True, **meta})}\n\n"
            else:
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Voice ─────────────────────────────────────────────────────────────────────

@app.post("/api/sessions/{session_id}/transcribe")
async def transcribe(session_id: str, audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    text = await _voice.transcribe(audio_bytes, filename=audio.filename or "recording.wav")
    return {"text": text}


class SynthRequest(BaseModel):
    text: str


@app.post("/api/sessions/{session_id}/synthesize")
async def synthesize(session_id: str, req: SynthRequest):
    audio_bytes = await _voice.synthesize(req.text)
    if audio_bytes is None:
        raise HTTPException(status_code=503, detail="TTS not available — check ELEVENLABS_API_KEY")
    return Response(content=audio_bytes, media_type="audio/mpeg")


# ── Evaluation ────────────────────────────────────────────────────────────────

@app.get("/api/sessions/{session_id}/evaluation")
async def get_evaluation(session_id: str):
    session = await _get_session(session_id)
    return {
        "evaluation": session.evaluation,
        "improvements": session.improvements,
        "profile": session.profile.to_dict(),
    }
