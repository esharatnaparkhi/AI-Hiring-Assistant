# TalentScout — Technical Project Summary

## Architecture Overview

TalentScout is a full-stack AI interview platform split into two independently runnable services:

- **Backend** — FastAPI (Python 3.11) at `localhost:8000`
- **Frontend** — Next.js 14 (TypeScript) at `localhost:3000`

All communication is over HTTP. Chat uses Server-Sent Events (SSE) for token streaming; all other endpoints are standard JSON REST. MongoDB stores sessions asynchronously via the Motor driver.

---

## Project Structure

```
AI-Hiring-Assistant/
├── README.md
├── ProjectSummary.md
│
├── backend/
│   ├── main.py                        # FastAPI app + all route handlers
│   ├── requirements.txt
│   ├── .env                           # API keys + DB config (not committed)
│   └── talentscout/
│       ├── config.py                  # Env var loading + constants
│       ├── prompts.py                 # System prompt, evaluation prompt, improvement prompt
│       ├── llm.py                     # AsyncOpenAI client (chat, chat_stream, complete)
│       ├── voice.py                   # ElevenLabs STT + TTS client
│       ├── conversation.py            # InterviewSession state machine
│       ├── storage.py                 # Motor async MongoDB CRUD
│       └── utils.py                   # new_session_id(), is_end_signal()
│
└── frontend/
    ├── package.json
    ├── tailwind.config.ts
    └── src/
        ├── app/
        │   ├── layout.tsx             # Root layout + font
        │   ├── globals.css            # Design tokens (CSS variables) + base styles
        │   ├── page.tsx               # Dashboard home (bento grid)
        │   └── interview/
        │       └── [sessionId]/
        │           └── page.tsx       # 3-panel interview UI
        ├── components/
        │   ├── dashboard/
        │   │   └── BentoGrid.tsx      # Asymmetric CSS grid dashboard
        │   ├── layout/
        │   │   ├── Sidebar.tsx        # Left panel: progress, profile, recent sessions
        │   │   └── ContextPanel.tsx   # Right panel: stage, voice toggle, evaluation
        │   └── chat/
        │       ├── ChatWindow.tsx     # Scrollable message list
        │       ├── MessageBubble.tsx  # User / AI bubble variants
        │       ├── ChatInput.tsx      # Sticky input pill
        │       └── VoiceButton.tsx    # Record / stop / speaking indicator
        ├── hooks/
        │   ├── useChat.ts             # SSE streaming state machine
        │   └── useVoice.ts            # STT recording + TTS playback
        └── lib/
            └── api.ts                 # Typed fetch wrappers for all endpoints
```

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend framework | Next.js (App Router) | 14 | SSR, routing, React server components |
| UI library | React | 18 | Component model |
| Language | TypeScript | 5 | End-to-end type safety |
| Styling | Tailwind CSS | 3 | Utility-first CSS classes |
| Animations | Framer Motion | 12 | Card hover, message entry animations |
| Icons | Lucide React | 0.576 | UI icons (trash, mic, clock, etc.) |
| Backend framework | FastAPI | 0.111+ | Async REST API + SSE streaming |
| ASGI server | Uvicorn | 0.29+ | Production-grade async server |
| LLM | OpenAI GPT-4o-mini | API v1 | Interview conduction + evaluation |
| STT | ElevenLabs Scribe v1 | SDK 1.0+ | Audio → text transcription |
| TTS | ElevenLabs Multilingual v2 | SDK 1.0+ | Text → MP3 audio |
| Database | MongoDB | 7+ | Session document storage |
| DB driver | Motor | 3.4+ | Async MongoDB client for Python |
| File uploads | python-multipart | 0.0.9+ | Audio upload parsing in FastAPI |

---

## Interview State Machine

The core logic lives in `backend/talentscout/conversation.py` as the `InterviewSession` class.

### Stages

```
GREETING (0) → PROFILE (1) → TECHNICAL (2) → EVALUATION (3) → COMPLETE (4)
```

| Stage | Trigger to Advance | What Happens |
|---|---|---|
| **Greeting** | Always shown first | AI introduces itself, begins collecting profile |
| **Profile** | All required fields filled (`full_name`, `email`, `years_of_experience`, `key_skills`) | Transitions naturally mid-conversation |
| **Technical** | End-signal keyword detected (exit, done, quit, bye, stop) | AI asks 3–5 skill-adapted questions one at a time |
| **Evaluation** | Evaluation LLM calls complete | `asyncio.gather()` runs evaluation + improvement prompts concurrently |
| **Complete** | Post-evaluation | Session marked complete, timestamp recorded |

