import time
from tools.memory import Memory
from config import BLACKLIST_KEYWORDS

def run_purge():
    print("=== STARTING HEURISTIC PURGE ===")
    try:
        mem = Memory()
    except Exception as e:
        print(f"[FATAL] Could not connect to Memory: {e}")
        return

    # Fetch all jobs regardless of status to catch anything slipping through
    jobs = mem.get_jobs(status="ALL")
    print(f"[PURGE] Scanning {len(jobs)} total jobs against blacklist...")
    print(f"[CONFIG] Blacklist: {BLACKLIST_KEYWORDS}")
    
    count = 0
    for job in jobs:
        # Check title and company
        title = str(job['title']).lower()
        company = str(job['company']).lower()
        text = f"{title} {company}"
        
        violation = None
        for term in BLACKLIST_KEYWORDS:
            if term.lower() in text:
                violation = term
                break
        
        # If active/pending and violates, kill it.
        # If already rejected, we skip to save DB writes, unless we want to update the reason.
        if violation and job['status'] != 'REJECTED':
            print(f"[REJECTING] {job['company']} - {job['title']} (Hit: '{violation}')")
            
            # 1. Update Score/Reason
            mem.update_job(
                job['url'], 
                0, 
                f"Auto-Purged by Heuristics: Found '{violation}'", 
                job['selected_resume']
            )
            
            # 2. Force Status (Because update_job logic might be conditional)
            mem.update_status(job['id'], 'REJECTED')
            count += 1
            
    print(f"\n[PURGE] Complete. {count} jobs moved to REJECTED.")

if __name__ == "__main__":
    run_purge()