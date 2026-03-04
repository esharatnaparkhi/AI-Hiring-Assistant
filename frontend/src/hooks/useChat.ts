"use client";

import { useState, useCallback, useRef } from "react";
import { streamChat, Profile } from "@/lib/api";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

interface ChatMeta {
  stage: string;
  profile: Profile;
  profile_pct: number;
  evaluation?: Record<string, unknown>;
  improvements?: unknown[];
}

export function useChat(sessionId: string, initialMessages: ChatMessage[] = []) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [meta, setMeta] = useState<ChatMeta | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const cancelRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(
    (text: string) => {
      if (isStreaming) return;

      const userId = crypto.randomUUID();
      const aiId = crypto.randomUUID();

      // Append user message + empty streaming AI placeholder
      setMessages((prev) => [
        ...prev,
        { id: userId, role: "user", content: text },
        { id: aiId, role: "assistant", content: "", streaming: true },
      ]);
      setIsStreaming(true);

      cancelRef.current = streamChat(
        sessionId,
        text,
        (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiId ? { ...m, content: m.content + token } : m
            )
          );
        },
        (doneMeta) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiId ? { ...m, streaming: false } : m
            )
          );
          setMeta({
            stage: doneMeta.stage as string,
            profile: doneMeta.profile as Profile,
            profile_pct: doneMeta.profile_pct as number ?? 0,
            evaluation: doneMeta.evaluation as Record<string, unknown>,
            improvements: doneMeta.improvements as unknown[],
          });
          setIsStreaming(false);
        }
      );
    },
    [sessionId, isStreaming]
  );

  const cancel = useCallback(() => {
    cancelRef.current?.();
    setIsStreaming(false);
    setMessages((prev) =>
      prev.map((m) => (m.streaming ? { ...m, streaming: false } : m))
    );
  }, []);

  return { messages, setMessages, meta, isStreaming, sendMessage, cancel };
}
