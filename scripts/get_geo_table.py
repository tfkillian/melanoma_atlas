import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Read URLs from text file
with open("GEO_urls.txt", "r") as f:
    geo_urls = [line.strip() for line in f if line.strip()]

# Define fields to extract
FIELDS = ["Title", "Organism", "Overall Design", "Status", "Submission date", "Last update date", "Series accession", "Summary"]

# Helper function to extract metadata
def extract_geo_metadata(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="formTable")
        rows = table.find_all("tr") if table else []

        metadata = {"URL": url}
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].text.strip().rstrip(":")
                value = cols[1].text.strip()
                if key in FIELDS:
                    metadata[key] = value

        # Fallback if some fields are missing
        for field in FIELDS:
            metadata.setdefault(field, "")

        return metadata
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return {"URL": url, **{field: "ERROR" for field in FIELDS}}

# Scrape all GEO entries
all_metadata = []
for url in geo_urls:
    metadata = extract_geo_metadata(url)
    all_metadata.append(metadata)
    time.sleep(1)  # polite delay to avoid hammering NCBI servers

# Convert to DataFrame
df = pd.DataFrame(all_metadata)

# Save to TSV
df.to_csv("geo_metadata_summary.tsv", sep="\t", index=False)
print("Metadata summary saved to geo_metadata_summary.tsv")
