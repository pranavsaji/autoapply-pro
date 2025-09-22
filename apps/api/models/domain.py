# apps/api/models/domain.py
from pydantic import BaseModel, AnyUrl, EmailStr, Field
from typing import List, Optional, Dict
from datetime import date
from uuid import UUID

class WorkExp(BaseModel):
    company: str
    title: str
    start: date
    end: Optional[date] = None
    highlights: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

class Education(BaseModel):
    school: str
    degree: str
    start: date
    end: date

class Profile(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    websites: Dict[str, AnyUrl] = Field(default_factory=dict)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    work: List[WorkExp] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    resume_path: Optional[str] = None

class Job(BaseModel):
    id: str | UUID
    title: str
    company: str
    # Relax URL validation so rows with non-strict URLs don’t 500 the API
    url: AnyUrl | str
    location: Optional[str] = None
    source: str  # greenhouse | lever | workday | ashby | linkedin | etc.
    salary: Optional[str] = None
    description_html: Optional[str] = None

class ApplicationPlan(BaseModel):
    job: Job
    resume_variant: str
    cover_letter: Optional[str] = None
    answers: Dict[str, str] = Field(default_factory=dict)
    requires_hitl: bool = True
