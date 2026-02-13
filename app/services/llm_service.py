# Wrapper LLM
# app/services/llm_service.py
from openai import AsyncOpenAI
from app.config import settings
from app.models.schemas import Message
from typing import AsyncIterator

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = settings.default_model
    
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> dict | AsyncIterator[str]:
        """Génère une complétion."""
        
        formatted_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]
        
        model = model or self.default_model
        
        if stream:
            return self._stream_complete(formatted_messages, model, temperature, max_tokens)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "model": model,
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _stream_complete(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncIterator[str]:
        """Streaming de la réponse."""
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

# Singleton
llm_service = LLMService()