from apps.api.settings import settings
from ai.llm import get_chat_client

_client = get_chat_client()

def tailored_cover_letter(profile: dict, job: dict) -> str:
    prompt = f"""
Write a one-page, high-impact cover letter for the following candidate and role.
Candidate:
{profile}

Role:
{job}

Tone: confident, specific, outcomes-focused, and aligned to the company's mission.
"""
    msg = [
        {"role": "system", "content": "You write ATS-friendly cover letters."},
        {"role": "user", "content": prompt},
    ]
    return _client.chat(model=settings.LLM_MODEL, messages=msg, temperature=0.4)
