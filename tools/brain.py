import ollama
import json
import os
import glob
import re
import threading
from config import OLLAMA_MODEL, MD_FOLDER, CORE_SCHEMA

class Brain:
    def __init__(self):
        print("[BRAIN] Loading Full Resume Database into Memory...")
        self.full_resumes = self._load_full_resumes()
        self.lock = threading.Lock()

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

    def generate_initial_strategy(self):
        print("[BRAIN] Analyzing Resume Catalog to generate schema-locked hunt strategy...")
        if not self.full_resumes: return []

        resume_names = "\n".join(list(self.full_resumes.keys()))
        prompt = f"""
        You are an elite career strategist. 
        Below is a list of highly specialized resumes.
        {resume_names}
        
        TASK: Generate 5 Job Search Queries.
        
        CRITICAL CONSTRAINTS:
        1. DO NOT include the candidate's name (Lucas Mougeot).
        2. You MUST ONLY use concepts from this STRICT SCHEMA: {CORE_SCHEMA}
        
        Output ONLY valid JSON: {{"terms": ["term1", "term2", "term3", "term4", "term5"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                data = json.loads(res['message']['content'])
                terms = data.get('terms', [])
                clean_terms = [t.replace("Lucas Mougeot", "").strip() for t in terms]
                print(f"[BRAIN] Initial Strategy defined: {clean_terms}")
                return clean_terms
            except: return []
    
    def evaluate(self, job):
        prompt = """
        Role: Ruthless Career Strategist.
        Task: Score this job 1-10 for a highly specialized Hybrid Engineer (AI + Hardware + Startups).
        
        STRICT SCORING RUBRIC:
        - 9 to 10: Dream Role. Requires BOTH AI (LLMs, Agents, ML) AND Physical Systems/Robotics.
        - 7 to 8: Strong Target. Requires EITHER advanced AI/ML OR advanced Robotics/Hardware.
        - 1 to 6: Trash. Auto-reject if: Healthcare, Medical, Logistics/Warehouse, Sales, HR, Education, or standard Web Development. 
        
        Output JSON ONLY: {"score": int, "reason": "One short sentence ruthless justification"}
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
        if not self.full_resumes: return "Default", "# No resumes loaded in database."

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
        prompt = f"""
        We found a high-value target: "{job['title']}".
        
        TASK: Suggest 2 NEW search terms to find similar cutting-edge roles.
        
        CRITICAL RULE: You MUST ONLY generate terms that are direct combinations of the job title and this strict schema: {CORE_SCHEMA}.
        Do NOT invent terms outside of this schema. Keep them highly technical.
        
        Output JSON: {{"terms": ["term1", "term2"]}}
        """
        with self.lock:
            try:
                res = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
                return json.loads(res['message']['content']).get('terms', [])
            except: return []