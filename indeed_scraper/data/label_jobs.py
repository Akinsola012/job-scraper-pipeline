import pandas as pd
import os
from urllib.parse import urlparse

# 🚀 Load your scraped data
df = pd.read_csv("data/jobs.csv")

# 🔍 Infer seniority level from job title
def get_seniority(title):
    title = title.lower()
    if "intern" in title: return "Intern"
    if "junior" in title or "entry" in title: return "Junior"
    if "mid" in title or "intermediate" in title: return "Mid"
    if "senior" in title or "sr" in title: return "Senior"
    if "lead" in title or "principal" in title: return "Lead"
    return "Unknown"

# ☁️ Determine if job is remote
def is_remote(title, location):
    title = title.lower()
    location = location.lower()
    if "remote" in title or "remote" in location:
        return "Yes"
    return "No"

# 🔧 Extract tech stack keywords from job title
def extract_tech(title):
    tech_keywords = ["python", "java", "sql", "aws", "react", "node", "docker", "c++", "typescript", "go"]
    title_lower = title.lower()
    return ", ".join([tech for tech in tech_keywords if tech in title_lower]) or "Unlabeled"

# 🏷️ Apply labeling functions
df["seniority_level"] = df["title"].apply(get_seniority)
df["is_remote"] = df.apply(lambda x: is_remote(x["title"], x["location"]), axis=1)
df["tech_stack"] = df["title"].apply(extract_tech)

# 💾 Save labeled dataset
os.makedirs("data", exist_ok=True)
df.to_csv("data/jobs_labeled.csv", index=False)
print(f"✅ Saved labeled ML dataset → data/jobs_labeled.csv with {len(df)} rows")