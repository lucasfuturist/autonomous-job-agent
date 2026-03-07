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
        
        print(f"\n[CNS] 🎯 Generated Strategy (Master List):")
        for i, term in enumerate(autonomous_seeds):
            print(f"  {i+1}. {term}")
        print("\n")
            
        mem.add_to_agenda(autonomous_seeds, source='SYSTEM')
    else:
        print(f"[CNS] 📅 Resuming with {mem.get_agenda_status()} items in Agenda.")
    
    hunting_active = True
    
    while True:
        if mem.check_and_clear_purge_flag():
            print("\n[CNS] 🧹 COMMAND OVERRIDE DETECTED. PURGING ANALYST QUEUE...")
            with job_queue.mutex:
                job_queue.queue.clear()
            print("[CNS] 🧹 Queue cleared. Analysts awaiting new mission targets.\n")
            hunting_active = True

        next_item = mem.peek_next_agenda_item()
        
        priority_bypass = False
        if next_item:
            source = next_item.get('source', 'SYSTEM')
            if source in ['USER', 'RECOVERY']:
                priority_bypass = True
                print(f"[CNS] ⚡ Priority Override: Bypassing queue check for '{next_item['term']}' ({source})")

        current_depth = job_queue.qsize()
        if current_depth >= MAX_QUEUE_DEPTH and not priority_bypass:
            if hunting_active:
                print(f"[CNS] 🛑 MATCHING MODE ENGAGED. Backlog ({current_depth}) exceeds limit. Hunter sleeping...")
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
                print(f"[CNS] 🪐 Gravity Pull: Re-queueing high-yield term '{gravity_term}' (Cooldown passed)")
                term = gravity_term
            else:
                print("[CNS] 🧠 Agenda exhausted. Brainstorming new vector from Master Profile...")
                new_terms = brain.generate_initial_strategy()
                
                print(f"\n[CNS] 🎯 Brainstorm Complete (Master List):")
                for i, t in enumerate(new_terms):
                    print(f"  {i+1}. {t}")
                print("\n")
                
                filtered_terms = mem.filter_cooldown_terms(new_terms, hours=0.5)
                
                if filtered_terms:
                    mem.add_to_agenda(filtered_terms)
                    time.sleep(2) 
                    continue
                else:
                    print("[CNS] 😴 All viable strategies on cooldown (30m). Sleeping 60s...")
                    time.sleep(60)
                    continue

        print(f"\n[CNS] 🔭 Executing Mission: '{term}'")
        
        loc = random.choice(LOCATIONS)
        is_remote = (loc == "Remote")
        
        # --- DYNAMIC YIELD PAGINATION LOOP ---
        offset = 0
        total_results = 0
        total_new = 0
        
        while True:
            results = perform_sweep(term, "USA" if is_remote else loc, is_remote, batch_size=SWEEP_BATCH_SIZE, offset=offset)
            
            if not results:
                break
                
            batch_new = 0
            for job in results:
                if mem.save_job(job):
                    job_queue.put(job)
                    batch_new += 1
            
            total_results += len(results)
            total_new += batch_new
            
            yield_rate = batch_new / len(results)
            print(f"  -> Batch Yield: {batch_new} new / {len(results)} scraped ({yield_rate*100:.1f}%)")
            
            # Check Threshold
            if yield_rate < MIN_YIELD_THRESHOLD:
                print(f"  -> 🛑 Target area exhausted (Yield < {MIN_YIELD_THRESHOLD*100:.0f}%). Concluding mission.")
                break
                
            # If JobSpy fails to paginate properly and returns exact same jobs, yield=0%, breaking the loop safely.
            offset += SWEEP_BATCH_SIZE
            print(f"  -> 🟢 Yield high enough. Paginating deeper (Next Offset: {offset})...")
            time.sleep(random.randint(5, 8)) # Respectful delay between page fetches
        
        # Log final mission totals
        mem.mark_agenda_complete(term)
        mem.log_mission_results(term, total_results, total_new, 0)
        
        print(f"[CNS] Mission Complete: '{term}'. Total: {total_new} new targets isolated.")
        time.sleep(random.randint(15, 30))

def analyst_loop(worker_id):
    print(f"[CNS] Analyst-{worker_id} Online.")
    while True:
        try:
            job = job_queue.get(timeout=5)
        except queue.Empty:
            time.sleep(2)
            continue
            
        print(f"[CNS-{worker_id}] Processing: {job['company']}")
        
        analysis = brain.evaluate(job)
        score = int(analysis.get('score', 0))
        reason = analysis.get('reason', 'N/A')
        
        mem.feedback_mission_quality(job.get('search_term'), score)

        if score >= MIN_SCORE:
            print(f"[CNS-{worker_id}] JIT Assembling Resume for {job['company']}...")
            resume, deployment_notes = brain.build_jit_resume(job)
            if deployment_notes:
                reason = f"{reason}\n\n### DEPLOYMENT SCRIPT:\n{deployment_notes}"
        else:
            resume = "N/A"
        
        if score >= 8 and job_queue.qsize() < 10:
            new_terms = brain.strategize(job)
            filtered = mem.filter_cooldown_terms(new_terms, hours=0.5)
            if filtered:
                print(f"    >>> EVOLVING: Adding {len(filtered)} terms to Agenda")
                mem.add_to_agenda(filtered, source='EVOLUTION')
        
        # --- UPDATE: PASS FULL ANALYSIS TO MEMORY ---
        mem.update_job(job['url'], score, reason, resume, analysis_data=analysis)
        job_queue.task_done()

def status_loop():
    while True:
        mem.export_status(job_queue.qsize())
        time.sleep(2)

if __name__ == "__main__":
    print("=== AUTONOMOUS AGENT BOOT SEQUENCE ===")
    
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