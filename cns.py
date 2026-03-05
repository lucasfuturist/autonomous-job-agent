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
search_queue = queue.Queue()  
seen_terms = set()

def hunter_loop():
    print("[CNS] Booting Hunter...")
    
    autonomous_seeds = brain.generate_initial_strategy()
    if not autonomous_seeds:
        autonomous_seeds = ["AI Engineer", "Robotics Engineer"]
        
    for t in autonomous_seeds: 
        search_queue.put(t)
        seen_terms.add(t)
        
    print(f"[CNS] Hunter Armed with {len(autonomous_seeds)} schema-locked strategies.")
    
    hunting_active = True
    
    while True:
        current_depth = job_queue.qsize()
        if current_depth >= MAX_QUEUE_DEPTH:
            if hunting_active:
                print(f"[CNS] 🛑 MATCHING MODE ENGAGED. Backlog ({current_depth}) exceeds limit ({MAX_QUEUE_DEPTH}). Hunter sleeping...")
                hunting_active = False
            time.sleep(10)
            continue
        else:
            if not hunting_active:
                print(f"[CNS] 🟢 HUNTING MODE ENGAGED. Backlog cleared ({current_depth}). Resuming sweeps...")
                hunting_active = True
            
        try:
            term = search_queue.get(timeout=5)
        except queue.Empty:
            # GRAVITATIONAL ROUTING: Mathematically pull the highest yielding term
            gravity_term = mem.get_gravitational_term()
            term = gravity_term if gravity_term else random.choice(list(seen_terms))
            print(f"[CNS] 🪐 Gravity Pull: Refocusing on high-yield term '{term}'")
        
        loc = random.choice(LOCATIONS)
        is_remote = (loc == "Remote")
        
        results = perform_sweep(term, "USA" if is_remote else loc, is_remote)
        
        mem.log_mission_results(term, len(results), 0)
        
        new_count = 0
        for job in results:
            if mem.save_job(job):
                job_queue.put(job)
                new_count += 1
        
        print(f"[CNS] Hunter found {new_count} new targets for '{term}'")
        search_queue.task_done()
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
            for t in new_terms:
                if t not in seen_terms:
                    print(f"    >>> EVOLVING: Adding '{t}' to search queue")
                    search_queue.put(t)
                    seen_terms.add(t)
        
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