# apps/api/routers/apply.py
from fastapi import APIRouter
from apps.api.models.domain import Job, ApplicationPlan, Profile
from apps.api.services.application_service import plan_application

router = APIRouter()

@router.post("/plan", response_model=ApplicationPlan)
async def plan(job: Job):
    # In real code, fetch profile from DB; using a stub:
    profile = Profile(full_name="Your Name", email="you@example.com")
    return await plan_application(profile, job)
