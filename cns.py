import threading
import queue
import time
import random

from config import LOCATIONS, NUM_ANALYSTS, MAX_QUEUE_DEPTH, MIN_SCORE, SWEEP_BATCH_SIZE, MIN_YIELD_THRESHOLD
from tools.memory import Memory
from tools.senses import perform_sweep
from tools.brain import Brain
from tools.server import start_server

mem = Memory()
brain = Brain()

job_queue = queue.Queue()     

def hunter_loop():
    print("[CNS] Booting Hunter (Persistent Mode)...")
    
    mem.recover_agenda()

    if mem.get_agenda_status() == 0:
        print("[CNS] 📭 Agenda empty. Generating initial data-driven strategy...")
        autonomous_seeds = brain.generate_initial_strategy()
        mem.add_to_agenda(autonomous_seeds, source='SYSTEM')
    else:
        print(f"[CNS] 📅 Resuming with {mem.get_agenda_status()} items in Agenda.")
    
    hunting_active = True
    last_state = None
    
    while True:
        # --- AGENT STATE CHECK ---
        current_state = mem.get_agent_state()
        if current_state != last_state:
            if current_state: 
                print("\n[CNS] 🟢 SYSTEM ACTIVE: Resuming scraping and analysis...")
                mem.set_system_activity("HUNTER", "System Online")
            else: 
                print("\n[CNS] 🛑 SYSTEM OFFLINE: UI & API running. Scraping paused...")
                mem.set_system_activity("HUNTER", "System Offline (Paused)")
            last_state = current_state
            
        if not current_state:
            time.sleep(2)
            continue

        if mem.check_and_clear_purge_flag():
            print("\n[CNS] 🧹 COMMAND OVERRIDE DETECTED. PURGING ANALYST QUEUE...")
            with job_queue.mutex:
                job_queue.queue.clear()
            hunting_active = True

        next_item = mem.peek_next_agenda_item()
        
        priority_bypass = False
        if next_item:
            source = next_item.get('source', 'SYSTEM')
            if source in ['USER', 'RECOVERY']:
                priority_bypass = True

        current_depth = job_queue.qsize()
        if current_depth >= MAX_QUEUE_DEPTH and not priority_bypass:
            if hunting_active:
                print(f"[CNS] 🛑 MATCHING MODE ENGAGED. Backlog ({current_depth}) exceeds limit. Hunter sleeping...")
                mem.set_system_activity("HUNTER", "Sleeping (Queue Full)")
                hunting_active = False
            time.sleep(10)
            continue
        else:
            if not hunting_active:
                print(f"[CNS] 🟢 HUNTING MODE ENGAGED. Backlog cleared ({current_depth}). Resuming sweeps...")
                hunting_active = True
            
        term = mem.get_next_agenda_item()
        
        if not term:
            gravity_term = mem.get_gravitational_term(cooldown_hours=0.5)
            if gravity_term:
                term = gravity_term
            else:
                new_terms = brain.generate_initial_strategy()
                filtered_terms = mem.filter_cooldown_terms(new_terms, hours=0.5)
                
                if filtered_terms:
                    mem.add_to_agenda(filtered_terms)
                    time.sleep(2) 
                    continue
                else:
                    mem.set_system_activity("HUNTER", "Idle (No Targets)")
                    time.sleep(60)
                    continue

        print(f"\n[CNS] 🔭 Executing Mission: '{term}'")
        mem.set_system_activity("HUNTER", f"Sweeping: {term}")
        
        loc = random.choice(LOCATIONS)
        is_remote = (loc == "Remote")
        
        offset = 0
        total_results = 0
        total_new = 0
        interrupted = False
        
        while True:
            # Re-check state mid-mission to allow immediate pausing
            if not mem.get_agent_state():
                interrupted = True
                break

            results = perform_sweep(term, "USA" if is_remote else loc, is_remote, batch_size=SWEEP_BATCH_SIZE, offset=offset)
            if not results: break
                
            batch_new = 0
            for job in results:
                if mem.save_job(job):
                    job_queue.put(job)
                    batch_new += 1
            
            total_results += len(results)
            total_new += batch_new
            yield_rate = batch_new / len(results)
            print(f"  -> Batch Yield: {batch_new} new / {len(results)} scraped ({yield_rate*100:.1f}%)")
            mem.set_system_activity("HUNTER", f"Processing Batch: {batch_new} New / {len(results)} Scraped")
            
            if yield_rate < MIN_YIELD_THRESHOLD: break
            offset += SWEEP_BATCH_SIZE
            time.sleep(random.randint(5, 8))
        
        if interrupted:
            print(f"[CNS] ⏸️ Mission '{term}' paused by user. Returning to queue...")
            mem.reset_mission_status(term)
            time.sleep(1) 
        else:
            mem.mark_agenda_complete(term)
            mem.log_mission_results(term, total_results, total_new, 0)
            time.sleep(random.randint(15, 30))

def analyst_loop(worker_id):
    print(f"[CNS] Analyst-{worker_id} Online.")
    while True:
        # --- AGENT STATE CHECK ---
        if not mem.get_agent_state():
            time.sleep(2)
            continue

        try:
            job = job_queue.get(timeout=5)
        except queue.Empty:
            time.sleep(2)
            continue
            
        print(f"[CNS-{worker_id}] Processing: {job['company']}")
        mem.set_system_activity(f"ANALYST-{worker_id}", f"Evaluating {job['company']}")
        
        analysis = brain.evaluate(job)
        
        # --- SAFELY HANDLE NULL SCORES ---
        raw_score = analysis.get('score')
        score = int(raw_score) if raw_score is not None else 0
        # ---------------------------------
        
        reason = analysis.get('reason', 'N/A')
        
        mem.feedback_mission_quality(job.get('search_term'), score)

        if score >= MIN_SCORE:
            print(f"[CNS-{worker_id}] Target Found: {job['company']} ({score}/10) - Skipping auto-resume to save compute.")
            mem.set_system_activity(f"ANALYST-{worker_id}", f"Target Found: {job['company']}")
            resume = "None"
        else:
            resume = "None"
        
        if score >= 8 and job_queue.qsize() < 10:
            new_terms = brain.strategize(job)
            filtered = mem.filter_cooldown_terms(new_terms, hours=0.5)
            if filtered:
                mem.add_to_agenda(filtered, source='EVOLUTION')
        
        mem.update_job(job['url'], score, reason, resume, analysis_data=analysis)
        job_queue.task_done()

def status_loop():
    while True:
        mem.export_status(job_queue.qsize())
        time.sleep(2)

if __name__ == "__main__":
    print("=== AUTONOMOUS AGENT BOOT SEQUENCE ===")
    
    # --- FORCE INITIAL LOG WRITE ---
    mem.set_system_activity("SYSTEM", "Booting...")
    
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=status_loop, daemon=True).start()
    
    stale_jobs = mem.get_stale_jobs()
    if stale_jobs:
        print(f"[CNS] ⚠️  RECOVERY MODE: Found {len(stale_jobs)} stale targets. Re-analyzing...")
        for j in stale_jobs:
            job_queue.put(j)
    
    threading.Thread(target=hunter_loop, daemon=True).start()
    
    for i in range(NUM_ANALYSTS):
        threading.Thread(target=analyst_loop, args=(i+1,), daemon=True).start()
    
    try:
        while True: time.sleep(100)
    except KeyboardInterrupt:
        print("\n[CNS] Shutting down.")