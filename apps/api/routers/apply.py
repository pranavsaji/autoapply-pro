# apps/api/routers/apply.py
from fastapi import APIRouter, Body
from apps.api.models.domain import Job, ApplicationPlan
from apps.api.services.application_service import plan_application

router = APIRouter()

@router.post("/plan", response_model=ApplicationPlan)
def plan(job: Job = Body(...)) -> ApplicationPlan:
    return plan_application(job)
