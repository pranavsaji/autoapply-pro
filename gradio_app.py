# gradio_app.py
import gradio as gr
import requests
import pandas as pd
from typing import List, Dict, Any, Tuple

API = "http://127.0.0.1:8000"  # FastAPI base

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

def search_jobs(query: str, location: str, limit: int = 50, offset: int = 0
               ) -> Tuple[pd.DataFrame, Dict[str, Any], dict, str]:
    """
    Returns:
      - DataFrame for the table
      - State index: {job_id: job_json}
      - Dropdown update (choices + default value) -> plain dict from gr.update(...)
      - Status message
    """
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
        empty_df = pd.DataFrame(columns=["Job ID", "Title", "Company", "Location", "Source", "URL"])
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
        lines.append(str(desc)[:2000])  # trimmed preview
    return "\n".join(lines)

def plan_application(job_id: str, idx: Dict[str, Any]) -> Dict[str, Any]:
    if not job_id or job_id not in idx:
        return {"error": "No job selected."}
    job = idx[job_id]
    r = requests.post(f"{API}/apply/plan", json=job, timeout=60)
    r.raise_for_status()
    plan = r.json()
    answers = plan.get("answers") or {}
    answers_md = "\n".join([f"- **{k}**: {v}" for k, v in answers.items()]) or "_No answers generated_"
    cl = plan.get("cover_letter") or "_No cover letter generated_"
    return {"Plan JSON": plan, "Answers (formatted)": answers_md, "Cover Letter": cl}

with gr.Blocks(title="AutoApply Pro — Jobs") as demo:
    gr.Markdown("# 🔍 AutoApply Pro — Job Search & Planner")

    with gr.Row():
        query_in = gr.Textbox(label="Query", placeholder="e.g., machine learning, data, ai…", value="")
        loc_in = gr.Textbox(label="Location (optional)", placeholder="e.g., Remote, San Francisco…", value="")
        search_btn = gr.Button("Search", variant="primary")

    status_md = gr.Markdown("")

    results_df = gr.Dataframe(
        headers=["Job ID", "Title", "Company", "Location", "Source", "URL"],
        interactive=False,
        label="Results",
    )

    state_idx = gr.State({})  # {job_id: job_json}

    with gr.Row():
        job_id_dd = gr.Dropdown(label="Select Job ID", choices=[], interactive=True)
        gr.Markdown("(Open the job posting from the table’s URL column)")

    details_md = gr.Markdown("Select a job to see details.")

    plan_btn = gr.Button("Plan Application ✍️", variant="primary")
    plan_json = gr.JSON(label="Raw Plan JSON")
    answers_md = gr.Markdown()
    coverletter_md = gr.Markdown()

    # Search -> table + state + dropdown + status
    search_btn.click(
        search_jobs,
        inputs=[query_in, loc_in],
        outputs=[results_df, state_idx, job_id_dd, status_md],
    ).then(
        job_details,
        inputs=[job_id_dd, state_idx],
        outputs=[details_md],
    )

    # Auto-search on page load (blank filters)
    demo.load(
        search_jobs,
        inputs=[gr.State(""), gr.State("")],   # query, location
        outputs=[results_df, state_idx, job_id_dd, status_md],
    ).then(
        job_details,
        inputs=[job_id_dd, state_idx],
        outputs=[details_md],
    )

    # Changing the dropdown -> refresh details
    job_id_dd.change(
        job_details,
        inputs=[job_id_dd, state_idx],
        outputs=[details_md],
    )

    # Plan Application -> show plan + answers + cover letter
    plan_btn.click(
        plan_application,
        inputs=[job_id_dd, state_idx],
        outputs=[plan_json],
    ).then(
        lambda pj: pj.get("Answers (formatted)", "_No answers_"),
        inputs=[plan_json],
        outputs=[answers_md],
    ).then(
        lambda pj: pj.get("Cover Letter", "_No cover letter_"),
        inputs=[plan_json],
        outputs=[coverletter_md],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7862)
