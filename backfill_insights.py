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
    
    # We look for jobs where the new schema fields are NULL.
    # We use 'tech_stack_core' as the proxy for "unprocessed".
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
            # A. Re-evaluate using the upgraded Brain prompt
            analysis = brain.evaluate(job)
            
            # B. Check for valid extraction
            score = analysis.get('score', 0)
            
            # --- FULL DEBUG OUTPUT ---
            if mode == 'test':
                print(json.dumps(analysis, indent=2))
            else:
                # Concise output for Final mode
                salary = f"${analysis.get('salary_base_min', 'N/A')}-{analysis.get('salary_base_max', 'N/A')}"
                work_mode = analysis.get('work_mode', 'Unknown')
                stack_len = len(analysis.get('tech_stack_core', []))
                print(f"    -> Score: {score}/10 | Pay: {salary} | Mode: {work_mode} | Stack Items: {stack_len}")

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
                success_count += 1
                
        except Exception as e:
            print(f"    -> [ERROR] Extraction failed: {e}")
        
        # Polite delay for local LLM thermal management
        if mode == 'final':
            time.sleep(1.0) 

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