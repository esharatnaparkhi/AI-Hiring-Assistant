"""
Reusable Streamlit UI components for TalentScout.
"""

import streamlit as st
import plotly.graph_objects as go

from ..conversation import InterviewSession
from ..voice import VoiceClient, VOICE_ENABLED
from ..storage import save_candidate
from ..utils import run_async

# ── Sidebar ───────────────────────────────────────────────────────────────────

_STAGE_ICONS = ["👋", "📋", "💻", "📊", "✅"]
_STAGE_NAMES = ["Greeting", "Profile", "Technical", "Evaluation", "Complete"]


def render_sidebar(session: InterviewSession) -> None:
    with st.sidebar:
        # Logo
        st.markdown('<div class="sidebar-logo">🎯 TalentScout</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">AI-Powered Interview Assistant</div>', unsafe_allow_html=True)

        st.divider()

        # Interview stage progress
        st.markdown("**Interview Progress**")
        stage_idx = session.stage_index
        cols = st.columns(len(_STAGE_NAMES))
        for i, (icon, name) in enumerate(zip(_STAGE_ICONS, _STAGE_NAMES)):
            with cols[i]:
                active = (i == stage_idx)
                done = (i < stage_idx)
                color = "#0ea5e9" if active else ("#4ade80" if done else "#334155")
                st.markdown(
                    f'<div style="text-align:center;font-size:1.2rem;color:{color}">{icon}</div>'
                    f'<div style="text-align:center;font-size:0.6rem;color:{color};margin-top:2px">{name}</div>',
                    unsafe_allow_html=True,
                )

        st.progress(session.stage_progress, text=f"Stage: {session.stage}")
        st.markdown("")

        # Candidate profile card
        st.markdown("**Candidate Profile**")
        profile = session.profile

        def _field(label: str, value) -> str:
            if not value:
                return ""
            display = ", ".join(value) if isinstance(value, list) else value
            return (
                f'<div class="profile-field">'
                f'<span class="profile-label">{label}</span>'
                f'<span class="profile-value">{display}</span>'
                f"</div>"
            )

        card_html = '<div class="profile-card">'
        card_html += _field("Name", profile.full_name)
        card_html += _field("Email", profile.email)
        card_html += _field("Phone", profile.phone)
        card_html += _field("Exp.", profile.years_of_experience and f"{profile.years_of_experience} yrs")
        card_html += _field("Location", profile.location)
        card_html += _field("Role", profile.desired_role)

        if profile.key_skills:
            tags = "".join(f'<span class="skill-tag">{s}</span>' for s in profile.key_skills)
            card_html += (
                '<div class="profile-field">'
                '<span class="profile-label">Skills</span>'
                f'<span class="profile-value">{tags}</span>'
                "</div>"
            )

        if not any([profile.full_name, profile.email, profile.key_skills]):
            card_html += '<div style="color:#64748b;font-size:0.8rem;">Collecting info…</div>'

        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)

        if profile.completeness_pct() > 0:
            st.progress(profile.completeness_pct() / 100, text=f"Profile {profile.completeness_pct()}% complete")

        st.markdown("")
        st.caption(f"Session `{session.session_id[:8]}…`")


# ── Chat ──────────────────────────────────────────────────────────────────────

def render_chat(session: InterviewSession) -> None:
    """Render conversation history as styled chat bubbles."""
    html = '<div class="chat-wrapper">'
    for msg in session.history:
        if msg.role == "user":
            html += (
                '<div class="bubble-row-user">'
                f'<div class="bubble-user">{_escape(msg.content)}</div>'
                "</div>"
            )
        else:
            html += (
                '<div class="bubble-row-ai">'
                '<div class="bubble-avatar">🤖</div>'
                f'<div class="bubble-ai">{_escape(msg.content)}</div>'
                "</div>"
            )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


# ── Text input + voice input ──────────────────────────────────────────────────

def render_input(session: InterviewSession, voice_client: VoiceClient) -> None:
    """
    Renders the input area.  Voice mode shows st.audio_input; text mode shows
    a standard chat_input.  Returns nothing — side-effects update session state.
    """
    if session.is_complete:
        return

    voice_mode: bool = st.session_state.get("voice_mode", False)

    if VOICE_ENABLED:
        toggle_col, _ = st.columns([1, 3])
        with toggle_col:
            st.session_state["voice_mode"] = st.toggle(
                "🎙️ Voice Mode",
                value=voice_mode,
                key="voice_toggle",
            )
        voice_mode = st.session_state["voice_mode"]

    if voice_mode and VOICE_ENABLED:
        _render_voice_input(session, voice_client)
    else:
        _render_text_input(session, voice_client, voice_mode)


def _render_text_input(session: InterviewSession, voice_client: VoiceClient, tts: bool) -> None:
    user_text = st.chat_input("Type your response…", key="chat_input")
    if user_text:
        _handle_turn(session, user_text, voice_client, tts)


