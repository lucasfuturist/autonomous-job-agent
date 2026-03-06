import hashlib
from jobspy import scrape_jobs
import pandas as pd
from config import SWEEP_DEPTH

def perform_sweep(term, location, is_remote):
    # SMARTER LOCATION DETECTION
    # If the user's command string (term) already contains a city, use it as the location override.
    term_lower = term.lower()
    
    final_location = location
    final_remote = is_remote

    # 1. Check for explicit remote keywords in the term
    if "remote" in term_lower or "work from home" in term_lower:
        final_remote = True
        final_location = "USA"
    
    # 2. If the term has a city but we passed a generic "USA" or "Remote", try to extract the specific city
    # This is a heuristic, but it fixes the "Mid-Level SWE Boston in USA" issue.
    # We check if the last word in the term looks like a city/state combo
    parts = term.split()
    if len(parts) > 1 and not final_remote:
        potential_loc = parts[-1]
        if potential_loc.lower() not in ["engineer", "developer", "manager", "lead", "specialist"]:
            # If the term ends in something that looks like a location, assume it overrides the default
            # "Robotics Engineer Austin" -> Search in "Austin"
            # (JobSpy handles loose location strings well)
            final_location = potential_loc 

    print(f"[SENSES] Exhaustive Sweep: '{term}' in {final_location} (Targeting {SWEEP_DEPTH} roles)...")
    
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location=final_location,
            results_wanted=SWEEP_DEPTH,
            country_usa=True,
            is_remote=final_remote
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
                "location": str(row.get('location', final_location)),
                "search_term": term
            })
        return results
    except Exception as e:
        print(f"[SENSES] API Glitch: {e}")
        return []