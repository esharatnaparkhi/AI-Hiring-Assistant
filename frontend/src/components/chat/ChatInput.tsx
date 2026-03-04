"use client";

import { useState, useRef, KeyboardEvent } from "react";
import { Send } from "lucide-react";
import VoiceButton from "./VoiceButton";

interface Props {
  onSend: (text: string) => void;
  isStreaming: boolean;
  voiceProps: {
    recording: boolean;
    transcribing: boolean;
    speaking: boolean;
    onToggle: () => void;
  };
  voiceModeEnabled: boolean;
}

export default function ChatInput({ onSend, isStreaming, voiceProps, voiceModeEnabled }: Props) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function submit() {
    const val = text.trim();
    if (!val || isStreaming) return;
    onSend(val);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function onKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function onInput() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }

  return (
    <div
      style={{
        position: "sticky",
        bottom: 0,
        paddingBottom: 20,
        paddingTop: 12,
        background: "var(--bg)",
      }}
    >
      <div
        className="mx-auto flex items-end gap-3 px-4 py-3"
        style={{
          maxWidth: 720,
          background: "var(--card-white)",
          borderRadius: "var(--radius-hero)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-card)",
        }}
      >
        {/* Voice button */}
        {voiceModeEnabled && (
          <VoiceButton {...voiceProps} />
        )}

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKey}
          onInput={onInput}
          placeholder={isStreaming ? "TalentScout is responding…" : "Type your response…"}
          disabled={isStreaming}
          style={{
            flex: 1,
            resize: "none",
            border: "none",
            outline: "none",
            background: "transparent",
            fontSize: "0.9rem",
            color: "var(--text-primary)",
            lineHeight: 1.55,
            padding: "4px 0",
            maxHeight: 180,
          }}
        />

        {/* Send button */}
        <button
          onClick={submit}
          disabled={!text.trim() || isStreaming}
          style={{
            width: 38,
            height: 38,
            borderRadius: "50%",
            border: "none",
            background: text.trim() && !isStreaming ? "var(--cta)" : "var(--border)",
            color: text.trim() && !isStreaming ? "#fff" : "var(--text-muted)",
            cursor: text.trim() && !isStreaming ? "pointer" : "not-allowed",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "background 0.15s",
            flexShrink: 0,
          }}
        >
          <Send size={16} />
        </button>
      </div>

      <p className="text-center mt-2" style={{ fontSize: "0.7rem", color: "var(--text-faint)" }}>
        Say <strong>done</strong> to finish the interview
      </p>
    </div>
  );
}
