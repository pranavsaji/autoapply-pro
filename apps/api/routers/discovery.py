# apps/api/routers/discovery.py
from fastapi import APIRouter, Query
from typing import List, Optional
from apps.api.models.domain import Job

router = APIRouter()

# Temporary in-memory sample
_SAMPLE = [
    Job(id="gh-1", title="Senior ML Engineer", company="ExampleCo",
        url="https://boards.greenhouse.io/example/jobs/12345",
        location="Remote", source="greenhouse", salary=None, description_html=None),
]

@router.get("/search", response_model=List[Job])
async def search_jobs(query: str = Query(""), location: Optional[str] = None):
    q = query.lower()
    results = [j for j in _SAMPLE if q in j.title.lower()]
    if location:
        results = [j for j in results if j.location and location.lower() in j.location.lower()]
    return results
