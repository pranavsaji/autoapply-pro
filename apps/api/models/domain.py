# apps/api/models/domain.py
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Optional, Dict
from datetime import date

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
    websites: Dict[str, HttpUrl] = Field(default_factory=dict)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    work: List[WorkExp] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    resume_path: Optional[str] = None

class Job(BaseModel):
    id: str
    title: str
    company: str
    url: HttpUrl
    location: Optional[str] = None
    source: str  # greenhouse | lever | workday | ashby | linkedin
    salary: Optional[str] = None
    description_html: Optional[str] = None

class ApplicationPlan(BaseModel):
    job: Job
    resume_variant: str
    cover_letter: Optional[str] = None
    answers: Dict[str, str] = Field(default_factory=dict)
    requires_hitl: bool = True
