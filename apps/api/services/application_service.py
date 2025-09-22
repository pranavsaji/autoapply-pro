import yaml, os
from ..models.domain import Profile, Job, ApplicationPlan
from ai.qa import generate_answers
from ai.cover_letter import tailored_cover_letter

with open("policies/preferences.yaml") as f:
    PREFS = yaml.safe_load(f)

async def plan_application(profile: Profile, job: Job) -> ApplicationPlan:
    questions = [
        "Briefly describe your most relevant experience",
        "Why do you want to work here?",
        "Are you legally authorized to work in the U.S.?",
    ]
    answers = generate_answers(profile.dict(), job.description_html or "", questions)

    cl = None
    if PREFS.get("application", {}).get("cover_letter") == "tailored":
        cl = tailored_cover_letter(profile.dict(), job.dict())

    plan = ApplicationPlan(job=job, resume_variant=PREFS.get("application", {}).get("resume_variant", "default"),
                           cover_letter=cl, answers=answers, requires_hitl=PREFS.get("application", {}).get("approval_mode") == "hitl")
    return plan