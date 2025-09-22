from .qa import client

def tailored_cover_letter(profile: dict, job: dict) -> str:
    prompt = f"""
Write a one-page, high-impact cover letter for the following candidate and role.
Candidate:
{profile}

Role:
{job}

Tone: confident, specific, outcomes-focused, and aligned to the company's mission.
"""
    resp = client.chat.completions.create(
        model=os.getenv("LLM_MODEL","gpt-4o-mini"),
        messages=[{"role":"system","content":"You write ATS-friendly cover letters."},
                  {"role":"user","content":prompt}],
        temperature=0.4
    )
    return resp.choices[0].message.content.strip()