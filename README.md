#  Job Scraper & Cleaner – Automated Pipeline for Indeed.com

A fully automated job scraping and cleaning pipeline powered by [Prefect Cloud](https://www.prefect.io) and [Playwright](https://playwright.dev/python/).  


---

##  Features

-  Scrapes job listings from a job website using `playwright`
-  Bypasses authentication and handles paginated job results
-  Cleans and transforms scraped job data with `pandas`
-  Deploys as a scheduled flow to **Prefect Cloud**
-  Optionally exports cleaned data to **Google Sheets**
-  Sends an **email alert every hour** after each successful run
-  Automatically schedules hourly scrapes via Prefect (no agent/worker required)

---

##  Tech Stack

| Layer              | Tool / Library                  |
|--------------------|----------------------------------|
| Web Scraping       | [`playwright`](https://playwright.dev/python/) |
| Data Cleaning      | `pandas`                         |
| Scheduling & Orchestration | [`prefect`](https://docs.prefect.io/) (Cloud) |
| Cloud Dashboard    | [Prefect Cloud](https://app.prefect.cloud) |
| Export to Sheets   | `gspread`, `oauth2client`        |
| Auth Bypass        | JS injection + cookie persistence |
| GitHub Tracking    | `git`, GitHub repo               |
| Notification       | `SMTP`, Prefect email block      |

---

##  Scraping Strategy

Using `Playwright`, the scraper:
- Launches a **headless Chromium** session
- Injects cookies via `context.add_cookies()` for **login bypass**
- Navigates paginated job listings using `Next` button detection
- Extracts:
  - Job title  
  - Company  
  - Location  
  - Salary  
  - Post date
- Stores data into a **CSV** for cleaning

>  Auth Bypass:
> Simulated login once, then reused session by persisting cookies across scraping runs.

---

## ⚙ Deployment Details

The main cleaning flow is deployed using:


- `prefect deploy` command
- Deployment name: `job-cleaning`
- Work pool: `my-managed-pool` (no agent required)
- Source script: `job_script.py` with a `@flow` function: `job_cleaning_flow()`
- Configured to **send email alerts** via Prefect notification blocks every hour.

---
