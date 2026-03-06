import ollama
import json
import os
import re
import threading
import random
from config import OLLAMA_MODEL, MD_FOLDER, CORE_SCHEMA, BLACKLIST_KEYWORDS, USER_PREFERENCES

class Brain:
    def __init__(self):
        print("[BRAIN] Initializing JIT Resume Forge...")
        self.lock = threading.Lock()
        self.feedback_file = "data/tactical_feedback.txt"
        self.master_data_path = "data/master_career_data.json"
        self._ensure_md_folder()

    def _ensure_md_folder(self):
        if not os.path.exists(MD_FOLDER):
            os.makedirs(MD_FOLDER)

    def _load_master_data(self):
        if not os.path.exists(self.master_data_path):
            return None
        try:
            with open(self.master_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[BRAIN] Error loading master data: {e}")
            return None

    def _load_dynamic_rules(self):
        if not os.path.exists(self.feedback_file):
            return "No dynamic rules set."
        try:
            with open(self.feedback_file, "r") as f:
                return f.read().strip()
        except:
            return "Error loading rules."

    def generate_initial_strategy(self):
        sample_universe = random.sample(CORE_SCHEMA, min(len(CORE_SCHEMA), 40))
        
        prompt = f"""
        Role: Tactical Headhunter.
        Candidate Loadouts (Resumes): Dynamic JIT Master Vault (AI, Systems, Robotics)
        Primary Search Universe Sample: {sample_universe}... (and 60+ other niche technical domains)
        
        TASK: Based on the candidate's broad profile and the universe, generate 10 highly specific Job Search Queries.
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

    def build_jit_resume(self, job):
        master = self._load_master_data()
        if not master:
            return "Default", None

        job_desc = str(job.get('description', ''))[:3000]
        job_title = str(job.get('title', ''))
        company = str(job.get('company', ''))
        
        # 1. Batch extraction of relevant bullets
        bullet_catalog = {}
        prompt_bullets = f"Job Title: {job_title}\nCompany: {company}\nDescription:\n{job_desc}\n\nCandidate Experience Bullets:\n"
        
        for exp in master.get('experience', []):
            for b in exp.get('standardized_bullets', []):
                bullet_catalog[b['id']] = b['text']
                prompt_bullets += f"- ID: {b['id']} | {b['text']}\n"
                
        prompt_bullets += "\nSelect the 5 to 7 most highly relevant bullet IDs for this specific job. Output ONLY valid JSON: {\"selected_ids\": [\"id1\", \"id2\"]}"
        
        selected_ids = []
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt_bullets}], format='json')
                data = json.loads(res['message']['content'])
                selected_ids = data.get('selected_ids', [])
            except Exception as e:
                print(f"[BRAIN] JIT Bullet Extraction Failed: {e}")
                selected_ids = list(bullet_catalog.keys())[:5]
                
        # 2. Executive Summary Synthesis
        prompt_summary = f"Job Title: {job_title}\nCompany: {company}\nDescription:\n{job_desc}\n\nWrite a punchy, 3-sentence professional summary for the candidate bridging their background to this specific role's mission. Output ONLY valid JSON: {{\"summary\": \"...\"}}"
        
        summary = "Dedicated Systems Engineer with a proven track record bridging software architecture, AI integration, and robust hardware automation."
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt_summary}], format='json')
                data = json.loads(res['message']['content'])
                summary = data.get('summary', summary)
            except Exception as e:
                print(f"[BRAIN] JIT Summary Extraction Failed: {e}")

        # 3. Assemble Markdown Payload
        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company)
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', job_title)
        filename = f"{clean_company}_{clean_title}_JIT"
        
        md_content = f"# Lucas Mougeot\n\n## Professional Summary\n{summary}\n\n## Relevant Experience\n\n"
        
        for exp in master.get('experience', []):
            role_bullets = [b for b in exp.get('standardized_bullets', []) if b['id'] in selected_ids]
            if role_bullets:
                md_content += f"### {exp['title']} at {exp['company']} ({exp.get('dates', '')})\n"
                for b in role_bullets:
                    md_content += f"- {b['text']}\n"
                md_content += "\n"
                
        md_content += "## Core Skills\n"
        skills = master.get('skills', {})
        for category, items in skills.items():
            md_content += f"- **{category.replace('_', ' ').title()}:** {', '.join(items)}\n"
            
        md_content += "\n## Education\n"
        for ed in master.get('education', []):
            md_content += f"- **{ed['degree']}** | {ed['institution']} \n  *{ed['details']}*\n"
            
        filepath = os.path.join(MD_FOLDER, f"{filename}.md")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
        except Exception as e:
            print(f"[BRAIN] Failed to write JIT resume: {e}")
            
        return filename, None

    def strategize(self, job):
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