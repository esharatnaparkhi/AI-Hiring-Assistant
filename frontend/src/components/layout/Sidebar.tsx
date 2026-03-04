"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Home, Clock } from "lucide-react";
import { Profile, SessionSummary } from "@/lib/api";
import { useEffect, useState } from "react";
import { listSessions } from "@/lib/api";

const STAGE_STEPS = ["Greeting", "Profile", "Technical", "Evaluation", "Complete"];

interface Props {
  sessionId: string;
  profile: Profile;
  profilePct: number;
  stageIndex: number;
  stage: string;
}

export default function Sidebar({ sessionId, profile, profilePct, stageIndex, stage }: Props) {
  const router = useRouter();
  const [recent, setRecent] = useState<SessionSummary[]>([]);

  useEffect(() => {
    listSessions(10).then(setRecent).catch(() => {});
  }, []);

  return (
    <aside
      className="flex flex-col h-full"
      style={{
        width: 270,
        flexShrink: 0,
        background: "var(--bg-sidebar)",
        borderRight: "1px solid var(--border)",
        padding: "20px 16px",
        gap: 20,
        overflowY: "auto",
      }}
    >
      {/* Logo */}
      <div>
        <Link href="/" className="flex items-center gap-2" style={{ textDecoration: "none" }}>
          <span style={{ fontSize: "1.3rem" }}>🎯</span>
          <span className="font-bold" style={{ fontSize: "1rem", color: "var(--text-primary)" }}>
            TalentScout
          </span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1">
        <button
          onClick={() => router.push("/")}
          className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-colors w-full text-left"
          style={{ color: "var(--text-muted)", background: "transparent" }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
        >
          <Home size={15} /> Dashboard
        </button>
      </nav>

      <hr style={{ border: "none", borderTop: "1px solid var(--border)" }} />

      {/* Stage progress */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>
          Interview Progress
        </p>
        <div className="flex flex-col gap-1.5">
          {STAGE_STEPS.map((s, i) => {
            const done = i < stageIndex;
            const active = i === stageIndex;
            return (
              <div key={s} className="flex items-center gap-2">
                <div
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: "50%",
                    background: done ? "#22C55E" : active ? "#7C3AED" : "var(--border)",
                    color: "#fff",
                    fontSize: "0.65rem",
                    fontWeight: 700,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {done ? "✓" : i + 1}
                </div>
                <span
                  style={{
                    fontSize: "0.8rem",
                    color: active ? "var(--text-primary)" : done ? "#22C55E" : "var(--text-faint)",
                    fontWeight: active ? 600 : 400,
                  }}
                >
                  {s}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <hr style={{ border: "none", borderTop: "1px solid var(--border)" }} />

      {/* Profile card */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            Candidate
          </p>
          {profilePct > 0 && (
            <span className="text-xs" style={{ color: "var(--text-faint)" }}>{profilePct}%</span>
          )}
        </div>

        {profilePct > 0 && (
          <div
            className="rounded-full mb-3"
            style={{ height: 4, background: "var(--border)" }}
          >
            <div
              className="rounded-full"
              style={{
                height: "100%",
                width: `${profilePct}%`,
                background: "linear-gradient(90deg, #7C3AED, #2563EB)",
                transition: "width 0.4s ease",
              }}
            />
          </div>
        )}

        <div
          className="rounded-2xl p-3 flex flex-col gap-2"
          style={{ background: "var(--bg)", border: "1px solid var(--border)" }}
        >
          {profile.full_name ? (
            <ProfileField label="Name" value={profile.full_name} />
          ) : (
            <p style={{ fontSize: "0.78rem", color: "var(--text-faint)" }}>Collecting info…</p>
          )}
          {profile.email && <ProfileField label="Email" value={profile.email} />}
          {profile.years_of_experience && (
            <ProfileField label="Exp." value={`${profile.years_of_experience} yrs`} />
          )}
          {profile.location && <ProfileField label="Location" value={profile.location} />}
          {profile.desired_role && <ProfileField label="Role" value={profile.desired_role} />}
          {profile.key_skills?.length > 0 && (
            <div>
              <span style={{ fontSize: "0.7rem", color: "var(--text-faint)" }}>Skills</span>
              <div className="mt-1">
                {profile.key_skills.map((s) => (
                  <span key={s} className="skill-tag">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent sessions */}
      {recent.length > 0 && (
        <>
          <hr style={{ border: "none", borderTop: "1px solid var(--border)" }} />
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider mb-2 flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
              <Clock size={11} /> Recent
            </p>
            {recent.filter(r => r.session_id !== sessionId).slice(0, 4).map((r) => (
              <button
                key={r.session_id}
                onClick={() => router.push(`/interview/${r.session_id}`)}
                className="w-full text-left rounded-xl px-2 py-1.5 mb-1 transition-colors"
                style={{ background: "transparent" }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                <p style={{ fontSize: "0.78rem", fontWeight: 500, color: "var(--text-secondary)" }}>
                  {r.name}
                </p>
                <p style={{ fontSize: "0.68rem", color: "var(--text-faint)" }}>{r.stage}</p>
              </button>
            ))}
          </div>
        </>
      )}

      <div className="mt-auto">
        <p style={{ fontSize: "0.68rem", color: "var(--text-faint)" }}>
          Session <span className="font-mono">{sessionId.slice(0, 8)}…</span>
        </p>
      </div>
    </aside>
  );
}

function ProfileField({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2 items-start">
      <span style={{ fontSize: "0.68rem", color: "var(--text-faint)", minWidth: 50, paddingTop: 1 }}>
        {label}
      </span>
      <span style={{ fontSize: "0.78rem", color: "var(--text-primary)", fontWeight: 500, wordBreak: "break-word" }}>
        {value}
      </span>
    </div>
  );
}
