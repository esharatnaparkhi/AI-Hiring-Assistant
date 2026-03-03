"""
TalentScout AI — Streamlit entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st

from talentscout.conversation import InterviewSession
from talentscout.voice import VoiceClient
from talentscout.utils import new_session_id, run_async
from talentscout.ui.styles import apply_styles
from talentscout.ui.components import (
    render_sidebar,
    render_chat,
    render_input,
    render_evaluation,
)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()

# ── Session state bootstrap ───────────────────────────────────────────────────
if "session" not in st.session_state:
    st.session_state.session = InterviewSession(new_session_id())

if "voice_client" not in st.session_state:
    st.session_state.voice_client = VoiceClient()

if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

session: InterviewSession = st.session_state.session
voice_client: VoiceClient = st.session_state.voice_client

# ── Kick off with AI greeting on very first load ──────────────────────────────
if not session.history:
    with st.spinner("Starting interview…"):
        run_async(session.initialize())
    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar(session)

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">🎯 TalentScout AI Interview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Your AI-powered hiring assistant — say <b>done</b> when you\'re finished.</div>',
    unsafe_allow_html=True,
)

# Chat history
render_chat(session)

# Input area (text or voice)
render_input(session, voice_client)

# Evaluation results (visible once interview ends)
if session.is_complete:
    render_evaluation(session)