### Silent Profile Extraction

The AI is instructed to embed structured JSON inside its responses when it detects profile data:

```
```json
{"profile_update": {"full_name": "Jane Doe", "email": "jane@example.com", "key_skills": ["Python", "SQL"]}}
```
```

The backend uses two regex patterns to extract this before displaying the message:

```python
_JSON_BLOCK_RE   = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_INLINE_PROFILE  = re.compile(r'\{[^{}]*"profile_update"[^{}]*\}', re.DOTALL)
```

Extracted JSON is applied to `CandidateProfile` and stripped from the visible message. Candidates never see the structured data.

### Profile Completeness

```python
def completeness_pct(self) -> int:
    required = [self.full_name, self.email, self.years_of_experience]
    filled = sum(1 for f in required if f) + min(len(self.key_skills), 3)
    return min(int(filled / 6 * 100), 100)
```

The sidebar progress bar reflects this live as the AI collects data.

---

## Streaming Architecture

### Why SSE Instead of WebSockets

SSE is unidirectional (server → client), which is exactly the pattern needed for AI token streaming. It requires no handshake protocol, works over standard HTTP/1.1, and is natively supported by the browser `EventSource` API. Simpler and sufficient for this use case.

### Backend: Async Generator → StreamingResponse

```python
@app.post("/api/sessions/{session_id}/chat")
async def chat(session_id: str, req: ChatRequest):
    session = await _get_session(session_id)

    async def event_stream():
        async for token, done, meta in session.process_message_stream(req.message):
            if done:
                await upsert_session(session.to_record())
                yield f"data: {json.dumps({'token': '', 'done': True, **meta})}\n\n"
            else:
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

`process_message_stream()` is a public async generator on `InterviewSession`. It:
1. Appends the user message to history
2. Checks for end-signal keywords
3. Passes the full history to `LLMClient.chat_stream()`
4. Yields each token as `(token, done=False, {})`
5. On completion: extracts profile updates, strips JSON, advances stage
6. Yields final `("", done=True, meta)` with stage + profile + evaluation data

### Frontend: fetch + ReadableStream

The frontend avoids `EventSource` (which only supports GET) in favour of `fetch` with a `ReadableStream` reader — allowing a POST body:

```typescript
export function streamChat(sessionId, message, onToken, onDone): () => void {
  const ctrl = new AbortController();

  fetch(`${API}/api/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal: ctrl.signal,
  }).then(async (res) => {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      const lines = buf.split("\n");
      buf = lines.pop() ?? "";                  // keep incomplete line in buffer
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const obj = JSON.parse(line.slice(6).trim());
        obj.done ? onDone(obj) : onToken(obj.token ?? "");
      }
    }
  });

  return () => ctrl.abort();                    // cancel function
}
```

The incomplete-line buffer (`buf = lines.pop()`) handles TCP packet fragmentation — a chunk might arrive mid-line.

### SSE Payload Format

```
data: {"token": "Hello", "done": false}
data: {"token": " there", "done": false}
data: {"token": "", "done": true, "stage": "Profile", "profile": {...}, "profile_pct": 75}
```

The final `done: true` packet carries full metadata. On interview completion it also includes:

```json
{
  "done": true,
  "stage": "Complete",
  "profile": { ... },
  "evaluation": { "rank": 4, "recommendation": "hire", "comments": "...", "strengths": [...], "concerns": [...] },
  "improvements": [{ "skill": "SQL", "score": 5, "advice": "Practice window functions" }]
}
```

---

## Voice Pipeline

### Speech-to-Text (Transcription)

```
Browser MediaRecorder → WAV blob → POST /transcribe → ElevenLabs Scribe v1 → text
```

1. User clicks the mic button; `navigator.mediaDevices.getUserMedia({ audio: true })` opens the stream
2. `MediaRecorder` collects chunks; user clicks again to stop
3. Chunks assembled into a `Blob` and sent as `multipart/form-data`
4. Backend passes bytes to `ElevenLabs.speech_to_text.convert()` via `asyncio.to_thread()` (offloads blocking SDK call)
5. Transcribed text returned to frontend and auto-sent as a chat message

### Text-to-Speech (Synthesis)

```
AI reply text → POST /synthesize → ElevenLabs Multilingual v2 → MP3 bytes → Object URL → HTMLAudioElement
```

1. After streaming completes, `useEffect` in the interview page detects the new assistant message
2. `useRef` tracks the last-spoken message ID — prevents re-speaking the same message during streaming token updates
3. Backend calls `ElevenLabs.text_to_speech.convert()` → returns an audio generator → joined into `bytes`
4. Frontend receives MP3 as a blob, creates `URL.createObjectURL(blob)`, plays via `new Audio(url).play()`
5. Object URL revoked on `audio.onended` to prevent memory leaks

### Re-speak Prevention Bug Fix

During token streaming, the messages array updates on every token. A naive `useEffect` on `messages` would find the previous completed assistant message (because the current one is `streaming: true`) and re-speak it on every token.

Fix: a `useRef<string | null>` stores the ID of the last spoken message. The effect only calls `voice.speak()` when `last.id !== lastSpokenIdRef.current`.

---

## Latency Optimizations

### 1. Streaming First Token Fast

The LLM client uses `stream=True` from the first call — the frontend receives and renders the first token typically within 200–500ms of the request, before the full reply is ready. Users perceive the response as instant.

### 2. Concurrent Evaluation Calls

When the interview closes, two separate LLM calls are needed (evaluation + improvement). These run in parallel:

```python
eval_raw, impr_raw = await asyncio.gather(
    self._llm.complete(eval_prompt),
    self._llm.complete(impr_prompt),
)
```

This halves evaluation latency compared to sequential calls.

### 3. In-Memory Session Cache

```python
_sessions: dict[str, InterviewSession] = {}
```

Session objects are kept in process memory after first load. Subsequent requests skip MongoDB entirely for active sessions — reducing per-message overhead to zero DB reads.

Sessions are only written to MongoDB (upserted) at the end of each streamed reply, not on every token.

### 4. `asyncio.to_thread` for Blocking SDK Calls

ElevenLabs SDK calls are synchronous. Wrapping them in `asyncio.to_thread()` offloads to a thread pool, preventing the event loop from blocking during STT/TTS calls:

```python
result = await asyncio.to_thread(
    self._client.speech_to_text.convert,
    file=audio_file,
    model_id=ELEVENLABS_STT_MODEL,
)
```

### 5. Low-Temperature LLM Settings

`temperature=0.3` for chat (interview consistency), `temperature=0.1` for evaluation (deterministic scoring). Lower temperatures reduce the chance of long, meandering responses, keeping token count low and latency tight.

### 6. `max_tokens` Limits

Interview messages capped at `max_tokens=512`; evaluation at `max_tokens=800`. Prevents runaway long responses and controls cost.

---

## MongoDB Schema

**Collection:** `sessions`

```json
{
  "_id": "ObjectId",
  "session_id": "uuid-v4-string",
  "stage": "Greeting | Profile | Technical | Evaluation | Complete",
  "profile": {
    "full_name": "string | null",
    "email": "string | null",
    "phone": "string | null",
    "years_of_experience": "string | null",
    "location": "string | null",
    "desired_role": "string | null",
    "key_skills": ["string"],
    "evaluation": {
      "rank": "1–5",
      "recommendation": "hire | maybe | no_hire",
      "comments": "string",
      "strengths": ["string"],
      "concerns": ["string"]
    }
  },
  "improvements": [
    { "skill": "string", "score": "0–10", "advice": "string" }
  ],
  "history": [
    ["user", "message content"],
    ["assistant", "message content"]
  ],
  "is_complete": "boolean",
  "ended_at": "unix timestamp | null",
  "stored_at": "unix timestamp"
}
```

**Indexes used:**
- `session_id` — unique, used for upsert and lookup
- `stored_at` — descending sort for `list_sessions()`

**Storage operations** (`storage.py`):

| Function | Operation | Notes |
|---|---|---|
| `upsert_session(record)` | `update_one` with `upsert=True` | Called after every streamed reply |
| `get_session(session_id)` | `find_one` | Cache miss fallback |
| `list_sessions(limit)` | `find().sort().limit()` | Dashboard + sidebar |
| `delete_session(session_id)` | `delete_one` | Also clears in-memory cache |

---

## API Reference

### Session Routes

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/sessions` | — | `{session_id, greeting}` |
| `GET` | `/api/sessions?limit=N` | — | `[{session_id, name, stage, stored_at}]` |
| `GET` | `/api/sessions/{id}` | — | Full session state |
| `DELETE` | `/api/sessions/{id}` | — | `{deleted: true}` |

### Chat

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/sessions/{id}/chat` | `{message: string}` | SSE token stream |

### Voice

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/sessions/{id}/transcribe` | `multipart/form-data` (audio file) | `{text: string}` |
| `POST` | `/api/sessions/{id}/synthesize` | `{text: string}` | `audio/mpeg` bytes |

### Evaluation

| Method | Path | Response |
|---|---|---|
| `GET` | `/api/sessions/{id}/evaluation` | `{evaluation, improvements, profile}` |

---

## Frontend State Management

State is managed entirely with React hooks — no external store (no Redux, no Zustand).

### useChat

```
sendMessage(text)
    │
    ├─ Append user message to messages[]
    ├─ Append empty assistant placeholder {streaming: true}
    ├─ Call streamChat() → returns cancel fn stored in ref
    │       │
    │       ├─ onToken(token)  → append token to last message
    │       └─ onDone(meta)    → set streaming=false, update meta state
    │
    └─ meta state triggers useEffect in page.tsx
           └─ Updates: profile, stage, stageIndex, evaluation, improvements
```

### State Sync on Mount vs SSE

| Source | When | Populates |
|---|---|---|
| `getSession()` on mount | Page load / refresh | Full history, profile, stage, evaluation |
| SSE `done` metadata | After each AI reply | Live stage, profile progress, evaluation on complete |

This dual-sync means the page correctly restores full state on refresh while also updating reactively during a live session.

---

## Design System

Defined entirely in `src/app/globals.css` as CSS custom properties.

### Color Tokens

| Variable | Value | Used For |
|---|---|---|
| `--bg` | `#F5F6F8` | Page background |
| `--bg-sidebar` | `#FAFAFA` | Sidebar background |
| `--bg-panel` | `#F8F8FB` | Context panel background |
| `--card-lavender` | `#EDE9FE` | Hero card, active highlights |
| `--card-blue` | `#DBEAFE` | Voice card, info highlights |
| `--card-pink` | `#FCE7F3` | Stats card, accent |
| `--card-white` | `#FFFFFF` | Chat area, sidebar cards |
| `--cta` | `#0F172A` | Primary button background |
| `--border` | `#E2E8F0` | All card and section borders |
| `--text-primary` | `#0F172A` | Headings, body copy |
| `--text-muted` | `#64748B` | Labels, secondary text |
| `--text-faint` | `#CBD5E1` | Placeholders, hints |

### Visual Language

- **Border radius:** `--radius-card: 20px` / `--radius-hero: 28px`
- **Shadows:** `0 2px 16px rgba(0,0,0,0.06)` resting, `0 8px 32px rgba(0,0,0,0.10)` hover
- **Glassmorphism:** `backdrop-filter: blur(12px)` + `rgba(255,255,255,0.7)` on nav/topbar
- **Framer Motion:** `scale(1.015)` on card hover, `y: 16px → 0` entry animations with stagger

---

## System Prompts

Three distinct prompts in `prompts.py`:

### SYSTEM_PROMPT (Interview Conductor)
Instructs the AI to: conduct a 3-phase interview (greeting → profile → technical), collect profile fields naturally, embed silent `{"profile_update": {...}}` JSON in replies, ask technical questions one at a time adapted to experience level, follow up on vague answers, and close gracefully on end signals. Keeps responses to 2–4 sentences.

### EVALUATION_PROMPT
One-shot prompt with full profile + transcript. Returns structured JSON:
```json
{"rank": 4, "recommendation": "hire", "comments": "...", "strengths": [...], "concerns": [...]}
```

### IMPROVEMENT_PROMPT
One-shot prompt focused on skill gaps. Returns:
```json
{"improvements": [{"skill": "Docker", "score": 4, "advice": "Practice multi-stage builds"}]}
```

Both evaluation prompts use `temperature=0.1` for deterministic, consistent scoring.
