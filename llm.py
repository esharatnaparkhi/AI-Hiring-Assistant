# llm.py
import os
from typing import List, Dict
from groq import Groq

SYSTEM_PROMPT = """
You are an AI Hiring Assistant.

Your tasks:
1. Collect candidate details in the profile stage:
   - full_name
   - email
   - phone
   - years_of_experience
   - location
   - key_skills

2. When the candidate provides details (structured or unstructured),
   parse them into JSON like this:

{
  "full_name": "...",
  "email": "...",
  "phone": "...",
  "years_of_experience": "...",
  "location": "...",
  "key_skills": ["...", "..."]
}

3. If some fields are missing, politely ask ONLY for the missing ones.

4. Once the profile is complete, switch to technical stage:
   - Ask 3–5 concise technical interview questions.
   - Ask them one by one, not all at once.

5. Respond in the same language as the candidate. Always produce clear, friendly, and professional replies.

6. For every candidate message, infer the sentiment (positive, neutral, negative) 
   and optionally summarize it internally for evaluation purposes.

7. Stop politely if the candidate says exit/quit/done.

"""


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY!")
        self.model = os.getenv("GROQ_MODEL")
        self.client = Groq(api_key=self.api_key)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send a chat completion request to Groq using SDK.

        Args:
            messages (list): A list of {"role": "system"|"user"|"assistant", "content": "..."}

        Returns:
            str: The assistant's reply
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()
