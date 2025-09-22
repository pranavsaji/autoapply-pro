from sqlalchemy import String, Text, Boolean, Integer, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from apps.api.models.db import Base

class JobRow(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    remote: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String, nullable=True)
    level: Mapped[str | None] = mapped_column(String, nullable=True)
    posted_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    apply_url: Mapped[str | None] = mapped_column(String, nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(String, nullable=True)

    currency: Mapped[str | None] = mapped_column(String, nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_period: Mapped[str | None] = mapped_column(String, nullable=True)

    description_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_raw: Mapped[str | None] = mapped_column(Text, nullable=True)

    hash_sim: Mapped[str | None] = mapped_column(String, nullable=True)
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
