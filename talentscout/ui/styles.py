import streamlit as st

_CSS = """
/* ── Global ─────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.sidebar-logo {
    font-size: 1.6rem;
    font-weight: 700;
    color: #38bdf8 !important;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.sidebar-tagline {
    font-size: 0.75rem;
    color: #94a3b8 !important;
    margin-bottom: 1.5rem;
}

/* Stage pill */
.stage-pill {
    display: inline-block;
    background: #0ea5e9;
    color: #fff !important;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 999px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Profile card */
.profile-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 0.5rem;
}
.profile-field {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 6px;
    font-size: 0.8rem;
}
.profile-label {
    color: #94a3b8 !important;
    min-width: 72px;
    font-size: 0.72rem;
    padding-top: 1px;
}
.profile-value {
    color: #f1f5f9 !important;
    font-weight: 500;
    word-break: break-word;
}
.skill-tag {
    display: inline-block;
    background: #1d4ed8;
    color: #bfdbfe !important;
    font-size: 0.68rem;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 999px;
    margin: 2px 2px 0 0;
}

/* ── Chat ────────────────────────────────────────────────────────────────── */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding: 4px 0 16px 0;
}

/* Shared bubble styles */
.bubble-user, .bubble-ai {
    max-width: 78%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 0.92rem;
    line-height: 1.55;
    word-break: break-word;
    white-space: pre-wrap;
}

/* User bubble — right */
.bubble-row-user {
    display: flex;
    justify-content: flex-end;
}
.bubble-user {
    background: #2563eb;
    color: #ffffff;
    border-bottom-right-radius: 4px;
}

/* AI bubble — left */
.bubble-row-ai {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    gap: 8px;
}
.bubble-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    flex-shrink: 0;
    color: #fff;
}
.bubble-ai {
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-bottom-left-radius: 4px;
}

/* ── Voice Controls ──────────────────────────────────────────────────────── */
.voice-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 16px;
}
.voice-label {
    font-size: 0.82rem;
    color: #94a3b8;
}

/* ── Evaluation Panel ────────────────────────────────────────────────────── */
.eval-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.eval-rank {
    font-size: 2.6rem;
    font-weight: 700;
    color: #38bdf8;
    line-height: 1;
}
.eval-label {
    font-size: 0.75rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}
.rec-badge {
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 999px;
    margin-top: 8px;
}
.rec-hire    { background:#166534; color:#bbf7d0 !important; }
.rec-maybe   { background:#713f12; color:#fef08a !important; }
.rec-no_hire { background:#7f1d1d; color:#fecaca !important; }

.bullet-list { list-style: none; padding: 0; margin: 0; }
.bullet-list li {
    font-size: 0.85rem;
    color: #cbd5e1;
    padding: 4px 0;
    display: flex;
    align-items: flex-start;
    gap: 6px;
}
.dot-green { color: #4ade80; }
.dot-red   { color: #f87171; }

/* ── Page title ──────────────────────────────────────────────────────────── */
.page-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0;
}
.page-subtitle {
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 1.2rem;
}
"""


def apply_styles() -> None:
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
