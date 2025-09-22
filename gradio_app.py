# gradio_app.py
import gradio as gr
import requests
import pandas as pd
from typing import List, Dict, Any, Tuple
import json
from urllib.parse import urlparse
from pathlib import Path
import mimetypes

API = "http://127.0.0.1:8000"

# ---------- helpers ----------
def _rows_from_jobs(jobs: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = [{
        "Job ID": str(j.get("id", "")),
        "Title": j.get("title", ""),
        "Company": j.get("company", ""),
        "Location": j.get("location") or "",
        "Source": j.get("source", ""),
        "URL": j.get("url", ""),
    } for j in jobs]
    return pd.DataFrame(rows, columns=["Job ID", "Title", "Company", "Location", "Source", "URL"])

def _is_valid_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def _guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"

# ---------- Profile API calls ----------
def api_get_profile() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API}/profile/me", timeout=10)
        if r.status_code == 200 and r.text:
            return r.json() or {}
    except Exception:
        pass
    return {}

def api_save_profile(full_name, email, phone, location, summary, skills_csv, websites_json) -> Dict[str, Any]:
    # Parse & sanitize websites JSON to avoid Pydantic URL errors
    websites: Dict[str, str] = {}
    try:
        if (websites_json or "").strip():
            raw = json.loads(websites_json)
            if isinstance(raw, dict):
                websites = {k: v for k, v in raw.items() if isinstance(v, str) and _is_valid_url(v)}
    except Exception:
        websites = {}

    skills = [s.strip() for s in (skills_csv or "").split(",") if s.strip()]
    prof = {
        "full_name": full_name or "",
        "email": email or "",           # must be a valid email
        "phone": phone or None,
        "location": location or None,
        "websites": websites,           # now Pydantic-safe
        "summary": (summary or None),
        "skills": skills,
        "work": [],
        "education": [],
        "resume_path": None,            # set by /profile/upload after upload
    }
    try:
        r = requests.post(f"{API}/profile/save", json=prof, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        # Surface server validation message if present
        try:
            return {"error": f"/profile/save failed: {e}", "detail": r.json()}
        except Exception:
            return {"error": f"/profile/save failed: {e}"}
    except Exception as e:
        return {"error": f"/profile/save failed: {e}"}

def api_upload_files(resume_path: str | None, cover_letter_path: str | None) -> Dict[str, Any]:
    files = {}
    try:
        if resume_path:
            rp = Path(resume_path)
            files["resume"] = (rp.name or "resume.pdf", open(rp, "rb"), _guess_mime(rp.name))
        if cover_letter_path:
            cp = Path(cover_letter_path)
            files["cover_letter"] = (cp.name or "cover_letter.txt", open(cp, "rb"), _guess_mime(cp.name))
        if not files:
            return {"error": "No files selected."}
        r = requests.post(f"{API}/profile/upload", files=files, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": f"/profile/upload failed: {e}"}
    finally:
        # close file handles if opened
        for k, v in list(files.items()):
            try:
                v[1].close()
            except Exception:
                pass

# ---------- Jobs API ----------
def search_jobs(query: str, location: str, limit: int = 50, offset: int = 0
               ) -> Tuple[pd.DataFrame, Dict[str, Any], dict, str]:
    try:
        params = {"limit": limit, "offset": offset}
        if query: params["query"] = query
        if location: params["location"] = location
        r = requests.get(f"{API}/discovery/search", params=params, timeout=20)
        r.raise_for_status()
        jobs: List[Dict[str, Any]] = r.json()
        idx = {str(j["id"]): j for j in jobs}
        df = _rows_from_jobs(jobs)
        choices = list(idx.keys())
        dd_update = gr.update(choices=choices, value=(choices[0] if choices else None))
        return df, idx, dd_update, f"Fetched {len(jobs)} job(s)."
    except Exception as e:
        empty_df = pd.DataFrame(columns=["Job ID","Title","Company","Location","Source","URL"])
        return empty_df, {}, gr.update(choices=[], value=None), f"Search error: {e}"

def job_details(job_id: str, idx: Dict[str, Any]) -> str:
    if not job_id or job_id not in idx:
        return "Select a job to see details."
    j = idx[job_id]
    lines = [
        f"**{j.get('title','')}** @ **{j.get('company','')}**",
        f"Location: {j.get('location') or 'N/A'}",
        f"Source: `{j.get('source','')}`",
    ]
    url = j.get("url")
    if url:
        lines.append(f"[Open Posting]({url})")
    desc = j.get("description_html") or ""
    if desc:
        lines.append("\n---\n")
        # keep raw HTML preview short; the API response can be long
        lines.append(str(desc)[:2000])
    return "\n".join(lines)

def plan_application(job_id: str, idx: Dict[str, Any]) -> Dict[str, Any]:
    if not job_id or job_id not in idx:
        return {"Plan JSON": {"error": "No job selected."}, "Answers (formatted)": "_No answers_", "Cover Letter": "_No cover letter_"}
    job = idx[job_id]
    try:
        r = requests.post(f"{API}/apply/plan", json=job, timeout=90)
        r.raise_for_status()
        plan = r.json()
        answers = (plan or {}).get("answers") or {}
        answers_md = "\n".join([f"- **{k}**: {v}" for k, v in answers.items()]) or "_No answers generated_"
        cl = (plan or {}).get("cover_letter") or "_No cover letter generated_"
        return {"Plan JSON": plan, "Answers (formatted)": answers_md, "Cover Letter": cl}
    except requests.HTTPError as e:
        try:
            detail = r.json()
        except Exception:
            detail = None
        return {
            "Plan JSON": {"error": f"/apply/plan failed: {e}", "detail": detail},
            "Answers (formatted)": "_Error_",
            "Cover Letter": "_Error_",
        }
    except Exception as e:
        return {
            "Plan JSON": {"error": f"/apply/plan failed: {e}"},
            "Answers (formatted)": "_Error_",
            "Cover Letter": "_Error_",
        }

# ---------- UI ----------
with gr.Blocks(title="AutoApply Pro") as demo:
    gr.Markdown("# ⚙️ AutoApply Pro")

    with gr.Tabs():
        # -------- Profile Tab --------
        with gr.Tab("Profile"):
            gr.Markdown("Upload your resume and optional cover letter, then save contact details.")
            with gr.Row():
                resume_u = gr.File(label="Resume (PDF/DOCX preferred)", file_count="single", type="filepath")
                cl_u = gr.File(label="Cover Letter (optional)", file_count="single", type="filepath")
            upload_btn = gr.Button("Upload Files")
            upload_status = gr.JSON(label="Upload Result")

            gr.Markdown("**Contact details**")
            with gr.Row():
                full_name = gr.Textbox(label="Full name")
                email = gr.Textbox(label="Email")
            with gr.Row():
                phone = gr.Textbox(label="Phone (optional)")
                location = gr.Textbox(label="Location (optional)")

            summary = gr.Textbox(label="Summary (optional)", lines=3, placeholder="1-2 lines about you")
            skills_csv = gr.Textbox(label="Skills (comma-separated)", placeholder="python, spark, sql, ...")
            websites_json = gr.Textbox(
                label="Websites JSON (optional)",
                placeholder='{"github":"https://github.com/you","linkedin":"https://www.linkedin.com/in/you"}'
            )

            with gr.Row():
                load_prof_btn = gr.Button("Load Saved Profile")
                save_prof_btn = gr.Button("Save Profile")

            prof_json = gr.JSON(label="Current Profile / Errors")

            # wiring for profile tab
            upload_btn.click(
                lambda r, c: api_upload_files(r, c),
                inputs=[resume_u, cl_u],
                outputs=[upload_status],
            )

            def _fill_from_profile(p: Dict[str, Any]):
                return (
                    p.get("full_name",""),
                    p.get("email",""),
                    p.get("phone","") or "",
                    p.get("location","") or "",
                    p.get("summary","") or "",
                    ", ".join(p.get("skills",[])),
                    ""  # don't prefill websites_json to avoid accidental invalid JSON
                )

            load_prof_btn.click(
                api_get_profile,
                inputs=[],
                outputs=[prof_json],
            ).then(
                _fill_from_profile,
                inputs=[prof_json],
                outputs=[full_name, email, phone, location, summary, skills_csv, websites_json]
            )

            save_prof_btn.click(
                api_save_profile,
                inputs=[full_name, email, phone, location, summary, skills_csv, websites_json],
                outputs=[prof_json],
            )

        # -------- Jobs Tab --------
        with gr.Tab("Jobs"):
            gr.Markdown("## 🔍 Job Search & Planner")
            with gr.Row():
                query_in = gr.Textbox(label="Query", placeholder="e.g., machine learning, data, ai…", value="")
                loc_in = gr.Textbox(label="Location (optional)", placeholder="e.g., Remote, San Francisco…", value="")
                search_btn = gr.Button("Search", variant="primary")
            status_md = gr.Markdown("")
            results_df = gr.Dataframe(headers=["Job ID","Title","Company","Location","Source","URL"], interactive=False, label="Results")
            state_idx = gr.State({})
            with gr.Row():
                job_id_dd = gr.Dropdown(label="Select Job ID", choices=[], interactive=True)
                gr.Markdown("(Open the job posting from the table’s URL column)")
            details_md = gr.Markdown("Select a job to see details.")
            plan_btn = gr.Button("Plan Application ✍️", variant="primary")
            plan_json = gr.JSON(label="Raw Plan JSON")
            answers_md = gr.Markdown()
            coverletter_md = gr.Markdown()

            search_btn.click(
                search_jobs,
                inputs=[query_in, loc_in],
                outputs=[results_df, state_idx, job_id_dd, status_md],
            ).then(
                job_details,
                inputs=[job_id_dd, state_idx],
                outputs=[details_md],
            )

            demo.load(
                search_jobs,
                inputs=[gr.State(""), gr.State("")],
                outputs=[results_df, state_idx, job_id_dd, status_md],
            ).then(
                job_details,
                inputs=[job_id_dd, state_idx],
                outputs=[details_md],
            )

            job_id_dd.change(job_details, inputs=[job_id_dd, state_idx], outputs=[details_md])

            plan_btn.click(
                plan_application,
                inputs=[job_id_dd, state_idx],
                outputs=[plan_json],
            ).then(
                lambda pj: (pj or {}).get("Answers (formatted)", "_No answers_"),
                inputs=[plan_json],
                outputs=[answers_md],
            ).then(
                lambda pj: (pj or {}).get("Cover Letter", "_No cover letter_"),
                inputs=[plan_json],
                outputs=[coverletter_md],
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7862)
