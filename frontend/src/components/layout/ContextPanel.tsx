"use client";

import { Volume2, VolumeX, Cpu, Info } from "lucide-react";

interface Improvement {
  skill: string;
  score: number;
  advice: string;
}

interface Evaluation {
  rank?: number;
  recommendation?: string;
  comments?: string;
  strengths?: string[];
  concerns?: string[];
}

interface Props {
  stage: string;
  sessionId: string;
  voiceModeEnabled: boolean;
  onVoiceToggle: () => void;
  evaluation?: Evaluation;
  improvements?: Improvement[];
  isComplete: boolean;
}

const REC_LABELS: Record<string, { label: string; cls: string }> = {
  hire:    { label: "✅ Hire",    cls: "rec-hire"    },
  maybe:   { label: "🤔 Maybe",   cls: "rec-maybe"   },
  no_hire: { label: "❌ No Hire", cls: "rec-no_hire" },
};

export default function ContextPanel({
  stage, sessionId: _sessionId, voiceModeEnabled, onVoiceToggle,
  evaluation, improvements, isComplete,
}: Props) {
  return (
    <aside
      className="flex flex-col gap-5 overflow-y-auto"
      style={{
        width: 280,
        flexShrink: 0,
        padding: "24px 16px",
        borderLeft: "1px solid var(--border)",
        background: "var(--bg-panel)",
      }}
    >
      {/* Model info */}
      <div className="card p-4" style={{ background: "var(--card-lavender)" }}>
        <div className="flex items-center gap-2 mb-1">
          <Cpu size={14} style={{ color: "#7C3AED" }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#7C3AED" }}>
            Model
          </span>
        </div>
        {/* <p className="font-semibold text-sm" style={{ color: "var(--text-primary)" }}>TalentScout AI</p> */}
        <p style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginTop: 2 }}>AI-Powered Interview Assistant</p>
      </div>

      {/* Stage info */}
      <div className="card p-4" style={{ background: "var(--card-white)" }}>
        <div className="flex items-center gap-2 mb-2">
          <Info size={14} style={{ color: "var(--text-muted)" }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            Current Stage
          </span>
        </div>
        <span
          className="inline-block text-xs font-semibold px-3 py-1 rounded-full"
          style={{ background: "var(--card-lavender)", color: "#5B21B6" }}
        >
          {stage}
        </span>
        {/* <p style={{ fontSize: "0.72rem", color: "var(--text-faint)", marginTop: 8 }}>
          Session <span className="font-mono">{sessionId.slice(0, 8)}…</span>
        </p> */}
      </div>

      {/* Voice toggle */}
      <div className="card p-4" style={{ background: "var(--card-blue)" }}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>Voice Mode</p>
            <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
              {voiceModeEnabled ? "Voice mode active" : "Click to enable"}
            </p>
          </div>
          <button
            onClick={onVoiceToggle}
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              border: "none",
              cursor: "pointer",
              background: voiceModeEnabled ? "#2563EB" : "var(--border)",
              color: voiceModeEnabled ? "#fff" : "var(--text-muted)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "background 0.15s",
            }}
          >
            {voiceModeEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          </button>
        </div>
      </div>

      {/* Evaluation (shown when complete) */}
      {isComplete && evaluation && (
        <>
          <div className="card p-4" style={{ background: "var(--card-white)" }}>
            <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>
              Evaluation
            </p>

            {/* Rank */}
            <div className="flex items-end gap-2 mb-2">
              <span className="font-bold" style={{ fontSize: "2.2rem", color: "var(--text-primary)", lineHeight: 1 }}>
                {evaluation.rank ?? "—"}
              </span>
              <span style={{ color: "var(--text-muted)", marginBottom: 4, fontSize: "0.85rem" }}>/5</span>
            </div>

            {/* Recommendation */}
            {evaluation.recommendation && REC_LABELS[evaluation.recommendation] && (
              <span
                className={`inline-block text-xs font-semibold px-3 py-1 rounded-full mb-3 ${REC_LABELS[evaluation.recommendation].cls}`}
              >
                {REC_LABELS[evaluation.recommendation].label}
              </span>
            )}

            {/* Comments */}
            {evaluation.comments && (
              <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                {evaluation.comments}
              </p>
            )}
          </div>

          {/* Strengths / Concerns */}
          {(evaluation.strengths?.length || evaluation.concerns?.length) && (
            <div className="card p-4" style={{ background: "var(--card-white)" }}>
              {evaluation.strengths?.length ? (
                <div className="mb-3">
                  <p className="text-xs font-semibold mb-1" style={{ color: "#166534" }}>💪 Strengths</p>
                  {evaluation.strengths.map((s, i) => (
                    <p key={i} style={{ fontSize: "0.78rem", color: "var(--text-secondary)", paddingLeft: 8 }}>
                      · {s}
                    </p>
                  ))}
                </div>
              ) : null}
              {evaluation.concerns?.length ? (
                <div>
                  <p className="text-xs font-semibold mb-1" style={{ color: "#7F1D1D" }}>⚠️ Concerns</p>
                  {evaluation.concerns.map((c, i) => (
                    <p key={i} style={{ fontSize: "0.78rem", color: "var(--text-secondary)", paddingLeft: 8 }}>
                      · {c}
                    </p>
                  ))}
                </div>
              ) : null}
            </div>
          )}

          {/* Improvements */}
          {improvements?.length ? (
            <div className="card p-4" style={{ background: "var(--card-white)" }}>
              <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>
                Areas to Improve
              </p>
              {improvements.map((item) => (
                <div key={item.skill} className="mb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-primary)" }}>
                      {item.skill}
                    </span>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{item.score}/10</span>
                  </div>
                  <div style={{ height: 6, background: "var(--border)", borderRadius: 999 }}>
                    <div
                      style={{
                        height: "100%",
                        width: `${item.score * 10}%`,
                        borderRadius: 999,
                        background: item.score < 4 ? "#EF4444" : item.score < 7 ? "#F59E0B" : "#22C55E",
                        transition: "width 0.4s ease",
                      }}
                    />
                  </div>
                  <p style={{ fontSize: "0.7rem", color: "var(--text-faint)", marginTop: 3 }}>{item.advice}</p>
                </div>
              ))}
            </div>
          ) : null}
        </>
      )}
    </aside>
  );
}
