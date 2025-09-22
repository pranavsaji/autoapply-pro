from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from apps.api.models.domain import Job
from apps.api.models.sql.jobs import JobRow

def _format_salary(row: JobRow) -> Optional[str]:
    if row.salary_min is None and row.salary_max is None:
        return None
    cur = row.currency or "USD"
    per = row.salary_period or "year"
    if row.salary_min is not None and row.salary_max is not None:
        return f"{cur} {int(row.salary_min):,}–{int(row.salary_max):,}/{per}"
    if row.salary_min is not None:
        return f"{cur} {int(row.salary_min):,}+/{per}"
    return f"{cur} up to {int(row.salary_max):,}/{per}"

def _to_job(row: JobRow) -> Job:
    url = row.canonical_url or row.apply_url or "http://example.com"  # fallback
    desc = row.description_md or row.description_raw
    return Job(
        id=row.id,
        title=row.title,
        company=row.company,
        url=url,
        location=row.location,
        source=row.source,
        salary=_format_salary(row),
        description_html=desc,
    )

def find_jobs(
    db: Session,
    query: Optional[str],
    location: Optional[str],
    remote: Optional[bool],
    source: Optional[str],
    limit: int = 25,
    offset: int = 0,
) -> List[Job]:
    stmt = select(JobRow)

    if query:
        like = f"%{query}%"
        stmt = stmt.where(or_(
            JobRow.title.ilike(like),
            JobRow.company.ilike(like),
            JobRow.description_md.ilike(like),
            JobRow.description_raw.ilike(like),
        ))

    if location:
        stmt = stmt.where(JobRow.location.ilike(f"%{location}%"))

    if remote is not None:
        stmt = stmt.where(JobRow.remote.is_(remote))

    if source:
        stmt = stmt.where(JobRow.source.ilike(source))

    stmt = stmt.order_by(JobRow.posted_at.desc().nullslast()).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    return [_to_job(r) for r in rows]
