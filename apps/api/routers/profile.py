# apps/api/routers/profile.py
from fastapi import APIRouter, UploadFile, File, Body, HTTPException
from typing import Optional
from apps.api.models.domain import Profile
from apps.api.services.profile_service import (
    get_profile, save_profile, attach_resume, attach_cover_letter
)

router = APIRouter()

@router.get("/me", response_model=Optional[Profile])
def read_profile():
    return get_profile()

@router.post("/save", response_model=Profile)
def save_profile_route(profile: Profile = Body(...)):
    return save_profile(profile)

@router.post("/upload", response_model=dict)
def upload_profile_assets(
    resume: Optional[UploadFile] = File(None),
    cover_letter: Optional[UploadFile] = File(None),
):
    result = {}
    if resume:
        prof = attach_resume(resume)
        result["resume_path"] = prof.resume_path
        result["resume_text_len"] = len(prof.resume_text or "")
    if cover_letter:
        path = attach_cover_letter(cover_letter)
        result["cover_letter_path"] = str(path.resolve())
    if not result:
        raise HTTPException(400, "Provide at least one file: resume or cover_letter.")
    return result
