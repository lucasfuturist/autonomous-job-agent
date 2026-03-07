import time
from tools.memory import Memory
from tools.brain import Brain
from config import MIN_SCORE

def run_assimilation():
    print("=== ASSIMILATION PROTOCOL INITIATED ===")
    try:
        mem = Memory()
        brain = Brain()
    except Exception as e:
        print(f"[ASSIMILATION] ❌ Failed to attach tools: {e}")
        return

    # Fetch jobs that are either PENDING or TARGET (we want to re-validate targets too)
    # We ignore REJECTED jobs because that would be a waste of tokens unless we're doing a total reset.
    candidates = mem.get_jobs(status="ALL")
    active_candidates = [j for j in candidates if j['status'] in ['PENDING', 'TARGET']]
    
    print(f"[ASSIMILATION] Re-evaluating {len(active_candidates)} active candidates against new rules...")
    
    rejection_count = 0
    
    for job in active_candidates:
        print(f"[ASSIMILATION] Scanning: {job['company']} - {job['title']}")
        
        # Re-run the brain's evaluation (which now includes the dynamic rules)
        analysis = brain.evaluate(job)
        new_score = int(analysis.get('score', 0))
        new_reason = analysis.get('reason', 'N/A')
        
        # Logic:
        # If score drops below MIN_SCORE (7), we reject it.
        # If it was a TARGET and score remains high, we update the reason just in case.
        
        if new_score < MIN_SCORE:
            print(f"    >>> 📉 DROPPED: Score {new_score}. Reason: {new_reason}")
            mem.update_job(
                job['url'], 
                new_score, 
                f"[ASSIMILATED] {new_reason}", 
                job['selected_resume']
            )
            mem.update_status(job['id'], 'REJECTED')
            rejection_count += 1
        else:
             print(f"    >>> ✅ RETAINED: Score {new_score}.")
             # Optional: Update the reason/score in DB even if it stays valid, 
             # so the UI shows the latest analysis
             mem.update_job(
                job['url'], 
                new_score, 
                new_reason, 
                job['selected_resume']
            )

    print(f"=== ASSIMILATION COMPLETE ===")
    print(f"Total Purged: {rejection_count}")

if __name__ == "__main__":
    run_assimilation()