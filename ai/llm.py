from typing import List, Dict, Any
from apps.api.settings import settings

# Simple shim to unify different SDKs into a single .chat(...) call
class ChatClient:
    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        raise NotImplementedError

class OpenAIChat(ChatClient):
    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        resp = self.client.chat.completions.create(
            model=model, messages=messages, temperature=temperature
        )
        return resp.choices[0].message.content.strip()

class GroqChat(ChatClient):
    def __init__(self):
        # pip install groq
        from groq import Groq
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        # Groq uses OpenAI-compatible Chat Completions
        resp = self.client.chat.completions.create(
            model=model, messages=messages, temperature=temperature
        )
        return resp.choices[0].message.content.strip()

def get_chat_client() -> ChatClient:
    provider = settings.LLM_PROVIDER
    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in .env")
        return OpenAIChat()
    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set in .env")
        return GroqChat()
    # Extend here for anthropic/vertex/bedrock
    raise RuntimeError(f"Unsupported LLM_PROVIDER: {provider}")
