import time
import random
import traceback
import re
from tools.memory import Memory
from duckduckgo_search import DDGS

def clean_company_name(name):
    if not name: return ""
    name = re.sub(r'\(.*?\)', '', name)
    name = name.split(',')[0]
    suffixes = [' inc', ' corp', ' llc', ' ltd', ' limited', ' corporation', ' incorporated']
    name_lower = name.lower()
    for s in suffixes:
        if name_lower.endswith(s):
            name = name[:-(len(s))]
            break
    return name.replace('.', '').strip()

def backfill():
    print("=== RECRUITER RECON BACKFILL PROTOCOL (QUERY: RECRUITER LINKEDIN) ===")
    mem = Memory()
    
    all_jobs = mem.get_jobs(status="ALL")
    targets = [
        j for j in all_jobs 
        if j['status'] in ['TARGET', 'APPLIED', 'INTERVIEW'] 
        and (not j.get('recruiters') or j.get('recruiters') == '')
    ]
    
    total = len(targets)
    print(f"[RECON] Found {total} targets needing recruiter intelligence.")
    
    if total == 0:
        return

    try:
        ddgs = DDGS()
    except Exception as e:
        print(f"[FATAL] Could not initialize DDGS: {e}")
        return
    
    for i, job in enumerate(targets):
        company = job['company']
        print(f"\n[{i+1}/{total}] Scanning: {company}")
        
        try:
            clean_name = clean_company_name(company)
            # Refined Query: Force quotes for exact company match, add 'recruiter' context
            search_query = f'"{clean_name}" recruiter linkedin'
            print(f"    -> Query: [{search_query}]")
            
            results = []
            
            try:
                # 'html' backend is more robust against bot detection than 'api'
                ddgs_results = ddgs.text(search_query, max_results=25, backend='html')
            except Exception as backend_err:
                print(f"    -> [WARN] HTML backend failed ({backend_err}), trying 'lite'...")
                ddgs_results = ddgs.text(search_query, max_results=25, backend='lite')
            
            count_raw = 0
            if ddgs_results:
                for r in ddgs_results:
                    count_raw += 1
                    url = r.get('href', '')
                    title = r.get('title', 'Unknown')
                    
                    print(f"    -> [HIT #{count_raw}]: {url}")
                    
                    if len(results) >= 5: 
                        continue

                    # Strict Filter: Keep only profile URLs
                    if 'linkedin.com/in/' in url:
                        print(f"       -> MATCH: Keeping {title[:30]}...")
                        results.append({
                            "name": title.split('|')[0].strip().split('-')[0].strip(),
                            "title": r.get('body', 'No snippet available')[:100] + "...",
                            "url": url
                        })
                    else:
                        print("       -> SKIP: Not a profile URL.")
            
            if results:
                mem.update_recruiters_by_id(job['id'], results)
                print(f"    -> SUCCESS: Found {len(results)} candidates. Saved.")
            else:
                if count_raw == 0:
                    print("    -> FAIL: 0 results returned (Possible Rate Limit or No Results).")
                else:
                    print(f"    -> FAIL: {count_raw} results found, but 0 were profiles.")
                # Save empty list to prevent infinite loop on this job
                if count_raw > 0:
                    mem.update_recruiters_by_id(job['id'], [])
                
        except Exception as e:
            print(f"    -> ERROR: {e}")
            
        sleep_time = random.uniform(8.0, 12.0)
        print(f"    -> Sleeping {sleep_time:.2f}s...")
        time.sleep(sleep_time)

    print("\n[RECON] Backfill complete.")

if __name__ == "__main__":
    backfill()