import sys
import time
import sqlite3
import json
from tools.memory import Memory
from tools.brain import Brain

def run_backfill(mode):
    print(f"=== INSIGHT EXTRACTION BACKFILL ({mode.upper()} MODE) ===")
    
    mem = Memory()
    brain = Brain()
    
    # 1. Identify Candidates
    conn = mem._get_conn()
    conn.row_factory = sqlite3.Row
    
    print("[BACKFILL] Querying database for unprocessed targets...")
    cursor = conn.execute("""
        SELECT * FROM jobs 
        WHERE tech_stack_core IS NULL 
        AND status != 'REJECTED'
        ORDER BY found_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    jobs = [dict(row) for row in rows]
    total_jobs = len(jobs)
    
    print(f"[BACKFILL] Found {total_jobs} eligible jobs.")
    
    if total_jobs == 0:
        print("[BACKFILL] No jobs need processing. System is up to date.")
        return

    # 2. Configure Limits based on Mode
    if mode == 'test':
        print("[MODE] TEST: limiting to 5 jobs, NO DB WRITES.")
        process_queue = jobs[:5]
    elif mode == 'final':
        print("[MODE] FINAL: Processing ALL jobs, WRITING to DB.")
        process_queue = jobs
    else:
        print(f"[ERROR] Unknown mode '{mode}'. Use 'test' or 'final'.")
        return

    # 3. Execution Loop
    success_count = 0
    
    for i, job in enumerate(process_queue):
        print(f"\n[{i+1}/{len(process_queue)}] Analyzing: {job['company']} - {job['title']}")
        
        try:
            # A. Evaluate using the single-pass extraction prompt
            analysis = brain.evaluate(job)
            
            # B. ALWAYS print the full JSON payload for debugging
            print(json.dumps(analysis, indent=2))
            
            score = analysis.get('score', 0)

            # C. Persist (Final Mode Only)
            if mode == 'final':
                existing_resume = job.get('selected_resume', 'Default')
                
                mem.update_job(
                    url=job['url'],
                    score=score,
                    reason=analysis.get('reason', 'Backfilled'),
                    resume=existing_resume,
                    analysis_data=analysis
                )
                print(f"    -> [SAVED] {job['company']} updated in Database.")
                success_count += 1
                
        except BaseException as e:
            # Catch BaseException and use repr(e) to expose hidden HTTP timeouts
            print(f"    -> [CRITICAL ERROR] Extraction failed for {job['company']}: {repr(e)}")
            print("    -> Skipping to next job to keep batch alive...")
        
        # Polite delay for local LLM thermal management (allow VRAM to flush)
        if mode == 'final':
            time.sleep(2.0) 

    print(f"\n=== BACKFILL COMPLETE ===")
    if mode == 'test':
        print(f"Analyzed {len(process_queue)} jobs in TEST mode. No changes made.")
        print("Run 'python backfill_insights.py final' to apply changes.")
    else:
        print(f"Successfully backfilled {success_count}/{total_jobs} jobs.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backfill_insights.py [test|final]")
    else:
        run_backfill(sys.argv[1].lower())