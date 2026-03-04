"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Mic, MessageSquare, Clock, BarChart2, ArrowRight, Sparkles, Trash2 } from "lucide-react";
import { createSession, listSessions, deleteSession, SessionSummary } from "@/lib/api";
import { useEffect, useState } from "react";

const fadeUp = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function BentoGrid() {
  const router = useRouter();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    listSessions().then(setSessions).catch(() => {});
  }, []);

  async function handleStart() {
    setStarting(true);
    try {
      const { session_id } = await createSession();
      router.push(`/interview/${session_id}`);
    } finally {
      setStarting(false);
    }
  }

  const completedCount = sessions.filter((s) => s.stage === "Complete").length;

  return (
    <motion.div
      className="grid gap-4"
      style={{
        gridTemplateColumns: "2fr 1fr 1fr",
        gridTemplateRows: "auto auto",
      }}
      variants={{ show: { transition: { staggerChildren: 0.07 } } }}
      initial="hidden"
      animate="show"
    >
      {/* ── Hero card ──────────────────────────────────────────────────────── */}
      <motion.div
        variants={fadeUp}
        className="card p-8 flex flex-col justify-between"
        style={{
          background: "var(--card-lavender)",
          borderRadius: "var(--radius-hero)",
          gridRow: "1 / 3",
          minHeight: 340,
        }}
      >
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Sparkles size={18} style={{ color: "#7C3AED" }} />
            <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: "#7C3AED" }}>
              AI Interview
            </span>
          </div>
          <h1
            className="font-bold leading-tight mb-3"
            style={{ fontSize: "2rem", color: "var(--text-primary)" }}
          >
            Ready for your next hire?
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", maxWidth: 320 }}>
            TalentScout conducts structured AI interviews with real-time voice support,
            profile extraction, and automated evaluation.
          </p>
        </div>

        <button
          className="btn-primary self-start mt-6"
          onClick={handleStart}
          disabled={starting}
        >
          {starting ? "Starting…" : "Start Interview"}
          <ArrowRight size={16} />
        </button>
      </motion.div>

      {/* ── Voice card ─────────────────────────────────────────────────────── */}
      <motion.div
        variants={fadeUp}
        className="card p-6 flex flex-col gap-3"
        style={{ background: "var(--card-blue)" }}
      >
        <div
          className="flex items-center justify-center rounded-2xl"
          style={{ width: 44, height: 44, background: "rgba(37,99,235,0.12)" }}
        >
          <Mic size={20} style={{ color: "#2563EB" }} />
        </div>
        <p className="font-semibold" style={{ color: "var(--text-primary)" }}>Voice Mode</p>
        <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Speak naturally — TalentScout AI transcribes your answers and responds with voice.
        </p>
      </motion.div>

      {/* ── Stats card ─────────────────────────────────────────────────────── */}
      <motion.div
        variants={fadeUp}
        className="card p-6 flex flex-col justify-between"
        style={{ background: "var(--card-pink)" }}
      >
        <div className="flex items-center justify-between">
          <BarChart2 size={20} style={{ color: "#BE185D" }} />
          <span className="text-xs font-medium" style={{ color: "#BE185D" }}>Completed</span>
        </div>
        <div>
          <p className="font-bold" style={{ fontSize: "2.4rem", color: "var(--text-primary)", lineHeight: 1 }}>
            {completedCount}
          </p>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: 4 }}>interviews finished</p>
        </div>
      </motion.div>

      {/* ── Recent sessions ─────────────────────────────────────────────────── */}
      <motion.div
        variants={fadeUp}
        className="card p-6"
        style={{ background: "var(--card-white)", gridColumn: "2 / 4" }}
      >
        <div className="flex items-center gap-2 mb-4">
          <Clock size={16} style={{ color: "var(--text-muted)" }} />
          <span className="font-semibold text-sm" style={{ color: "var(--text-primary)" }}>
            Recent Sessions
          </span>
        </div>
        {sessions.length === 0 ? (
          <p style={{ fontSize: "0.82rem", color: "var(--text-faint)" }}>No sessions yet.</p>
        ) : (
          <div className="flex flex-col gap-2">
            {sessions.slice(0, 5).map((s) => (
              <div
                key={s.session_id}
                className="flex items-center rounded-xl px-3 py-2 transition-colors group"
                style={{ background: "var(--bg)" }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-lavender)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "var(--bg)")}
              >
                <button
                  onClick={() => router.push(`/interview/${s.session_id}`)}
                  className="flex-1 text-left flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-sm" style={{ color: "var(--text-primary)" }}>
                      {s.name}
                    </p>
                    <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                      {s.stage} · {s.stored_at ? new Date(s.stored_at * 1000).toLocaleDateString() : "—"}
                    </p>
                  </div>
                  <MessageSquare size={14} style={{ color: "var(--text-faint)" }} />
                </button>
                <button
                  onClick={async (e) => {
                    e.stopPropagation();
                    await deleteSession(s.session_id);
                    setSessions((prev) => prev.filter((x) => x.session_id !== s.session_id));
                  }}
                  className="opacity-0 group-hover:opacity-100 ml-2 flex-shrink-0 transition-opacity"
                  style={{ color: "var(--text-faint)", background: "none", border: "none", cursor: "pointer", padding: 4, borderRadius: 6 }}
                  title="Delete session"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
