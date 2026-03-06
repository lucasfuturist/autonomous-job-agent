import hashlib
from jobspy import scrape_jobs
import pandas as pd

def perform_sweep(term, location, is_remote, batch_size=30, offset=0):
    # SMARTER LOCATION DETECTION
    term_lower = term.lower()
    final_location = location
    final_remote = is_remote

    if "remote" in term_lower or "work from home" in term_lower:
        final_remote = True
        final_location = "USA"
    
    parts = term.split()
    if len(parts) > 1 and not final_remote:
        potential_loc = parts[-1]
        if potential_loc.lower() not in ["engineer", "developer", "manager", "lead", "specialist"]:
            final_location = potential_loc 

    print(f"[SENSES] Deep Sweep: '{term}' in {final_location} (Batch: {batch_size}, Offset: {offset})...")
    
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location=final_location,
            results_wanted=batch_size,
            offset=offset,
            country_usa=True,
            is_remote=final_remote
        )
        
        results = []
        if jobs is None or len(jobs) == 0:
            return results

        for _, row in jobs.iterrows():
            url = str(row.get('job_url', ''))
            if not url: continue
            
            company = str(row.get('company', 'Unknown')).strip()
            title = str(row.get('title', 'Unknown')).strip()
            
            raw_loc = str(row.get('location', final_location)).strip()
            if final_remote and 'remote' not in raw_loc.lower():
                raw_loc = f"Remote - {raw_loc}"

            results.append({
                "id": hashlib.md5(url.encode()).hexdigest(),
                "company": company,
                "title": title,
                "description": str(row.get('description', '')),
                "url": url,
                "location": raw_loc,
                "search_term": term
            })
        return results
    except Exception as e:
        print(f"[SENSES] API Glitch: {e}")
        return []