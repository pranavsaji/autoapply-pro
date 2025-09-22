# ai/qa.py
from typing import Dict, Any
from apps.api.settings import settings

def generate_answers(job: Dict[str, Any], resume_text: str = "") -> Dict[str, Any]:
    """
    Returns a plan dict like:
      {
        "resume_variant": "ml_senior",
        "cover_letter": "...",
        "answers": { "q": "a", ... }
      }
    Uses OpenAI if configured; otherwise falls back to a simple heuristic.
    """
    jd_text = (job.get("description_html") or "")[:12000]
    title = job.get("title","")
    company = job.get("company","")

    # If no API configured, fallback mock
    if settings.LLM_PROVIDER != "openai" or not settings.OPENAI_API_KEY:
        return {
            "resume_variant": "default",
            "cover_letter": f"Cover letter for {title} at {company}.\n\nResume highlights:\n{resume_text[:800]}",
            "answers": {
                "Briefly describe your most relevant experience": (resume_text[:900] or "See resume."),
                "Why do you want to work here?": f"I’m excited about {company} and the {title} role.",
            },
        }

    # --- OpenAI path ---
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    system = (
        "You are an application assistant. Write concise, specific answers grounded ONLY in the resume text. "
        "Avoid generic fluff. Use bullet points sparingly. Return JSON with keys: resume_variant, cover_letter, answers."
    )
    user = (
        f"JOB TITLE: {title}\nCOMPANY: {company}\n"
        f"JOB DESCRIPTION (HTML allowed):\n{jd_text}\n\n"
        f"RESUME TEXT:\n{resume_text}\n\n"
        "Tasks:\n"
        "1) Choose resume_variant (short token like 'ml_senior', 'data_eng').\n"
        "2) Draft a one-page cover_letter tailored to the job.\n"
        "3) Provide answers for common questions:\n"
        "   - Briefly describe your most relevant experience\n"
        "   - Why do you want to work here?\n"
        "Return strict JSON."
    )

    # Note: use your preferred model here
    chat = client.chat.completions.create(
        model=settings.OPENAI_MODEL or "gpt-4o-mini",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        response_format={ "type":"json_object" },
        temperature=0.4,
    )
    import json
    try:
        content = chat.choices[0].message.content
        data = json.loads(content)
        data.setdefault("resume_variant", "default")
        data.setdefault("cover_letter", None)
        data.setdefault("answers", {})
        return data
    except Exception:
        # fail-soft
        return {
            "resume_variant": "default",
            "cover_letter": None,
            "answers": {},
        }
