from playwright.async_api import Page
import asyncio

async def apply_greenhouse(page: Page, job, plan):
    # Example selectors vary per company; this is a template.
    # 1) Click "Apply for this job"
    await page.click("text=Apply for this job", timeout=10_000)

    # 2) Upload resume
    if plan.job and plan.job.url:
        # Suppose iframe form
        frames = page.frames
    await page.set_input_files("input[type=file]", plan.job.id and plan.job.id)  # replace with plan.resume path

    # 3) Fill required fields
    await page.fill("input[name='first_name']", plan.answers.get("first_name",""))
    await page.fill("input[name='last_name']", plan.answers.get("last_name",""))
    await page.fill("input[name='email']", plan.answers.get("email",""))

    # 4) Free-text questions
    for q, a in plan.answers.items():
        locator = page.locator(f"textarea[aria-label*='{q[:30]}']")
        if await locator.count():
            await locator.first.fill(a)

    # 5) Submit (IF ALLOWED)
    # await page.click("button[type=submit]")
    await asyncio.sleep(1)