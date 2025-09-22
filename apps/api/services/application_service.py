# apps/api/services/application_service.py
from typing import Dict, Any
from apps.api.services.profile_service import get_profile
from apps.api.models.domain import Job, ApplicationPlan
from ai.qa import generate_answers  # your existing LLM helper

def plan_application(job: Job) -> ApplicationPlan:
    prof = get_profile()
    resume_text = prof.resume_text if prof else None

    # Your LLM helper should accept resume_text + job description/html
    plan = generate_answers(
        job=job.model_dump(),
        resume_text=resume_text or "",
    )
    # Ensure required fields exist even if LLM returns partials
    plan.setdefault("answers", {})
    plan.setdefault("cover_letter", None)
    plan.setdefault("resume_variant", "default")

    return ApplicationPlan(
        job=job,
        resume_variant=plan["resume_variant"],
        cover_letter=plan.get("cover_letter"),
        answers=plan["answers"],
        requires_hitl=True,
    )
