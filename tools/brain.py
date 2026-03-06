import ollama
import json
import os
import re
import threading
import random
from config import OLLAMA_MODEL, HEAVY_MODEL, MD_FOLDER, TITLE_BLACKLIST, COMPANY_BLACKLIST, ALLOWLIST_OVERRIDES, USER_PREFERENCES, MAX_COMMUTE_MILES, INITIAL_SEARCH_TERMS

class Brain:
    def __init__(self):
        print(f"[BRAIN] Multi-Agent Core Online | Scout: {OLLAMA_MODEL} | Sniper: {HEAVY_MODEL}")
        self.lock = threading.Lock()
        self.feedback_file = "data/tactical_feedback.txt"
        self.master_data_path = "data/master_career_data.json"
        self._ensure_md_folder()

        from tools.memory import Memory
        self.MemoryClass = Memory

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
        # We completely bypass the LLM hallucination phase.
        # We load the user's hardcoded 100-item Master List and shuffle it.
        # This creates the exact "exhaust one search, move to the next" queue behavior requested.
        print("[BRAIN] Loading Curated Master Target List...")
        
        terms = INITIAL_SEARCH_TERMS.copy()
        random.shuffle(terms)
        return terms
    
    def evaluate(self, job):
        # 0. PRE-COGNITION GEOFENCE (Save GPU cycles)
        location = job.get('location', '')
        if location:
            mem_instance = self.MemoryClass()
            distance = mem_instance.get_or_fetch_distance(location)
            
            if distance is not None:
                # -1.0 is Remote
                if distance != -1.0 and distance > MAX_COMMUTE_MILES:
                    print(f"[BRAIN] 🛑 Geofence Reject: '{job['company']}' is {distance} miles away in {location}.")
                    return {"score": 0, "reason": f"Geofence Reject: {distance} miles away (Max allowed: {MAX_COMMUTE_MILES} mi). Not remote."}

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
        Role: Ruthless, Strictly Factual Technical Resume Writer.
        Target Job: {job_title} at {company}
        Job Description Context: {job_desc[:800]}

        Candidate's ACTUAL Approved Experience for this role:
        {actual_experience_text}

        TASK: Construct the Strategic Header and Narrative.
        
        1. **target_title**: A specific, professional title adapted for this role (e.g. "Senior Robotics Engineer" or "AI Infrastructure Lead").
        2. **core_competency**: A 3-5 word technical subtitle anchoring the candidate's value (e.g. "Real-Time Perception & Edge AI" or "Deterministic Systems & LLM Ops").
        3. **summary**: A punchy, 3-4 sentence professional summary.

        ABSOLUTE ZERO-HALLUCINATION RULES FOR SUMMARY:
        - ZERO DOMAIN INFERENCE: You are FORBIDDEN from claiming the candidate has experience in {company}'s specific domain (e.g., "Ion Traps", "Human-Machine Teaming", "Aerospace Logistics") UNLESS those exact words appear in the Candidate's ACTUAL Experience text above.
        - DO NOT SHAPE-SHIFT: Do not state the candidate is an "Expert in [Target Job Title]" if they have never held that title.
        - FACT-BASED ALIGNMENT: State ONLY the hardware, software, and systems the candidate has factually built. Frame those TRUE skills as the reason they are highly capable of solving {company}'s engineering problems.
        - ANTI-PATTERNS: Do NOT use "Seasoned", "Passionate", "Results-oriented", "I am a...", or generic fluff.

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

        # --- DYNAMIC SKILLS EXTRACTION START ---
        print(f"[BRAIN] Tailoring Core Skills for {company}...")
        prompt_skills = f"""
        Role: Strict Technical Recruiter.
        Job Title: {job_title}
        Job Description: {job_desc[:1000]}
        
        Candidate's Master Skills JSON:
        {json.dumps(master.get('skills', {}))}
        
        TASK: Filter the Candidate's Master Skills JSON. Keep ONLY the skills highly relevant to this specific job.
        
        CRITICAL RULES:
        1. RUTHLESS PRUNING: Drop completely irrelevant skills (e.g., remove "SEM/EDS" and "HiPIMS" if it's a pure software role; remove "React" if it's a pure hardware role).
        2. NO HALLUCINATION: DO NOT invent new skills. Only use the exact strings present in the Master JSON.
        3. MAXIMUM 15 SKILLS: Keep the list punchy, dense, and hyper-targeted.
        
        Output ONLY valid JSON matching the original category structure.
        """
        
        dynamic_skills = master.get('skills', {}) # Fallback
        with self.lock:
            try:
                res_skills = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_skills}], format='json')
                parsed_skills = json.loads(res_skills['message']['content'])
                if "skills" in parsed_skills and isinstance(parsed_skills["skills"], dict):
                    dynamic_skills = parsed_skills["skills"]
                elif parsed_skills:
                    dynamic_skills = parsed_skills
            except Exception as e:
                print(f"[BRAIN] Dynamic Skills Extraction Failed: {e}")
        # --- DYNAMIC SKILLS EXTRACTION END ---

        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company)
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', job_title)
        
        # --- FIX: NAMING CONVENTION UPDATE ---
        filename = f"{clean_company}_{clean_title}_Lucas_Mougeot"
        
        # --- MARKDOWN ASSEMBLY ---
        md_content = f"""---
target_title: "{strategy['target_title']}"
core_competency: "{strategy['core_competency']}"
---

## Professional Summary
{strategy['summary']}

## Relevant Experience
"""
        
        # --- EXPERIENCE SORTING ---
        experiences = master.get('experience', [])
        try:
            experiences.sort(key=lambda x: 0 if "Founding Systems Engineer" in x.get('title', '') else 1)
        except Exception:
            pass 

        for exp in experiences:
            role_bullets = [b for b in exp.get('standardized_bullets', []) if b['id'] in valid_approved_ids]
            role_bullets = role_bullets[:12] 
            
            if role_bullets:
                md_content += f"### {exp['title']} at {exp['company']} ({exp.get('dates', '')})\n"
                for b in role_bullets:
                    md_content += f"- {b['text']}\n"
                md_content += "\n"
        
        # Assemble the Tailored Skills Markdown
        md_content += "## Core Skills\n"
        for category, items in dynamic_skills.items():
            if items and isinstance(items, list): 
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
        sample_universe = random.sample(INITIAL_SEARCH_TERMS, 20)
        
        prompt = f"""
        Target Identified: "{job['title']}".
        
        TASK: Select exactly 2 job titles from the Approved Master List that are most similar or adjacent to the Target.
        
        Approved Master List: {sample_universe}
        
        Output JSON: {{"terms": ["term1", "term2"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                terms = json.loads(res['message']['content']).get('terms', [])
                valid_terms = [t for t in terms if t in INITIAL_SEARCH_TERMS]
                return valid_terms if valid_terms else random.sample(INITIAL_SEARCH_TERMS, 2)
            except: 
                return []