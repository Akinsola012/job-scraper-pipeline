import os, json, asyncio
import pandas as pd
import nest_asyncio
nest_asyncio.apply()

from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright

async def main():
    os.makedirs("data", exist_ok=True)
    query = "python"
    search_location = "Texas"
    results = []

    async with async_playwright() as pw:
        # 🖥️ Connect to manually launched Chrome
        browser = await pw.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()

        base_url = f"https://www.indeed.com/jobs?q={query}&l={search_location}"
        await page.goto(base_url, wait_until="domcontentloaded")
        await asyncio.sleep(5)

        visited = set()

        while True:
            current_url = page.url
            if current_url in visited:
                print("🛑 Already visited this page — stopping")
                break
            visited.add(current_url)

            # 🔽 Scroll to trigger lazy-loaded content
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            print("\n🧭 Page title:", await page.title())
            print("🌐 Current URL:", current_url)

            cards = await page.query_selector_all("div.job_seen_beacon")
            print(f"→ Found {len(cards)} job cards")

            for i, card in enumerate(cards, start=1):
                try:
                    title = await card.eval_on_selector("h2.jobTitle span", "el => el.innerText")

                    # Company name (primary → fallback → URL-based)
                    try:
                        company = await card.eval_on_selector("span.companyName", "el => el.innerText")
                    except:
                        try:
                            company = await card.eval_on_selector("div.companyInfo > span", "el => el.innerText")
                        except:
                            href = await card.eval_on_selector("h2.jobTitle a", "el => el.getAttribute('href')")
                            cmp_value = parse_qs(urlparse(href).query).get("cmp", ["Unknown Company"])[0]
                            company = cmp_value

                    # Location
                    try:
                        location = await card.eval_on_selector("div.companyLocation", "el => el.innerText")
                    except:
                        location = "Location not found"

                    # Job link
                    link = await card.eval_on_selector("h2.jobTitle a", "el => el.href")

                    results.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "link": link
                    })

                except Exception as e:
                    print(f"   ✖ Error scraping card #{i}: {e}")
                    continue

            # ⏭ Try to click the next pagination arrow
            next_page = await page.query_selector("a[aria-label='Next Page']")
            if next_page:
                print("➡️ Clicking 'Next Page' →")
                await next_page.click()
                await asyncio.sleep(6)
            else:
                print("✅ No more pages — scraping complete")
                break

        # 💾 Save results
        with open("data/jobs.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        pd.DataFrame(results).to_csv("data/jobs.csv", index=False)
        print(f"\n✅ Scraped {len(results)} jobs → data/jobs.json & jobs.csv")

asyncio.run(main())