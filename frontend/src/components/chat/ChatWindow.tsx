"use client";

import { useEffect, useRef } from "react";
import { ChatMessage } from "@/hooks/useChat";
import MessageBubble from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
}

export default function ChatWindow({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className="flex-1 overflow-y-auto"
      style={{ padding: "24px 0" }}
    >
      <div
        className="flex flex-col gap-4 mx-auto"
        style={{ maxWidth: 720 }}
      >
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
