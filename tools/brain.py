import ollama
import json
import os
import re
import threading
import random
from config import OLLAMA_MODEL, HEAVY_MODEL, MD_FOLDER, CORE_SCHEMA, TITLE_BLACKLIST, COMPANY_BLACKLIST, ALLOWLIST_OVERRIDES, USER_PREFERENCES

class Brain:
    def __init__(self):
        print(f"[BRAIN] Multi-Agent Core Online | Scout: {OLLAMA_MODEL} | Sniper: {HEAVY_MODEL}")
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

    def parse_command(self, user_input):
        prompt = f"""
        Role: Mission Commander.
        User Command: "{user_input}"
        
        Task: Translate this natural language command into a list of 3-5 specific, high-yield job search queries that cover the user's intent.
        CRITICAL RULE: Combine ROLE and LOCATION into single strings.
        
        BAD OUTPUT: ["Robotics", "Seattle", "Jobs"]
        GOOD OUTPUT: ["Robotics Engineer Seattle", "Robotics Engineer Austin", "Mid-Level Systems Engineer Seattle"]
        
        Output JSON: {{"queries": ["term1", "term2", "term3"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                data = json.loads(res['message']['content'])
                return data.get('queries', [])
            except Exception as e:
                print(f"[BRAIN] Command Parse Failed: {e}")
                return [user_input]

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
        # 1. SMART HEURISTIC CHECK (Regex token-based)
        title_lower = str(job.get('title', '')).lower()
        company_lower = str(job.get('company', '')).lower()
        
        for pattern in COMPANY_BLACKLIST:
            if re.search(pattern, company_lower):
                print(f"[BRAIN] 🚫 Hard Reject: Company '{pattern}' matched {job.get('company')}")
                return {"score": 0, "reason": f"Heuristic Reject: Blacklisted Company '{pattern}'"}
                
        for pattern in TITLE_BLACKLIST:
            if re.search(pattern, title_lower):
                print(f"[BRAIN] 🚫 Hard Reject: Title token '{pattern}' matched {job.get('title')}")
                return {"score": 0, "reason": f"Heuristic Reject: Blacklisted Role '{pattern}'"}

        # 2. LOAD DYNAMIC RULES
        dynamic_rules = self._load_dynamic_rules()

        # 3. HIGH-SPEED LLM EVALUATION (THE SCOUT)
        prompt = f"""
        Role: Hostile Technical Gatekeeper.
        
        CANDIDATE PROFILE:
        - Deep Tech Systems Engineer (Python, C++, Robotics, AI Infrastructure).
        - Wants: Founding Engineer, AI Platform, Robotics Middleware, Hard Tech.
        
        ANTI-PERSONA (IMMEDIATE REJECT):
        - NOT a Doctor, Nurse, or Medical Professional.
        - NOT a Civil Engineer (Construction, HVAC, Concrete).
        - NOT a Web Developer (Wordpress, Shopify).
        - NOT IT Support (Helpdesk, SysAdmin).
        
        JOB TO EVALUATE:
        Title: {job['title']}
        Company: {job['company']}
        Description: {job['description'][:2000]}
        
        SCORING RUBRIC:
        - 0-2: MEDICAL/CLINICAL/TRADES. Anything mentioning patients, clinical care, nursing, or manual trades (plumber, mechanic).
        - 3-5: IRRELEVANT TECH. IT Support, pure frontend web dev, or generic "Business Analyst".
        - 6-7: SOFT MATCH. Pure backend software with no hardware/AI angle.
        - 8-10: HARD MATCH. Robotics, AI Systems, LLM Infrastructure, Edge Computing.
        
        DYNAMIC RULES FROM USER:
        {USER_PREFERENCES}
        {dynamic_rules}
        
        Output ONLY valid JSON: {{"score": int, "reason": "Short justification"}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[
                    {'role': 'user', 'content': prompt}
                ], format='json')
                return json.loads(res['message']['content'])
            except Exception as e: 
                return {"score": 0, "reason": f"Brain Fault ({OLLAMA_MODEL}): {e}"}

    def build_jit_resume(self, job):
        master = self._load_master_data()
        if not master:
            return "Default", None

        job_desc = str(job.get('description', ''))[:2000]
        job_title = str(job.get('title', ''))
        company = str(job.get('company', ''))
        
        bullet_catalog = {}
        prompt_bullets = f"Job Title: {job_title}\nCompany: {company}\nDescription:\n{job_desc}\n\nTask: Select the top 15 to 20 relevant bullet IDs. INCLUE adjacent technical context (e.g. if software role, include hardware/robotics context to show systems depth). We want a dense, 2-page resume.\n\nCandidate Bullets:\n"
        
        fallback_ids = []
        for exp in master.get('experience', []):
            for i, b in enumerate(exp.get('standardized_bullets', [])):
                bullet_catalog[b['id']] = b['text']
                prompt_bullets += f"- {b['id']}: {b['text']}\n"
                if i < 6: fallback_ids.append(b['id'])
                
        prompt_bullets += "\nOutput EXACTLY this JSON format and nothing else: {\"selected_ids\": [\"exp_ez_1\", \"exp_stealth_2\"]}"
        
        approved_ids = []
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_bullets}], format='json')
                raw_content = res['message']['content']
                try:
                    data = json.loads(raw_content)
                    if "selected_ids" in data:
                        approved_ids = data["selected_ids"]
                    else:
                        approved_ids = [k for k, v in data.items() if v is True]
                except json.JSONDecodeError:
                    print(f"[BRAIN] JSON parse failed, deploying Regex Extraction...")
                    approved_ids = list(set(re.findall(r'exp_[a-zA-Z0-9]+_\d+', raw_content)))
            except Exception as e:
                print(f"[BRAIN] Bullet Extractor API Failed: {e}")
                
        valid_approved_ids = [i for i in approved_ids if i in bullet_catalog]
        
        if len(valid_approved_ids) < 10:
            print("[BRAIN] LLM too strict, injecting fallback density...")
            valid_approved_ids = list(set(valid_approved_ids + fallback_ids))

        actual_experience_text = "\n".join([f"- {bullet_catalog[i]}" for i in valid_approved_ids[:8]])
        
        prompt_strategy = f"""
        Role: Elite Career Strategist.
        Target Job: {job_title} at {company}
        Job Description Sample: {job_desc[:800]}

        Candidate's ACTUAL Bullets Selected:
        {actual_experience_text}

        TASK: Construct the Strategic Header and Narrative.
        
        1. **target_title**: A specific, professional title adapted for this role (e.g. "Senior Robotics Engineer" or "AI Infrastructure Lead").
        2. **core_competency**: A 3-5 word technical subtitle anchoring the candidate's value (e.g. "Real-Time Perception & Edge AI" or "Deterministic Systems & LLM Ops").
        3. **summary**: A 3-4 sentence professional summary.
           - ANTI-PATTERNS: Do NOT use "Seasoned", "Passionate", "Results-oriented", "I am a...", or generic fluff.
           - STYLE: Dense, narrative, specific. Bridge the candidate's actual work (NASA, Robotics, Stealth Startup) to the specific needs of {company}.
           - TONE: High-Agency Engineering Leader.

        Output ONLY valid JSON: {{ "target_title": "...", "core_competency": "...", "summary": "..." }}
        """
        
        strategy = {
            "target_title": job_title,
            "core_competency": "Systems Engineering & AI Infrastructure",
            "summary": "Dedicated Systems Engineer with a proven track record bridging software architecture, AI integration, and robust hardware automation."
        }
        
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_strategy}], format='json')
                raw_content = res['message']['content']
                data = json.loads(raw_content)
                strategy.update(data)
            except Exception as e:
                print(f"[BRAIN] Strategy Synthesis Failed: {e}")

        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company)
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', job_title)
        filename = f"{clean_company}_{clean_title}_JIT"
        
        md_content = f"""---
target_title: "{strategy['target_title']}"
core_competency: "{strategy['core_competency']}"
---
# Lucas Mougeot

## Professional Summary
{strategy['summary']}

## Relevant Experience
"""
        
        for exp in master.get('experience', []):
            role_bullets = [b for b in exp.get('standardized_bullets', []) if b['id'] in valid_approved_ids]
            role_bullets = role_bullets[:12] 
            
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
        
        Output JSON: {{"terms": ["term1", "term2"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                return json.loads(res['message']['content']).get('terms', [])
            except: return []