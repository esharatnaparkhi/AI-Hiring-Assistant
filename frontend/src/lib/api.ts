const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SessionSummary {
  session_id: string;
  name: string;
  stage: string;
  stored_at: number;
}

export interface Profile {
  full_name?: string;
  email?: string;
  phone?: string;
  years_of_experience?: string;
  location?: string;
  desired_role?: string;
  key_skills: string[];
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface SessionState {
  session_id: string;
  stage: string;
  stage_index: number;
  profile: Profile;
  profile_pct: number;
  is_complete: boolean;
  history: Message[];
  evaluation: Record<string, unknown>;
  improvements: { skill: string; score: number; advice: string }[];
}

export interface Evaluation {
  evaluation: {
    rank?: number;
    recommendation?: string;
    comments?: string;
    strengths?: string[];
    concerns?: string[];
  };
  improvements: { skill: string; score: number; advice: string }[];
  profile: Profile;
}

// ── API helpers ───────────────────────────────────────────────────────────────

export async function createSession(): Promise<{ session_id: string; greeting: string }> {
  const res = await fetch(`${API}/api/sessions`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to create session");
  return res.json();
}

export async function listSessions(limit = 20): Promise<SessionSummary[]> {
  const res = await fetch(`${API}/api/sessions?limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionState> {
  const res = await fetch(`${API}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error("Session not found");
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<boolean> {
  const res = await fetch(`${API}/api/sessions/${sessionId}`, { method: "DELETE" });
  return res.ok;
}

export async function getEvaluation(sessionId: string): Promise<Evaluation> {
  const res = await fetch(`${API}/api/sessions/${sessionId}/evaluation`);
  if (!res.ok) throw new Error("Evaluation not found");
  return res.json();
}

export async function transcribeAudio(sessionId: string, blob: Blob): Promise<string> {
  const form = new FormData();
  form.append("audio", blob, "recording.wav");
  const res = await fetch(`${API}/api/sessions/${sessionId}/transcribe`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) return "";
  const data = await res.json();
  return data.text ?? "";
}

export async function synthesizeSpeech(sessionId: string, text: string): Promise<string | null> {
  const res = await fetch(`${API}/api/sessions/${sessionId}/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) return null;
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

/**
 * Open an SSE stream for a chat message. Calls onToken for each streamed
 * token and onDone with final metadata when the stream ends.
 */
export function streamChat(
  sessionId: string,
  message: string,
  onToken: (token: string) => void,
  onDone: (meta: Record<string, unknown>) => void,
): () => void {
  const ctrl = new AbortController();

  fetch(`${API}/api/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal: ctrl.signal,
  }).then(async (res) => {
    if (!res.body) return;
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      // Parse complete SSE lines
      const lines = buf.split("\n");
      buf = lines.pop() ?? "";
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const payload = line.slice(6).trim();
        if (!payload) continue;
        try {
          const obj = JSON.parse(payload);
          if (obj.done) {
            onDone(obj);
          } else {
            onToken(obj.token ?? "");
          }
        } catch {
          /* ignore malformed chunk */
        }
      }
    }
  }).catch(() => { /* aborted */ });

  return () => ctrl.abort();
}
