# app.py
import os, asyncio, time, json, re
import streamlit as st
from dotenv import load_dotenv
import plotly.graph_objects as go  # Added for bar chart

from llm import LLMClient, SYSTEM_PROMPT
from utils import (
    is_end_signal, new_session_id
)
from storage import hash_candidate

load_dotenv()
st.set_page_config(page_title="AI Hiring Assistant", layout="centered") 
st.sidebar.title("Instructions")
st.sidebar.markdown(
    """
    - Chat with the AI for a hiring interview.
    - Provide your full profile in one message.
    - Technical questions will follow automatically.
    - Say **exit / quit / done / bye / stop** to finish.
    """
)

st.title("AI Hiring Assistant")
st.caption("Chat with me for your hiring interview. Say **exit/quit/done/bye/stop** to finish.")

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = new_session_id()
if "history" not in st.session_state:
    st.session_state.history = []
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "stage" not in st.session_state:
    st.session_state.stage = "profile"

def extract_json_from_text(text: str):
    match = re.search(r"\{[\s\S]*\}", text) 
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

for role, content in st.session_state.history:
    if role == "assistant":
        st.chat_message("assistant").markdown(content)

if not st.session_state.history:
    greet_text = (
        "👋 Hello! I’m your AI hiring assistant.\n\n"
        "Could you please provide your details in one message?\n"
        "Your **full name, email, phone, years of experience, location, and key skills.**"
    )
    st.session_state.history.append(("assistant", greet_text))
    st.chat_message("assistant").markdown(greet_text)

user_text = st.chat_input("Type here...")
if user_text:
    st.session_state.history.append(("user", user_text))
    st.chat_message("user").markdown(user_text)

    if is_end_signal(user_text):
        st.session_state.stage = "done"

        async def evaluate_and_store():
            client = LLMClient()
            eval_prompt = f"""
                You are an AI Hiring Assistant.
                Candidate Profile: {st.session_state.profile}
                Conversation History: {st.session_state.history}

                Please provide:
                1. A concise evaluation comment of the candidate's performance.
                2. A rank from 1 (low) to 5 (excellent) based on technical answers.

                Return the result as JSON:
                {{ "rank": ..., "comments": "..." }}
            """
            messages_eval = [{"role": "system", "content": eval_prompt}]
            eval_resp = await client.chat(messages_eval)
            parsed_eval = extract_json_from_text(eval_resp)
            if parsed_eval:
                st.session_state.profile["evaluation"] = parsed_eval

            record = {
                "session_id": st.session_state.session_id,
                "profile": st.session_state.profile,
                "history": st.session_state.history,
                "ended_at": int(time.time()),
                "stored_at": int(time.time()),
            }

            # Storing Data
            hash_candidate(record)

            improv_prompt = f"""
                You are an AI Hiring Assistant.
                Candidate Profile: {st.session_state.profile}
                Conversation History: {st.session_state.history}

                Please provide a list of 3-5 skills/areas and a score (1-5)
                indicating where the candidate needs improvement.
                Return as JSON: {{ "skills": ["...", "..."], "scores": [1,2,...] }}
            """
            messages_improv = [{"role": "system", "content": improv_prompt}]
            improv_resp = await client.chat(messages_improv)
            improv_data = extract_json_from_text(improv_resp)

            if improv_data:
                skills = improv_data.get("skills", [])
                scores = improv_data.get("scores", [])
                if skills and scores:
                    fig = go.Figure(go.Bar(
                        x=skills,
                        y=scores,
                        marker_color='indianred',
                        text=scores,
                        textposition='auto'
                    ))
                    fig.update_layout(
                        title="Areas to Improve",
                        yaxis=dict(title="Knowledge Score (1=Low, 5=High)"),
                        xaxis=dict(title="Skills"),
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        asyncio.run(evaluate_and_store())

        bye = "Thank you for your responses! We'll review and get back to you."
        st.session_state.history.append(("assistant", bye))
        st.chat_message("assistant").markdown(bye)

    else:  #Main Flow
        async def run_flow(user_text):
            client = LLMClient()

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for role, content in st.session_state.history:
                messages.append({"role": role, "content": content})

            response = await client.chat(messages)

            parsed = extract_json_from_text(response)
            if parsed:
                st.session_state.profile.update(parsed)
                clean_reply = re.sub(r"```json[\s\S]*```", "", response).strip()
                if not clean_reply:
                    clean_reply = "Got your profile details!"
                reply = clean_reply
            else:
                reply = response 

            st.session_state.history.append(("assistant", reply))
            st.chat_message("assistant").markdown(reply)

        asyncio.run(run_flow(user_text))
