# AI Hiring Assistant

**An AI chatbot for hiring interviews.** Collects candidate info, asks skill-based technical questions, and evaluates performance with rank and comments.

---

## Features

- Chat interface with **Streamlit**  
- Collects **name, email, phone, experience, location, skills**  
- Extracts info from free-text input  
- Asks **3–5 technical questions one by one**  
- Ends on keywords: `exit`, `quit`, `done`, `bye`, `stop`  
- Uses **Groq AI** for question generation  
- Automatically evaluates candidate performance and stores **rank and comments**  
- Stores candidate data **locally**, no cloud required  

---

## Setup

1. Create virtual environment:

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

--- 

## How It Works

1. **Profile Collection**  
   The AI asks for the candidate's **name, email, phone, experience, location, and key skills** in one message.

2. **Silent Extraction**  
   The assistant extracts this info into a structured JSON profile behind the scenes.

3. **Technical Questions**  
   Based on skills, the AI asks **3–5 tailored questions** one by one in a conversational style.

4. **Performance Evaluation**  
   After the interview, the AI generates a **rank (1–5) and comments** on the candidate's performance.

5. **Graceful Exit & Storage**  
   The session ends on keywords like `exit`, `quit`, or `done`.  
   The profile, answers, and evaluation are saved locally for recruiters to review.
