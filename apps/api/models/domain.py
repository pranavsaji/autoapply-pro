from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Optional, Dict
from datetime import date

class WorkExp(BaseModel):
    company: str
    title: str
    start: date
    end: Optional[date]
    highlights: List[str] = []
    technologies: List[str] = []

class Education(BaseModel):
    school: str
    degree: str
    start: date
    end: date

class Profile(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str]
    location: Optional[str]
    websites: Dict[str, HttpUrl] = {}
    summary: Optional[str]
    skills: List[str] = []
    work: List[WorkExp] = []
    education: List[Education] = []
    resume_path: Optional[str]

class Job(BaseModel):
    id: str
    title: str
    company: str
    url: HttpUrl
    location: Optional[str]
    source: str  # greenhouse|lever|workday|ashby|linkedin
    salary: Optional[str]
    description_html: Optional[str]

class ApplicationPlan(BaseModel):
    job: Job
    resume_variant: str
    cover_letter: Optional[str]
    answers: Dict[str, str] = {}
    requires_hitl: bool = True