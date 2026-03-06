# TalentScout — AI Hiring Assistant

TalentScout is an AI-powered interview platform that conducts structured job interviews autonomously. It collects candidate profiles through natural conversation, asks tailored technical questions, and delivers a complete evaluation report — all in real time.

---

## What It Does

A recruiter opens TalentScout and starts an interview session. The AI greets the candidate, naturally collects their details (name, email, experience, skills), then asks 3–5 technical questions adapted to their skill level. When the candidate says they're done, TalentScout generates a ranked evaluation with hiring recommendation, strengths, concerns, and a skill-gap breakdown — instantly available in the UI.

**Candidate experience:**
1. Receives a warm greeting and a brief overview of the process
2. Shares their background in a free-form conversation (not a form)
3. Answers 3–5 technical questions, one at a time, at their pace
4. Gets a graceful sign-off when the interview closes

**Recruiter output:**
- Rank score (1–5)
- Hire / Maybe / No Hire recommendation
- Written comments, strengths, and concerns
- Skill-gap analysis with proficiency scores and actionable advice
- Full session history persisted in MongoDB

---

## Features

- **Real-time token streaming** — AI responses appear word-by-word via SSE
- **Voice mode** — candidates can speak their answers and hear AI responses (ElevenLabs STT + TTS)
- **Automatic profile extraction** — the AI silently parses structured JSON from its own replies; candidates never see it
- **Stage-aware state machine** — Greeting → Profile → Technical → Evaluation → Complete
- **Session persistence** — all sessions stored in MongoDB; resume or review any past interview
- **Bento dashboard** — home page shows recent sessions, completed count, and a one-click "Start Interview" button
- **3-panel interview UI** — sidebar (progress + profile), chat center, context panel (evaluation results)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.11, Uvicorn |
| LLM | OpenAI GPT-4o-mini (streaming) |
| Voice | ElevenLabs Scribe (STT) + Multilingual v2 (TTS) |
| Database | MongoDB + Motor (async) |
| Streaming | Server-Sent Events (SSE) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB running locally (`brew services start mongodb-community`)

### Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=talentscout
```

```bash
python3.11 -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Interview Flow

```
Start Interview
     │
     ▼
  Greeting ──► Profile Collection ──► Technical Questions ──► Evaluation ──► Complete
                (name, email,           (3–5 questions,          (rank, rec,
                 skills, exp)            skill-adapted)            skill gaps)
```

The interview ends automatically when the candidate says `done`, `exit`, `quit`, `bye`, or `stop`.

---
