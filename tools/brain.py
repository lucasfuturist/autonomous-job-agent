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

    def _normalize_keys(self, data):
        """Fixes malformed JSON keys from smaller LLMs (e.g. 'tech_ stack_ core' -> 'tech_stack_core')"""
        if not isinstance(data, dict):
            return data
        
        normalized = {}
        for k, v in data.items():
            clean_k = k.replace(" ", "")
            normalized[clean_k] = v
        return normalized

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
        print("[BRAIN] Loading Curated Master Target List...")
        terms = INITIAL_SEARCH_TERMS.copy()
        random.shuffle(terms)
        return terms
    
    def evaluate(self, job):
        # --- 0. FAST FAIL: HEURISTICS ---
        location = job.get('location', '')
        if location:
            mem_instance = self.MemoryClass()
            distance = mem_instance.get_or_fetch_distance(location)
            if distance is not None and distance != -1.0 and distance > MAX_COMMUTE_MILES:
                return {"score": 0, "reason": f"Geofence Reject: {distance} miles away."}

        title_lower = str(job.get('title', '')).lower()
        company_lower = str(job.get('company', '')).lower()
        
        for pattern in COMPANY_BLACKLIST:
            if re.search(pattern, company_lower):
                return {"score": 0, "reason": f"Heuristic Reject: Blacklisted Company '{pattern}'"}
        for pattern in TITLE_BLACKLIST:
            if re.search(pattern, title_lower):
                return {"score": 0, "reason": f"Heuristic Reject: Blacklisted Role '{pattern}'"}

        dynamic_rules = self._load_dynamic_rules()

        # --- PASS 1: SCORING (FIT CHECK) ---
        # Keep this lightweight (OLLAMA_MODEL) for speed
        score_data = {"score": 0, "reason": "Default"}
        prompt_score = f"""
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
        
        SCORING RUBRIC (0-10):
        - 0-2: Medical/Trades/Sales/IT Support.
        - 3-5: Generic Web Dev or Business Analyst.
        - 8-10: Hard Match (Robotics, AI Infra, C++/Python Systems).
        
        DYNAMIC RULES: {USER_PREFERENCES} {dynamic_rules}
        
        Output JSON: {{"score": int, "reason": "Short justification"}}
        """
        
        with self.lock:
            try:
                res1 = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt_score}], format='json')
                score_data = json.loads(res1['message']['content'])
            except Exception as e:
                return {"score": 0, "reason": f"Scoring Fault: {e}"}

        # If the job is junk, don't waste time (or heavy compute) extracting data
        if score_data.get('score', 0) < 2:
            return score_data

        # --- PASS 2: DATA EXTRACTION (HEAVY MODEL) ---
        # Use HEAVY_MODEL here for precision JSON extraction
        prompt_extract = f"""
        Role: Precise Data Extraction Engine.
        Task: Extract technical metadata from the text below.
        
        SOURCE TEXT:
        Title: {job['title']}
        Company: {job['company']}
        Description: {job['description'][:3000]}
        
        RULES:
        1. EXTRACT ONLY what is explicitly stated in the text.
        2. DO NOT infer skills not listed.
        3. DO NOT include "reasoning" or "comments" in the JSON. Output RAW JSON only.
        4. If a field is missing, return null (for ints) or [] (for lists).
        
        SCHEMA:
        - salary_base_min: int or null
        - salary_base_max: int or null
        - work_mode: "Remote", "Hybrid", "Onsite", "Unknown"
        - travel_pct_max: int or null
        - clearance_required: "None", "Secret", "TS/SCI", "Poly"
        - itar_ear_restricted: boolean
        - tech_stack_core: list[str] (Top 5 required technologies)
        - hardware_physical_tools: list[str] (Hardware/Machinery)
        - yoe_actual: int (Minimum years required)
        - red_flags: list[str] (Toxic traits, unpaid, etc.)

        Output JSON:
        {{
            "salary_base_min": 100000,
            "salary_base_max": 150000,
            "work_mode": "Hybrid",
            "travel_pct_max": 10,
            "clearance_required": "None",
            "itar_ear_restricted": false,
            "tech_stack_core": ["Python", "AWS"],
            "hardware_physical_tools": [],
            "yoe_actual": 5,
            "red_flags": []
        }}
        """
        
        extract_data = {}
        with self.lock:
            try:
                # SWITCHED TO HEAVY_MODEL FOR STABILITY
                res2 = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_extract}], format='json')
                raw_extract = json.loads(res2['message']['content'])
                extract_data = self._normalize_keys(raw_extract)
            except Exception as e:
                print(f"[BRAIN] Extraction Fault ({HEAVY_MODEL}): {e}")
                
        # Merge results
        final_result = {**score_data, **extract_data}
        return final_result

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
        
        # --- FIX: TOTAL TIMELINE GUARANTEE ---
        # Ensure EVERY job in the master JSON is represented by at least 2 bullets
        # to prevent the LLM from truncating years of overall experience.
        guaranteed_ids = []
        for exp in master.get('experience', []):
            job_bullet_ids = [b['id'] for b in exp.get('standardized_bullets', [])]
            
            # Count how many bullets for this specific job the LLM actually kept
            kept_count = sum(1 for j_id in job_bullet_ids if j_id in valid_approved_ids)
            
            if kept_count < 2:
                needed = 2 - kept_count
                missing_ids = [j_id for j_id in job_bullet_ids if j_id not in valid_approved_ids]
                guaranteed_ids.extend(missing_ids[:needed])
                
        # Merge the forced IDs into the approved list
        if guaranteed_ids:
            print(f"[BRAIN] Anti-Truncation Triggered: Forcing {len(guaranteed_ids)} missing bullets into {company}...")
            valid_approved_ids.extend(guaranteed_ids)
        
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
        - DO NOT SHAPE-SHIFT: Do not state the candidate is an "Expert in [Target Job Title]" if they have never held that title. Anchor the identity in their actual background.
        - FACT-BASED ALIGNMENT: State ONLY the hardware, software, and systems the candidate has factually built. Frame those TRUE skills as the reason they are highly capable of solving {company}'s engineering problems.
        - NARRATIVE PROSE: Write in flowing, professional resume prose using implied first-person. DO NOT start sentences with raw, floating verbs like "Architect and implement." Use connecting phrases like "Systems Engineer with a proven track record of architecting..." or "Leverages deep expertise in X to build Y."
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

        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company)
        clean_title = re.sub(r'[^a-zA-Z0-9]', '', job_title)
        
        filename = f"{clean_company}_{clean_title}_Lucas_Mougeot"
        
        md_content = f"""---
target_title: "{strategy['target_title']}"
core_competency: "{strategy['core_competency']}"
---

## Professional Summary
{strategy['summary']}

## Relevant Experience
"""
        
        experiences = master.get('experience', [])
        try:
            experiences.sort(key=lambda x: 0 if "Founding Systems Engineer" in x.get('title', '') else 1)
        except Exception:
            pass 

        for exp in experiences:
            role_bullets = [b for b in exp.get('standardized_bullets', []) if b['id'] in valid_approved_ids]
            # Ensure we respect the overall length limit, but we don't truncate completely
            role_bullets = role_bullets[:12] 
            
            if role_bullets:
                md_content += f"### {exp['title']} at {exp['company']} ({exp.get('dates', '')})\n"
                for b in role_bullets:
                    md_content += f"- {b['text']}\n"
                md_content += "\n"
        
        CATEGORY_LABELS = {
            "programming_languages": "Programming Languages",
            "ai_and_machine_learning": "AI and Machine Learning",
            "backend_data_and_infrastructure": "Backend Data and Infrastructure",
            "robotics_edge_and_autonomy": "Robotics Edge and Autonomy",
            "materials_characterization": "Materials Characterization",
            "hardware_and_thermal_processing": "Hardware and Thermal Processing",
            "electrochemistry_and_lab_techniques": "Electrochemistry and Lab Techniques",
            "engineering_methodologies": "Engineering Methodologies"
        }

        md_content += "## Core Skills\n"
        for category, items in dynamic_skills.items():
            if items and isinstance(items, list): 
                display_label = CATEGORY_LABELS.get(category, category.replace('_', ' ').title())
                md_content += f"- **{display_label}:** {', '.join(items)}\n"
            
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