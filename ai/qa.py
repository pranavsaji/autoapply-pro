from apps.api.settings import settings
from ai.llm import get_chat_client

SYSTEM = (
    "You draft concise, truthful, professional answers for job applications. "
    "Never fabricate employment details; prefer specific, quantified outcomes."
)

_client = get_chat_client()

def generate_answers(profile: dict, job_desc: str, questions: list[str]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for q in questions:
        prompt = f"""
Profile:
{profile}

Job Description:
{job_desc}

Question:
{q}

Draft a 3-5 sentence answer tailored to this job. Use the candidate's real skills and experience.
"""
        msg = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ]
        answers[q] = _client.chat(model=settings.LLM_MODEL, messages=msg, temperature=0.3)
    return answers