def _render_voice_input(session: InterviewSession, voice_client: VoiceClient) -> None:
    st.markdown(
        '<div class="voice-bar"><span class="voice-label">🎙️ Click the mic to record your response</span></div>',
        unsafe_allow_html=True,
    )
    audio = st.audio_input("Record", key="voice_recorder", label_visibility="collapsed")
    if audio is not None:
        audio_bytes = audio.read()
        if audio_bytes:
            with st.spinner("Transcribing…"):
                user_text = run_async(voice_client.transcribe(audio_bytes, filename="recording.wav"))
            if user_text:
                st.markdown(f"*You said:* **{user_text}**")
                _handle_turn(session, user_text, voice_client, tts=True)
            else:
                st.warning("Could not transcribe audio — please try again or switch to text mode.")


def _handle_turn(
    session: InterviewSession,
    user_text: str,
    voice_client: VoiceClient,
    tts: bool,
) -> None:
    """Process one conversation turn (LLM call + optional TTS) and rerun."""
    with st.spinner("TalentScout is thinking…"):
        reply = run_async(session.process_message(user_text))

    # Auto-play TTS if voice mode is on
    if tts and VOICE_ENABLED:
        with st.spinner("Generating voice response…"):
            audio_bytes = run_async(voice_client.synthesize(reply))
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # Persist if interview ended
    if session.is_complete:
        save_candidate(session.to_record())

    st.rerun()


# ── Evaluation Panel ──────────────────────────────────────────────────────────

def render_evaluation(session: InterviewSession) -> None:
    """Full evaluation display shown after the interview completes."""
    st.markdown("---")
    st.markdown("## 📊 Interview Results")

    ev = session.evaluation
    rank = ev.get("rank", "—")
    rec = ev.get("recommendation", "maybe")
    comments = ev.get("comments", "")
    strengths = ev.get("strengths", [])
    concerns = ev.get("concerns", [])

    # Top row: rank + recommendation
    col_rank, col_rec, col_comment = st.columns([1, 1, 3])
    with col_rank:
        st.markdown(
            f'<div class="eval-card">'
            f'<div class="eval-rank">{rank}<span style="font-size:1.2rem;color:#64748b">/5</span></div>'
            f'<div class="eval-label">Overall Rank</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_rec:
        badge_class = f"rec-{rec}"
        label_map = {"hire": "✅ Hire", "maybe": "🤔 Maybe", "no_hire": "❌ No Hire"}
        label = label_map.get(rec, rec.title())
        st.markdown(
            f'<div class="eval-card">'
            f'<div class="eval-label">Recommendation</div>'
            f'<div class="rec-badge {badge_class}">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_comment:
        st.markdown(
            f'<div class="eval-card" style="height:100%">'
            f'<div class="eval-label">Summary</div>'
            f'<div style="color:#cbd5e1;font-size:0.88rem;margin-top:6px">{_escape(comments)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Strengths / Concerns
    scol, ccol = st.columns(2)
    with scol:
        st.markdown("#### 💪 Strengths")
        if strengths:
            items = "".join(
                f'<li><span class="dot-green">●</span> {_escape(s)}</li>' for s in strengths
            )
            st.markdown(f'<ul class="bullet-list">{items}</ul>', unsafe_allow_html=True)
        else:
            st.caption("No strengths recorded.")
    with ccol:
        st.markdown("#### ⚠️ Concerns")
        if concerns:
            items = "".join(
                f'<li><span class="dot-red">●</span> {_escape(c)}</li>' for c in concerns
            )
            st.markdown(f'<ul class="bullet-list">{items}</ul>', unsafe_allow_html=True)
        else:
            st.caption("No concerns recorded.")

    # Improvement chart
    if session.improvements:
        st.markdown("#### 📈 Areas to Improve")
        labels = [item.get("skill", "") for item in session.improvements]
        scores = [item.get("score", 0) for item in session.improvements]
        advices = [item.get("advice", "") for item in session.improvements]

        fig = go.Figure(
            go.Bar(
                x=scores,
                y=labels,
                orientation="h",
                marker=dict(
                    color=scores,
                    colorscale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#22c55e"]],
                    cmin=0,
                    cmax=10,
                    showscale=True,
                    colorbar=dict(title="Score (0-10)", tickfont=dict(color="#94a3b8")),
                ),
                hovertemplate="<b>%{y}</b><br>Score: %{x}/10<br>%{customdata}<extra></extra>",
                customdata=advices,
            )
        )
        fig.update_layout(
            xaxis=dict(range=[0, 10], tickfont=dict(color="#94a3b8"), gridcolor="#1e293b"),
            yaxis=dict(tickfont=dict(color="#e2e8f0")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.6)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.success("Interview complete. Results have been saved. 🎉")
