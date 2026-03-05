import ollama
import json
import os
import glob
import re
import threading
import random
from config import OLLAMA_MODEL, MD_FOLDER, CORE_SCHEMA, BLACKLIST_KEYWORDS, USER_PREFERENCES

class Brain:
    def __init__(self):
        print("[BRAIN] Loading Full Resume Database into Memory...")
        self.full_resumes = self._load_full_resumes()
        self.lock = threading.Lock()
        self.feedback_file = "data/tactical_feedback.txt"

    def _load_full_resumes(self):
        resumes = {}
        if not os.path.exists(MD_FOLDER): return resumes
        search_pattern = os.path.join(MD_FOLDER, "**", "*.md")
        for md_path in glob.glob(search_pattern, recursive=True):
            if "_meta" in md_path: continue
            base_name = os.path.basename(md_path).replace('.md', '')
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    resumes[base_name] = f.read()
            except: pass
        print(f"[BRAIN] Armed with {len(resumes)} full-text tactical loadouts.")
        return resumes

    def _load_dynamic_rules(self):
        if not os.path.exists(self.feedback_file):
            return "No dynamic rules set."
        try:
            with open(self.feedback_file, "r") as f:
                return f.read().strip()
        except:
            return "Error loading rules."

    def generate_initial_strategy(self):
        # Slightly more aggressive generation
        if not self.full_resumes: return []

        resume_names = "\n".join(list(self.full_resumes.keys()))
        
        # We sample the universe to prevent token overflow while maintaining variety on boot
        # Sample 40 terms from the massive list to show the LLM what we mean
        sample_universe = random.sample(CORE_SCHEMA, min(len(CORE_SCHEMA), 40))
        
        prompt = f"""
        Role: Tactical Headhunter.
        Candidate Loadouts (Resumes): {resume_names}
        Primary Search Universe Sample: {sample_universe}... (and 60+ other niche technical domains)
        
        TASK: Based on the resumes and the universe, generate 10 highly specific Job Search Queries.
        Focus on:
        1. High-yield titles (e.g., 'Founding Systems Engineer', 'Robotics Integrator')
        2. Niche tech (e.g., 'Deterministic RAG', 'Computational Geometry')
        3. Hardware-Software bridges.
        
        Output JSON: {{"terms": ["term1", "term2", ...]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                data = json.loads(res['message']['content'])
                terms = data.get('terms', [])
                clean_terms = [t.replace("Lucas Mougeot", "").strip() for t in terms]
                return clean_terms
            except: 
                # Fallback: Pick 5 random high-value terms from the schema if LLM fails
                return random.sample(CORE_SCHEMA, 5)
    
    def evaluate(self, job):
        # 1. HARD HEURISTIC CHECK (Save GPU cycles)
        job_text = (str(job.get('title', '')) + " " + str(job.get('company', ''))).lower()
        for term in BLACKLIST_KEYWORDS:
            if term.lower() in job_text:
                print(f"[BRAIN] 🚫 Hard Reject: '{term}' found in {job.get('company')}")
                return {"score": 0, "reason": f"Heuristic Reject: Blacklisted term '{term}' detected."}

        # 2. LOAD DYNAMIC RULES
        dynamic_rules = self._load_dynamic_rules()

        # 3. LLM EVALUATION WITH PREFERENCES & DYNAMIC RULES
        prompt = f"""
        Role: Career Strategist.
        Task: Score job 1-10 for a versatile Software/Hardware Engineer.
        
        BASE PREFERENCES:
        {USER_PREFERENCES}

        DYNAMIC CONSTRAINTS (HIGHEST PRIORITY):
        {dynamic_rules}
        
        SCORING RUBRIC:
        - 0: BLACKLIST/REJECT (Matches Negative Constraints).
        - 9-10: Perfect Match. High Agency, AI/Robotics, Founding Role.
        - 7-8: Good Match. Strong Software Engineering, Data Engineering, or Hardware roles.
        - 5-6: Decent. Generic Tech roles (Web Dev, QA) or "Senior" roles that are reachable.
        - 1-4: Reject. Sales, HR, Nursing, Truck Driving, or completely non-technical.
        
        Output JSON: {{"score": int, "reason": "Short justification"}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': f"Title: {job['title']}\nDesc: {job['description'][:2000]}"}
                ], format='json')
                return json.loads(res['message']['content'])
            except Exception as e: 
                return {"score": 0, "reason": f"Brain Fault: {e}"}

    def pick_resume_and_script(self, job):
        if not self.full_resumes: return "Default", "# No resumes loaded."

        job_title = str(job['title']).lower()
        job_text = (job_title + " " + str(job['description'])).lower()
        job_words = set(re.findall(r'\b[a-z0-9]{5,}\b', job_text))
        
        scores = {}
        for name, text in self.full_resumes.items():
            text_lower = text.lower()
            name_lower = name.lower()
            scores[name] = sum(1 for w in job_words if w in text_lower)
            for title_word in re.findall(r'\b[a-z0-9]{4,}\b', job_title):
                if title_word in name_lower: scores[name] += 15 
            
        winner = max(scores, key=scores.get) if scores else list(self.full_resumes.keys())[0]

        clean_company = re.sub(r'[^a-zA-Z0-9]', '', str(job['company']))
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', str(job['title']))
        
        ps_script = f"""$dest = "C:\\projects\\pdf2md\\submitted_pdfs\\Lucas_Mougeot_{clean_company}_{clean_title}.pdf"\nCopy-Item -Path "C:\\projects\\pdf2md\\input_pdfs\\{winner}.pdf" -Destination $dest\n(Get-Item $dest).LastWriteTime = (Get-Date)\nAdd-Content -Path "C:\\projects\\pdf2md\\submitted_pdfs\\submissions.md" -Value "- **{job['company']}** | {job['title']} | Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm') | Resume: {winner}"\n"""
        return winner, ps_script

    def strategize(self, job):
        # Sample universe for pivot context
        sample_universe = random.sample(CORE_SCHEMA, min(len(CORE_SCHEMA), 20))
        
        prompt = f"""
        Target Identified: "{job['title']}".
        Your Search Universe Sample: {sample_universe}
        
        Suggest 2 search terms that would find 'neighboring' roles.
        If it's a software role, suggest a hardware/systems equivalent.
        If it's a robotics role, suggest an AI infrastructure equivalent.
        
        Output JSON: {{"terms": ["term1", "term2"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                return json.loads(res['message']['content']).get('terms', [])
            except: return []