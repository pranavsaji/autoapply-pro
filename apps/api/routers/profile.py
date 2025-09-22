from fastapi import APIRouter, UploadFile
from ..services.profile_service import import_resume_pdf, get_profile

router = APIRouter()

@router.post("/import")
async def import_resume(file: UploadFile):
    return await import_resume_pdf(file)

@router.get("")
async def read_profile():
    return await get_profile()