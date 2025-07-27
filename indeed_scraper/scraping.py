import os, json, asyncio
import pandas as pd
import nest_asyncio
from urllib.parse import urljoin
from playwright.async_api import async_playwright

nest_asyncio.apply()

async def main():
    os.makedirs("data", exist_ok=True)
    query = "python"
    location = "United States"
    results = []

    async with async_playwright() as pw:
        # Connect to manually opened Chrome
        browser = await pw.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()

        base_url = f"https://www.indeed.com/jobs?q={query}&l={location}"
        await page.goto(base_url, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        visited = set()

        while True:
            current_url = page.url
            if current_url in visited:
                break
            visited.add(current_url)

            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            cards = await page.query_selector_all("div.job_seen_beacon")
            for card in cards:
                row = {k: "" for k in [
                    "title", "company", "location", "salary", "remote_or_onsite",
                    "job_type", "date_posted", "rating", "link"
                ]}

                try:
                    row["title"] = await card.eval_on_selector(
                        "h2.jobTitle span", "el => el.innerText.trim()"
                    )
                except: pass

                try:
                    row["company"] = await card.eval_on_selector(
                        "span[data-testid='company-name']", "el => el.innerText.trim()"
                    )
                except: pass

                try:
                    row["location"] = await card.eval_on_selector(
                        "div[data-testid='text-location']", "el => el.innerText.trim()"
                    )
                except: pass

                try:
                    row["salary"] = await card.eval_on_selector(
                        ".salary-snippet", "el => el.innerText.trim()"
                    )
                except: pass

                try:
                    row["date_posted"] = await card.eval_on_selector(
                        "span.date", "el => el.innerText.trim()"
                    )
                except: pass

                try:
                    row["rating"] = await card.eval_on_selector(
                        "span.ratingsContent", "el => el.innerText.trim()"
                    )
                except: pass

                try:
                    partial_link = await card.eval_on_selector(
                        "h2.jobTitle a", "el => el.getAttribute('href')"
                    )
                    row["link"] = urljoin("https://www.indeed.com", partial_link)
                except: pass

                desc = f"{row['title']} {row['company']} {row['location']}".lower()
                row["remote_or_onsite"] = "Remote" if "remote" in desc else "Onsite"
                row["job_type"] = "Internship" if "intern" in desc else "Full-time"

                results.append(row)

            # Move to the next numbered page
            next_btn = await page.query_selector("a[aria-label='Next Page']")
            if not next_btn:
                break
            await next_btn.click()
            await asyncio.sleep(4)

        # Save data
        df = pd.DataFrame(results)
        df = df.loc[:, df.replace("", pd.NA).notna().any()]
        df.to_csv("data/USA_python_jobs.csv", index=False)
        with open("data/USA_python_jobs.json", "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=2)

        print(f"✅ Scraped {len(df)} job listings → Saved to data/USA_python_jobs.csv & data/USA_python_jobs.json")

asyncio.run(main())