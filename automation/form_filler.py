import asyncio, os, re
from playwright.async_api import async_playwright
from .steps.greenhouse_steps import apply_greenhouse
from .steps.lever_steps import apply_lever

SITE_MAP = {
  "greenhouse": apply_greenhouse,
  "lever": apply_lever,
}

async def submit_application(job, plan, hitl_required=True):
    site = job.source
    if site not in SITE_MAP:
        raise ValueError(f"Unsupported site: {site}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=os.getenv("HEADLESS","true").lower()=="true")
        context = await browser.new_context()
        page = await context.new_page()

        # Load job URL and delegate to site-specific flow
        await page.goto(job.url, wait_until="domcontentloaded")
        await SITE_MAP[site](page, job, plan)

        # Optional: present summary for human approval
        if hitl_required:
            # Snapshot / store draft state (screenshot + JSON answers)
            await page.screenshot(path=f"/tmp/{job.id}_review.png")
            # In a real system, pause and await approval via dashboard/webhook.

        # Finalize submission if allowed and approved
        # NOTE: Respect policies/sites.yaml; do not auto-submit when disallowed.

        await context.close()
        await browser.close()