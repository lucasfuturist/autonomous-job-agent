import hashlib
from jobspy import scrape_jobs
import pandas as pd
from config import SWEEP_DEPTH

def perform_sweep(term, location, is_remote):
    print(f"[SENSES] Exhaustive Sweep: '{term}' in {location} (Targeting {SWEEP_DEPTH} roles)...")
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location=location,
            results_wanted=SWEEP_DEPTH,
            country_usa=True,
            is_remote=is_remote
        )
        
        results = []
        for _, row in jobs.iterrows():
            url = str(row.get('job_url', ''))
            if not url: continue
            
            company = str(row.get('company', 'Unknown')).strip()
            title = str(row.get('title', 'Unknown')).strip()
            
            results.append({
                "id": hashlib.md5(url.encode()).hexdigest(),
                "company": company,
                "title": title,
                "description": str(row.get('description', '')),
                "url": url,
                "location": str(row.get('location', location)),
                "search_term": term
            })
        return results
    except Exception as e:
        print(f"[SENSES] API Glitch: {e}")
        return []