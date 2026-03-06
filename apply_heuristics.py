import time
import re
from tools.memory import Memory
from config import TITLE_BLACKLIST, COMPANY_BLACKLIST, ALLOWLIST_OVERRIDES

def check_heuristics(title, company):
    title_lower = str(title).lower()
    company_lower = str(company).lower()
    
    # 1. Check Allowlist Pardons (Does this look like a core tech role?)
    is_core_tech = False
    for pattern in ALLOWLIST_OVERRIDES:
        if re.search(pattern, title_lower):
            is_core_tech = True
            break
            
    # 2. Check Strict Company Blacklist (Trash agencies)
    for pattern in COMPANY_BLACKLIST:
        if re.search(pattern, company_lower):
            return f"Blacklisted Company: '{pattern}'"
            
    # 3. Check Strict Title Blacklist
    for pattern in TITLE_BLACKLIST:
        if re.search(pattern, title_lower):
            return f"Blacklisted Title Token: '{pattern}'"
            
    return None

def run_purge():
    start_time = time.time()
    print("=== STARTING SMART HEURISTIC PURGE (BULK MODE) ===")
    try:
        mem = Memory()
    except Exception as e:
        print(f"[FATAL] Could not connect to Memory: {e}")
        return

    # Fetch active jobs (we don't need to re-reject things already rejected)
    jobs = mem.get_jobs(status="ALL")
    active_jobs = [j for j in jobs if j['status'] != 'REJECTED']
    
    print(f"[PURGE] Loaded {len(active_jobs)} active targets. Scanning...")
    
    purge_list = []
    
    # 1. High-Speed Memory Scan
    for job in active_jobs:
        violation = check_heuristics(job['title'], job['company'])
        
        if violation:
            reason = f"Auto-Purged by Smart Heuristics: {violation}"
            # Store tuple of (reason, id) for executemany
            purge_list.append((reason, job['id']))
            # Optional: Print to console so you can see what's caught, 
            # though printing 5000 lines can also slow your terminal down slightly.
            print(f"  -> Flagged: {job['company']} - {job['title']}")
            
    # 2. Single Bulk Database Transaction
    if purge_list:
        print(f"\n[PURGE] Scan complete. Executing bulk database transaction for {len(purge_list)} items...")
        mem.bulk_reject(purge_list)
    
    elapsed = round(time.time() - start_time, 2)
    print(f"[PURGE] Complete. {len(purge_list)} jobs moved to REJECTED in {elapsed} seconds.")

if __name__ == "__main__":
    run_purge()