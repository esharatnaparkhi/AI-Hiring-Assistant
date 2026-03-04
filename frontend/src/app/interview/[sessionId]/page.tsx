"use client";

import { useParams } from "next/navigation";
import { useEffect, useRef, useState, useCallback } from "react";
import { getSession, Profile } from "@/lib/api";
import { useChat, ChatMessage } from "@/hooks/useChat";
import { useVoice } from "@/hooks/useVoice";
import Sidebar from "@/components/layout/Sidebar";
import ContextPanel from "@/components/layout/ContextPanel";
import ChatWindow from "@/components/chat/ChatWindow";
import ChatInput from "@/components/chat/ChatInput";

const STAGES = ["Greeting", "Profile", "Technical", "Evaluation", "Complete"];

export default function InterviewPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  const [loading, setLoading] = useState(true);
  const [voiceMode, setVoiceMode] = useState(false);
  const [profile, setProfile] = useState<Profile>({ key_skills: [] });
  const [profilePct, setProfilePct] = useState(0);
  const [stageIndex, setStageIndex] = useState(0);
  const [stage, setStage] = useState("Greeting");
  const [isComplete, setIsComplete] = useState(false);
  const [evaluation, setEvaluation] = useState<Record<string, unknown> | undefined>();
  const [improvements, setImprovements] = useState<{ skill: string; score: number; advice: string }[]>([]);

  // Single chat hook instance
  const { messages, setMessages, meta, isStreaming, sendMessage } = useChat(sessionId, []);

  // Load session history on mount
  useEffect(() => {
    getSession(sessionId)
      .then((s) => {
        setProfile(s.profile);
        setProfilePct(s.profile_pct);
        setStageIndex(s.stage_index);
        setStage(s.stage);
        setIsComplete(s.is_complete);
        setEvaluation(s.evaluation as Record<string, unknown>);
        setImprovements(
          (s.improvements as { skill: string; score: number; advice: string }[]) ?? []
        );
        setMessages(
          s.history.map((m) => ({
            id: crypto.randomUUID(),
            role: m.role,
            content: m.content,
          }))
        );
      })
      .catch(() => {})
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  // Sync sidebar state from SSE metadata after each AI reply
  useEffect(() => {
    if (!meta) return;
    setProfile(meta.profile);
    setProfilePct(meta.profile_pct);
    setStage(meta.stage);
    const idx = STAGES.indexOf(meta.stage);
    if (idx >= 0) setStageIndex(idx);
    if (meta.stage === "Complete") {
      setIsComplete(true);
      if (meta.evaluation) setEvaluation(meta.evaluation as Record<string, unknown>);
      if (meta.improvements)
        setImprovements(meta.improvements as { skill: string; score: number; advice: string }[]);
    }
  }, [meta]);

  // Voice
  const voice = useVoice(sessionId);

  const handleVoiceToggle = useCallback(async () => {
    if (voice.recording) {
      const text = await voice.stopAndTranscribe();
      if (text) sendMessage(text);
    } else {
      await voice.startRecording();
    }
  }, [voice, sendMessage]);

  // Track which message has already been spoken so we never re-speak on token updates
  const lastSpokenIdRef = useRef<string | null>(null);

  // Auto-speak only the newly completed AI reply (not re-speak old ones during streaming)
  useEffect(() => {
    if (!voiceMode) return;
    // Find the latest assistant message that has finished streaming
    const last = [...messages].reverse().find((m) => m.role === "assistant" && !m.streaming && m.content);
    if (last && last.id !== lastSpokenIdRef.current) {
      lastSpokenIdRef.current = last.id;
      voice.speak(last.content);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages, voiceMode]);

  if (loading) {
    return (
      <div
        className="flex items-center justify-center min-h-screen"
        style={{ color: "var(--text-muted)" }}
      >
        Loading session…
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "var(--bg)" }}>
      {/* Left sidebar */}
      <Sidebar
        sessionId={sessionId}
        profile={profile}
        profilePct={profilePct}
        stageIndex={stageIndex}
        stage={stage}
      />

      {/* Center chat */}
      <main className="flex flex-col flex-1 overflow-hidden">
        {/* Top bar */}
        <div
          className="flex items-center justify-between px-8 py-3 flex-shrink-0"
          style={{
            borderBottom: "1px solid var(--border)",
            background: "rgba(255,255,255,0.7)",
            backdropFilter: "blur(8px)",
          }}
        >
          <h1 className="font-semibold text-sm" style={{ color: "var(--text-primary)" }}>
            {isComplete ? "Interview Complete ✅" : `Interview · ${stage}`}
          </h1>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            GPT-4o mini + ElevenLabs
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6">
          <ChatWindow messages={messages} />
        </div>

        {/* Input */}
        <div className="px-6">
          <ChatInput
            onSend={sendMessage}
            isStreaming={isStreaming}
            voiceModeEnabled={voiceMode}
            voiceProps={{
              recording: voice.recording,
              transcribing: voice.transcribing,
              speaking: voice.speaking,
              onToggle: handleVoiceToggle,
            }}
          />
        </div>
      </main>

      {/* Right context panel */}
      <ContextPanel
        stage={stage}
        sessionId={sessionId}
        voiceModeEnabled={voiceMode}
        onVoiceToggle={() => setVoiceMode((v) => !v)}
        evaluation={
          evaluation as {
            rank?: number;
            recommendation?: string;
            comments?: string;
            strengths?: string[];
            concerns?: string[];
          }
        }
        improvements={improvements}
        isComplete={isComplete}
      />
    </div>
  );
}
