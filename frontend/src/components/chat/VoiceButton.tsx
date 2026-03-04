"use client";

import { Mic, MicOff, Loader2, Volume2 } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  recording: boolean;
  transcribing: boolean;
  speaking: boolean;
  onToggle: () => void;
}

export default function VoiceButton({ recording, transcribing, speaking, onToggle }: Props) {
  const busy = transcribing || speaking;

  const icon = transcribing
    ? <Loader2 size={18} className="animate-spin" />
    : speaking
    ? <Volume2 size={18} />
    : recording
    ? <MicOff size={18} />
    : <Mic size={18} />;

  const label = transcribing
    ? "Transcribing…"
    : speaking
    ? "Speaking…"
    : recording
    ? "Stop"
    : "Speak";

  return (
    <motion.button
      onClick={onToggle}
      disabled={busy}
      whileTap={{ scale: 0.95 }}
      title={label}
      style={{
        width: 42,
        height: 42,
        borderRadius: "50%",
        border: "none",
        cursor: busy ? "not-allowed" : "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: recording
          ? "#EF4444"
          : busy
          ? "var(--border)"
          : "var(--card-blue)",
        color: recording ? "#fff" : busy ? "var(--text-muted)" : "#2563EB",
        transition: "background 0.15s",
        flexShrink: 0,
      }}
    >
      {icon}
    </motion.button>
  );
}
