import pandas as pd
import asyncio
import nest_asyncio
nest_asyncio.apply()

from playwright.async_api import async_playwright

# 🔍 Extract salary and description from job page
async def enrich_job_data(row, page):
    await page.goto(row["link"], wait_until="domcontentloaded")
    await asyncio.sleep(3)

    # Scroll to trigger lazy content
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(1)

    try:
        # 📝 Job description
        desc_el = await page.query_selector("div#jobDescriptionText")
        description = await desc_el.inner_text() if desc_el else "Not found"

        # 💰 Salary (if available)
        salary_el = await page.query_selector("span[data-testid='salaryDetail']")
        if not salary_el:
            salary_el = await page.query_selector("div[data-testid='salary-snippet-container']")
        salary = await salary_el.inner_text() if salary_el else "Not listed"

    except Exception as e:
        print(f"   ✖ Error scraping {row['title']}: {e}")
        description = "Error"
        salary = "Error"

    return description, salary

# 🚀 Main enrichment loop
async def main():
    df = pd.read_csv("data/jobs.csv")
    descriptions = []
    salaries = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for i, row in df.iterrows():
            print(f"🔎 Scraping job {i+1}/{len(df)}: {row['title']}")
            desc, sal = await enrich_job_data(row, page)
            descriptions.append(desc)
            salaries.append(sal)

        await browser.close()

    df["description"] = descriptions
    df["salary"] = salaries
    df.to_csv("data/jobs_enriched.csv", index=False)
    print(f"\n✅ Saved enriched dataset → data/jobs_enriched.csv")

asyncio.run(main())