# apps/api/services/profile_service.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
import json
from fastapi import UploadFile
from apps.api.models.domain import Profile

DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
PROFILE_JSON = DATA_DIR / "profile.json"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def _safe_write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2))
    tmp.replace(path)

def get_profile() -> Optional[Profile]:
    if PROFILE_JSON.exists():
        return Profile(**json.loads(PROFILE_JSON.read_text()))
    return None

def save_profile(p: Profile) -> Profile:
    _safe_write_json(PROFILE_JSON, p.model_dump())
    return p

def _parse_pdf_text(pdf_path: Path) -> str:
    # lightweight, robust parser
    try:
        from pypdf import PdfReader
        text = []
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text).strip()
    except Exception as e:
        return f""  # fail-soft

def _parse_docx_text(docx_path: Path) -> str:
    try:
        import docx
        doc = docx.Document(str(docx_path))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception:
        return ""

def store_upload(file: UploadFile, prefix: str) -> Path:
    ext = Path(file.filename).suffix or ".bin"
    out = UPLOADS_DIR / f"{prefix}{ext}"
    with out.open("wb") as f:
        f.write(file.file.read())
    return out

def attach_resume(file: UploadFile) -> Profile:
    path = store_upload(file, prefix="resume")
    prof = get_profile() or Profile(
        full_name="", email="you@example.com"
    )
    prof.resume_path = str(path.resolve())

    text = ""
    if path.suffix.lower() == ".pdf":
        text = _parse_pdf_text(path)
    elif path.suffix.lower() in {".docx"}:
        text = _parse_docx_text(path)
    prof.resume_text = (text or None)

    return save_profile(prof)

def attach_cover_letter(file: UploadFile) -> Path:
    return store_upload(file, prefix="cover_letter")
