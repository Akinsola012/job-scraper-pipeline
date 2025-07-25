import pandas as pd
from prefect import task, flow
import os

@task
def process_jobs():
    input_path = os.path.join("indeed_scraper", "data", "jobs_enriched.csv")

    print(f"📂 Loading data from {input_path}")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        raise Exception(f"❌ File not found at: {input_path}")

    # Trim whitespace from all text columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Replace placeholder strings with NaN
    df.replace({
        "Unknown Company": pd.NA,
        "Not listed": pd.NA,
        "Not found": pd.NA,
        "Location not found": pd.NA
    }, inplace=True)

    # Add flags based on available data
    df["has_description"] = df["description"].notna()
    df["has_salary"] = df["salary"].notna()
    df["has_location"] = df["location"].notna()
    df["has_company"] = df["company"].notna()

    # Save cleaned data
    output_path = os.path.join("indeed_scraper", "data", "cleaned_jobs.csv")
    df.to_csv(output_path, index=False)
    print(f"💾 Cleaned data saved to {output_path}")

    return f"{len(df)} listings processed and enriched with flags ✅"

@flow(name="JobCleaningFlow")
def job_cleaning_flow():
    result = process_jobs()
    print("✅", result)

if __name__ == "__main__":
    job_cleaning_flow()

  