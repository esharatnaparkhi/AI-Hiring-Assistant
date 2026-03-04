import BentoGrid from "@/components/dashboard/BentoGrid";

export default function HomePage() {
  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      {/* Top nav */}
      <header
        className="flex items-center justify-between px-10 py-5"
        style={{ borderBottom: "1px solid var(--border)", background: "rgba(255,255,255,0.7)", backdropFilter: "blur(12px)" }}
      >
        <div className="flex items-center gap-2">
          <span style={{ fontSize: "1.4rem" }}>🎯</span>
          <span className="font-bold" style={{ fontSize: "1.1rem", color: "var(--text-primary)" }}>
            TalentScout
          </span>
          <span
            className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full"
            style={{ background: "var(--card-lavender)", color: "#7C3AED" }}
          >
            AI
          </span>
        </div>
        <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
          Powered by OpenAI + ElevenLabs
        </p>
      </header>

      {/* Main content */}
      <main className="px-10 py-10" style={{ maxWidth: 1280, margin: "0 auto" }}>
        <div className="mb-8">
          <h2 className="font-bold mb-1" style={{ fontSize: "1.5rem", color: "var(--text-primary)" }}>
            Dashboard
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Start a new interview or review past sessions.
          </p>
        </div>

        <BentoGrid />
      </main>
    </div>
  );
}
