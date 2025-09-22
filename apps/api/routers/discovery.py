from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from apps.api.models.db import get_db
from apps.api.models.domain import Job
from apps.api.models.sql.jobs import JobRow
from apps.api.services.discovery_service import find_jobs

router = APIRouter()

@router.get("/debug_count")
def debug_count(db: Session = Depends(get_db)):
    n = db.execute(select(func.count()).select_from(JobRow)).scalar_one()
    return {"count": n}

@router.get("/search", response_model=List[Job])
def search_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    remote: Optional[bool] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return find_jobs(db, query, location, remote, source, limit, offset)
