from playwright.async_api import Page

async def apply_lever(page: Page, job, plan):
    # Similar logic; selectors must be tailored per form
    await page.click("text=Apply for this job")
    await page.fill("input[name='name']", plan.answers.get("full_name",""))
    await page.fill("input[name='email']", plan.answers.get("email",""))
    # Upload resume, cover letter, etc.