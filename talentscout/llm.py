import asyncio
from openai import AsyncOpenAI
from .config import OPENAI_API_KEY, OPENAI_MODEL
from .prompts import SYSTEM_PROMPT


class LLMClient:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def chat(self, messages: list[dict]) -> str:
        """Send a conversation to the LLM and return the assistant reply."""
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = await self._client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=full_messages,
            temperature=0.3,
            max_tokens=512,
        )
        return response.choices[0].message.content

    async def complete(self, prompt: str) -> str:
        """One-shot completion — used for evaluation prompts."""
        response = await self._client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800,
        )
        return response.choices[0].message.content
