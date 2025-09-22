import os
from typing import Dict
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SYSTEM = (
    "You draft concise, truthful, professional answers for job applications. "
    "Never fabricate employment details; prefer specific, quantified outcomes."
)

def generate_answers(profile: dict, job_desc: str, questions: list[str]) -> Dict[str,str]:
    answers: Dict[str,str] = {}
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
        resp = client.chat.completions.create(
            model=os.getenv("LLM_MODEL","gpt-4o-mini"),
            messages=[
                {"role":"system","content":SYSTEM},
                {"role":"user","content":prompt}
            ],
            temperature=0.3
        )
        answers[q] = resp.choices[0].message.content.strip()
    return answers