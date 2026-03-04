"use client";

import { motion } from "framer-motion";
import { ChatMessage } from "@/hooks/useChat";

interface Props {
  message: ChatMessage;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <motion.div
      className={`flex ${isUser ? "justify-end" : "justify-start"} items-end gap-2`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Avatar — AI only */}
      {!isUser && (
        <div
          className="flex-shrink-0 flex items-center justify-center rounded-full text-white text-xs font-bold"
          style={{
            width: 32,
            height: 32,
            background: "linear-gradient(135deg, #7C3AED, #2563EB)",
          }}
        >
          AI
        </div>
      )}

      {/* Bubble */}
      <div
        style={{
          maxWidth: 600,
          padding: "12px 18px",
          borderRadius: isUser ? "20px 20px 6px 20px" : "20px 20px 20px 6px",
          background: isUser ? "var(--cta)" : "var(--card-white)",
          color: isUser ? "#fff" : "var(--text-primary)",
          border: isUser ? "none" : "1px solid var(--border)",
          boxShadow: "var(--shadow-sm)",
          fontSize: "0.9rem",
          lineHeight: 1.6,
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}
        className={message.streaming ? "cursor" : ""}
      >
        {message.content || (message.streaming ? "" : "—")}
      </div>
    </motion.div>
  );
}
