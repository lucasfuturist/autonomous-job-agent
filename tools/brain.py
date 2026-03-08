# tools/brain.py
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
        GOOD OUTPUT:["Robotics Engineer Seattle", "Robotics Engineer Austin", "Mid-Level Systems Engineer Seattle"]
        
        Output JSON: {{"queries":["term1", "term2", "term3"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                data = json.loads(res['message']['content'])
                return data.get('queries',[])
            except Exception as e:
                print(f"[BRAIN] Command Parse Failed: {e}")
                return[user_input]

    def generate_initial_strategy(self):
        print("[BRAIN] Loading Curated Master Target List...")
        terms = INITIAL_SEARCH_TERMS.copy()
        random.shuffle(terms)
        return terms
    
    def extract_metadata(self, description, title, company):
        prompt_extract = f"""
        Role: Precise Data Extraction Engine.
        Task: Analyze the job description and extract technical metadata.
        
        SOURCE TEXT:
        Title: {title}
        Company: {company}
        Description: {description[:3000]}
        
        RULES:
        1. EXTRACT ONLY what is explicitly stated in the text.
        2. DO NOT include "reasoning" or "comments" as JSON keys. Output RAW JSON only.
        3. If a field is missing, return null (for ints) or[] (for lists).
        
        SCHEMA:
        - score: int (Rate technical relevance to Python/C++/AI/Robotics from 0 to 10. 0=Retail/Medical, 5=Generic IT/Software, 10=AI/Robotics)
        - reason: "str" (One sentence objective summary of the role)
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
        """
        
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_extract}], format='json')
                raw_extract = json.loads(res['message']['content'])
                return self._normalize_keys(raw_extract)
            except Exception as e:
                print(f"[BRAIN] Extraction Fault ({HEAVY_MODEL}): {repr(e)}")
                return {
                    "score": 0, 
                    "reason": f"Extraction Fault: {repr(e)}"
                }

    def evaluate(self, job):
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

        return self.extract_metadata(job['description'], job['title'], job['company'])

    def build_jit_resume(self, job):
        master = self._load_master_data()
        if not master:
            return "Default", None

        job_desc = str(job.get('description', ''))[:2000]
        job_title = str(job.get('title', ''))
        company = str(job.get('company', ''))
        
        bullet_catalog = {}
        
        # --- 1. BUILD UNIFIED CATALOG (Experience + Projects) ---
        prompt_bullets = f"""
        Job Title: {job_title}
        Company: {company}
        Description:
        {job_desc}
        
        TASK: Select the absolute best bullet IDs to build a STRICT 1-PAGE 'Staff-Level Hybrid Portfolio' resume.
        
        CRITICAL EXECUTION STEPS & GUARDRAILS:
        1. DOMAIN CLASSIFICATION: Identify the target environment. Is it Cloud/SaaS? Silicon/Hardware? Physical Robotics? Edge Compute? Multi-Agent AI?
        2. PERFECT PAGE YIELD: You MUST select EXACTLY 7-9 bullets from 'Experience' and EXACTLY 3-5 bullets from 'Projects'. Do not exceed this limit.
        3. PROJECT DIVERSITY: Your Project bullets MUST span at least 2 distinct projects that directly answer the JD's requirements.
        
        CANDIDATE ASSETS:
        """
        
        fallback_ids =[]
        
        # Ingest Experience
        prompt_bullets += "\n--- EXPERIENCE ---\n"
        for exp in master.get('experience',[]):
            for i, b in enumerate(exp.get('standardized_bullets',[])):
                bullet_catalog[b['id']] = b['text']
                prompt_bullets += f"- {b['id']} ({exp['company']}): {b['text']}\n"
                if i < 3: fallback_ids.append(b['id']) # Fallback to core job history

        # Ingest Projects
        prompt_bullets += "\n--- PROJECTS ---\n"
        for proj in master.get('projects',[]):
            for i, b in enumerate(proj.get('standardized_bullets',[])):
                bullet_catalog[b['id']] = b['text']
                prompt_bullets += f"- {b['id']} (Project: {proj['name']}): {b['text']}\n"
                if i == 0 and len(fallback_ids) < 16:
                    fallback_ids.append(b['id'])

        prompt_bullets += """
        Output EXACTLY this JSON format (Do NOT output anything else): 
        {
            "strategy_rationale": "Briefly explain which projects and experiences you are prioritizing based on the JD.",
            "selected_ids":["exp_ez_1", "proj_lpe_2"]
        }
        """
        
        approved_ids =[]
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_bullets}], format='json')
                raw_content = res['message']['content']
                try:
                    data = json.loads(raw_content)
                    if "selected_ids" in data:
                        approved_ids = data["selected_ids"]
                        print(f"[BRAIN] Strategy Rationale: {data.get('strategy_rationale', 'None')}")
                    else:
                        approved_ids =[k for k, v in data.items() if isinstance(v, bool) and v is True]
                except json.JSONDecodeError:
                    print(f"[BRAIN] JSON parse failed, deploying Regex Extraction...")
                    approved_ids = list(set(re.findall(r'(?:exp|proj)_[a-zA-Z0-9]+_\d+', raw_content)))
            except Exception as e:
                print(f"[BRAIN] Bullet Extractor API Failed: {e}")
                
        valid_approved_ids = [i for i in approved_ids if i in bullet_catalog]
        
        # --- 2. ANTI-GAP GUARANTEE (Jobs Only) ---
        guaranteed_ids =[]
        for exp in master.get('experience',[]):
            job_bullet_ids = [b['id'] for b in exp.get('standardized_bullets',[])]
            kept_count = sum(1 for j_id in job_bullet_ids if j_id in valid_approved_ids)
            
            if kept_count < 1:
                needed = 1 - kept_count
                missing_ids =[j_id for j_id in job_bullet_ids if j_id not in valid_approved_ids]
                guaranteed_ids.extend(missing_ids[:needed])
                
        if guaranteed_ids:
            valid_approved_ids.extend(guaranteed_ids)
        
        # Dialed back up to 13 to hit the Goldilocks zone for 1-page aesthetics
        if len(valid_approved_ids) < 13:
            for fid in fallback_ids:
                if fid not in valid_approved_ids:
                    valid_approved_ids.append(fid)
                if len(valid_approved_ids) >= 13:
                    break

        # --- 3. SUMMARY GENERATION ---
        actual_experience_text = "\n".join([f"- {bullet_catalog[i]}" for i in valid_approved_ids if i in bullet_catalog][:12])
        
        prompt_strategy = f"""
        Role: Staff-Level Systems Architect & Ruthless Technical Resume Writer.
        Target Job: {job_title} at {company}
        Job Description Context: {job_desc[:800]}

        Candidate's ACTUAL Approved Experience for this role:
        {actual_experience_text}

        TASK: Construct the Strategic Header and Narrative.
        
        1. **target_title**: A specific, professional title adapted for this role.
        2. **core_competency**: A 3-5 word technical subtitle anchoring value.
        3. **summary**: A 2-sentence, high-impact technical thesis statement.

        ABSOLUTE ZERO-HALLUCINATION & TONE RULES:
        - PERSONA ALIGNMENT: Analyze the JD's vibe. Is it highly collaborative R&D? Strict compliance? Dev tools? Mold the candidate's summary to position them as the exact persona required to solve their specific challenges.
        - SYNTHESIS, NOT REPETITION: Do NOT just copy phrases. Synthesize the background into a high-level thesis.
        - STRICT LENGTH: Maximum of 2 sentences.
        - ZERO DOMAIN INFERENCE: You are FORBIDDEN from claiming experience in {company}'s specific domain.
        - NO TIMELINES: Do not calculate "years of experience".
        - BANNED WORDS: Never use "passionate", "innovative", "proven track record", "results-driven", "dynamic", "experienced", or "skilled".

        Output ONLY valid JSON: {{ "target_title": "...", "core_competency": "...", "summary": "..." }}
        """
        
        strategy = {
            "target_title": job_title,
            "core_competency": "Systems Engineering & AI Infrastructure",
            "summary": "Architects high-throughput, deterministic AI systems with a focus on real-time regulatory compliance and edge AI integration. Designs and deploys robust, versioned data pipelines ensuring integrity and auditability across legal and technical domains."
        }
        
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_strategy}], format='json')
                raw_content = res['message']['content']
                data = json.loads(raw_content)
                strategy.update(data)
            except Exception as e:
                print(f"[BRAIN] Strategy Synthesis Failed: {e}")

        # --- 4. SKILL PRUNING ---
        prompt_skills = f"""
        Role: Strict Technical Recruiter.
        Job Title: {job_title}
        Job Description: {job_desc[:1000]}
        
        Candidate's Master Skills JSON:
        {json.dumps(master.get('skills', {}))}
        
        TASK: Filter the Candidate's Master Skills JSON. Keep ONLY the skills highly relevant to this specific job.
        
        CRITICAL RULES:
        1. RUTHLESS PRUNING: Drop completely irrelevant skills.
        2. NO HALLUCINATION: DO NOT invent new skills. Only use the exact strings present in the Master JSON.
        3. MAXIMUM 12 SKILLS TOTAL: Keep the list punchy.
        
        Output ONLY valid JSON matching the original category structure.
        """
        
        dynamic_skills = master.get('skills', {})
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

        # --- 5. HEAVY KEYWORD EXTRACTION (CHAIN OF THOUGHT INTERSECTION) ---
        candidate_text_blob = strategy.get('summary', '') + "\n"
        candidate_text_blob += actual_experience_text + "\n"
        for proj in master.get('projects',[]):
            for b in proj.get('standardized_bullets',[]):
                if b['id'] in valid_approved_ids:
                    candidate_text_blob += b['text'] + "\n"
        for cat, items in dynamic_skills.items():
            if isinstance(items, list):
                candidate_text_blob += ", ".join(items) + "\n"

        prompt_highlights = f"""
        Role: Expert Technical Recruiter
        Target Job: {job_title} at {company}
        Job Description: {job_desc[:1200]}
        
        Candidate's Drafted Resume Text:
        {candidate_text_blob}
        
        TASK: Identify 6-8 technical "must-have" keywords from the Job Description that ALSO appear in the Candidate's Resume Text.
        
        CRITICAL RULE: You MUST output a mapping to prove the intersection. The 'candidate_match' string must be EXACTLY how it is spelled in the Candidate's Drafted Resume Text.
        Do not extract generic words like "development" or "software". Focus on hard skills, tools, and architecture (e.g., Python, Docker, LangGraph, C++, PyTorch, Multi-agent).
        
        Output EXACTLY this JSON format:
        {{
            "keyword_mapping":[
                {{"jd_term": "multi-agent architectures", "candidate_match": "multi-agent systems"}},
                {{"jd_term": "Docker/Kubernetes", "candidate_match": "Docker"}},
                {{"jd_term": "knowledge graph", "candidate_match": "knowledge graphs"}}
            ]
        }}
        """
        
        highlights =[]
        try:
            h_res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt_highlights}], format='json')
            h_data = json.loads(h_res['message']['content'])
            if "keyword_mapping" in h_data:
                highlights =[item.get("candidate_match") for item in h_data["keyword_mapping"] if "candidate_match" in item]
            else:
                highlights = h_data if isinstance(h_data, list) else []
            print(f"[BRAIN] Extracted Intersecting JD Keywords for Bolding: {highlights}")
        except Exception as e:
            print(f"[BRAIN] Keyword extraction failed: {e}")

        def bold_highlights(text, terms):
            if not terms: return text
            
            terms = sorted([t for t in terms if isinstance(t, str) and len(t) >= 2], key=len, reverse=True)
            
            for term in terms:
                if len(term) <= 3 and term.lower() not in["c", "c++", "ai", "ml", "qa", "ui", "ux", "cv", "go", "aws", "gcp", "api", "rag", "llm"]: 
                    continue 
                
                term_lower = term.lower()
                if not term[-1].isalpha() or len(term) <= 3:
                    regex_core = re.escape(term)
                elif term_lower.endswith('s') and not term_lower.endswith('ss'):
                    regex_core = re.escape(term[:-1]) + r's?'
                else:
                    regex_core = re.escape(term) + r's?'

                pattern = re.compile(rf'(?<![a-zA-Z0-9_\*]){regex_core}(?![a-zA-Z0-9_\*])', re.IGNORECASE)
                text = pattern.sub(lambda m: f"**{m.group(0)}**", text)
            
            text = re.sub(r'\*{3,}', '**', text)
            return text

        # --- 6. MARKDOWN ASSEMBLY ---
        highlighted_summary = bold_highlights(strategy['summary'], highlights)

        md_content = f"""---
target_title: "{strategy['target_title']}"
core_competency: "{strategy['core_competency']}"
---

## Professional Summary
{highlighted_summary}

## Relevant Experience
"""
        
        # Experience Loop
        experiences = master.get('experience',[])
        for exp in experiences:
            role_bullets =[b for b in exp.get('standardized_bullets', []) if b['id'] in valid_approved_ids]
            if role_bullets:
                md_content += f"### {exp['title']} at {exp['company']} ({exp.get('dates', '')})\n\n"
                for b in role_bullets:
                    highlighted_bullet = bold_highlights(b['text'], highlights)
                    md_content += f"- {highlighted_bullet}\n"
                md_content += "\n"
        
        # Project Loop
        project_section = ""
        projects = master.get('projects',[])
        for proj in projects:
            selected_proj_bullets =[b for b in proj.get('standardized_bullets', []) if b['id'] in valid_approved_ids]
            if selected_proj_bullets:
                project_section += f"### {proj['name']}\n\n"
                if 'context' in proj:
                    project_section += f"*{proj['context']}*\n\n"
                for b in selected_proj_bullets:
                    highlighted_proj_bullet = bold_highlights(b['text'], highlights)
                    project_section += f"- {highlighted_proj_bullet}\n"
                project_section += "\n"
        
        if project_section:
            md_content += "## Selected Engineering Architectures\n\n" + project_section

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

        md_content += "## Core Skills\n\n"
        for category, items in dynamic_skills.items():
            if items and isinstance(items, list): 
                display_label = CATEGORY_LABELS.get(category, category.replace('_', ' ').title())
                bolded_items =[bold_highlights(item, highlights) for item in items]
                md_content += f"- **{display_label}:** {', '.join(bolded_items)}\n"
            
        md_content += "\n## Education\n\n"
        for ed in master.get('education',[]):
            md_content += f"- **{ed['degree']}** | {ed['institution']}<br>*{ed['details']}*\n"
            
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
        
        Output JSON: {{"terms":["term1", "term2"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                terms = json.loads(res['message']['content']).get('terms',[])
                valid_terms =[t for t in terms if t in INITIAL_SEARCH_TERMS]
                return valid_terms if valid_terms else random.sample(INITIAL_SEARCH_TERMS, 2)
            except: 
                return[]

    def generate_outreach(self, job):
        company = str(job.get('company', 'your company'))
        title = str(job.get('title', 'the open role'))
        tech = "systems engineering"
        try:
            parsed_tech = json.loads(job.get('tech_stack_core', '[]'))
            if parsed_tech: 
                tech = ", ".join(parsed_tech[:2])
        except: 
            pass
        
        prompt = f"""
        Role: Professional Engineer doing direct outreach to a Technical Recruiter / Talent Acquisition.
        Task: Write a concise, natural LinkedIn connection message (Under 250 characters MAXIMUM).
        
        Target Company: {company}
        Target Role: {title}
        Key Technologies Required: {tech}
        Candidate Profile: Systems Engineer. Built production multi-agent LLM orchestrators (LangGraph), temporal PostgreSQL Knowledge Graphs, and deterministic AST-parsing pipelines.
        
        RULES:
        1. PHYSICAL LIMIT: MUST be under 250 characters total.
        2. FORMAT: Start exactly with "Hi [Name],\n\n" and end exactly with "\n\nI'd love to connect and discuss this role!\n\nBest,\nLucas".
        3. THE RECRUITER PIVOT: The recipient is in Talent Acquisition, NOT a Staff Engineer. Do NOT use overly dense jargon like "temporal PostgreSQL" or "AST parsing". Instead, translate your Candidate Profile into accessible, high-level alignment matching the Target Role (e.g., "deploying LLM applications", "building AI infrastructure", or "developing ML pipelines").
        4. THE NARRATIVE: "I just applied for[Role]. With my background in[Accessible High-Level Skill], I believe I'd be a strong fit for the team."
        5. TONE: Warm, natural, confident, and recruiter-friendly.
        
        Output valid JSON only: {{ "message": "..." }}
        """
        with self.lock:
            try:
                res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                data = json.loads(res['message']['content'])
                return data.get('message', "Hi[Name],\n\nI recently applied for your open role and believe my systems engineering background strongly aligns with your team's needs.\n\nBest,\nLucas")
            except Exception as e:
                return "Hi [Name],\n\nI recently applied for your open role and believe my systems engineering background strongly aligns with your team's needs.\n\nBest,\nLucas"