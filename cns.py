import threading
import queue
import time
import random

from config import LOCATIONS, NUM_ANALYSTS, MAX_QUEUE_DEPTH
from tools.memory import Memory
from tools.senses import perform_sweep
from tools.brain import Brain
from tools.server import start_server

mem = Memory()
brain = Brain()

job_queue = queue.Queue()     

def hunter_loop():
    print("[CNS] Booting Hunter (Persistent Mode)...")
    
    # 1. Crash Recovery
    mem.recover_agenda()

    # 2. Boot Check
    if mem.get_agenda_status() == 0:
        print("[CNS] 📭 Agenda empty. Generating initial strategy...")
        autonomous_seeds = brain.generate_initial_strategy()
        if not autonomous_seeds:
            autonomous_seeds = ["AI Engineer", "Robotics Engineer"]
        mem.add_to_agenda(autonomous_seeds, source='SYSTEM')
    else:
        print(f"[CNS] 📅 Resuming with {mem.get_agenda_status()} items in Agenda.")
    
    hunting_active = True
    
    while True:
        # 3. Check for Priority Bypass
        next_item = mem.peek_next_agenda_item()
        
        # Priority if Manual Injection (USER) or Crash Recovery (RECOVERY)
        priority_bypass = False
        if next_item:
            source = next_item.get('source', 'SYSTEM')
            if source in ['USER', 'RECOVERY']:
                priority_bypass = True
                print(f"[CNS] ⚡ Priority Override: Bypassing queue check for '{next_item['term']}' ({source})")

        # 4. Backpressure (with Bypass)
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
            
        # 5. Fetch Agenda (Locks item as PROCESSING)
        term = mem.get_next_agenda_item()
        
        # 6. If Agenda Dry, Replenish (With Cooldowns)
        if not term:
            gravity_term = mem.get_gravitational_term(cooldown_hours=24)
            if gravity_term:
                print(f"[CNS] 🪐 Gravity Pull: Re-queueing high-yield term '{gravity_term}' (Cooldown passed)")
                term = gravity_term
            else:
                print("[CNS] 🧠 Agenda exhausted. Brainstorming new vector...")
                new_terms = brain.generate_initial_strategy()
                filtered_terms = mem.filter_cooldown_terms(new_terms, hours=24)
                
                if filtered_terms:
                    mem.add_to_agenda(filtered_terms)
                    time.sleep(2) 
                    continue
                else:
                    print("[CNS] 😴 All viable strategies on cooldown. Sleeping 60s...")
                    time.sleep(60)
                    continue

        print(f"[CNS] 🔭 Executing Mission: '{term}'")
        
        # 7. Execute Sweep
        loc = random.choice(LOCATIONS)
        is_remote = (loc == "Remote")
        
        results = perform_sweep(term, "USA" if is_remote else loc, is_remote)
        
        new_count = 0
        for job in results:
            if mem.save_job(job):
                job_queue.put(job)
                new_count += 1
        
        # 8. Mark Complete (Delete from Agenda, Log to History)
        mem.mark_agenda_complete(term)
        mem.log_mission_results(term, len(results), new_count, 0)
        
        print(f"[CNS] Hunter found {new_count} new targets (of {len(results)} scraped) for '{term}'")
        
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

        resume, ps_script = brain.pick_resume_and_script(job)
        reason = f"{reason}\n\n### DEPLOYMENT SCRIPT:\n{ps_script}"
        
        if score >= 8 and job_queue.qsize() < 10:
            new_terms = brain.strategize(job)
            filtered = mem.filter_cooldown_terms(new_terms, hours=24)
            if filtered:
                print(f"    >>> EVOLVING: Adding {len(filtered)} terms to Agenda")
                mem.add_to_agenda(filtered, source='EVOLUTION')
        
        mem.update_job(job['url'], score, reason, resume)
        job_queue.task_done()

def status_loop():
    while True:
        mem.export_status(job_queue.qsize())
        time.sleep(2)

if __name__ == "__main__":
    print("=== AUTONOMOUS AGENT BOOT SEQUENCE ===")
    
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=status_loop, daemon=True).start()
    
    if brain.full_resumes:
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