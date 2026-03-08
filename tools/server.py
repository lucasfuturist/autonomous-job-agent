# tools/server.py
import http.server
import socketserver
import sys
import json
import os
import traceback
import threading
import glob
import shutil
import re
import urllib.parse
import time

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# --- CONFIG & EXTERNAL IMPORTS ---
try:
    import ollama 
    from config import PORT, MD_FOLDER, HEAVY_MODEL
except ImportError as e:
    print(f"\n[SERVER] 🛑 CRITICAL IMPORT ERROR: {e}")
    print("Ensure you are running from the project root and have dependencies installed.\n")
    sys.exit(1)

# --- PDF GENERATION SUPPORT ---
try:
    import markdown2
    from xhtml2pdf import pisa
    PDF_ENABLED = True
except ImportError:
    print("[SERVER] ⚠️  PDF libs missing. Run: 'pip install markdown2 xhtml2pdf'")
    PDF_ENABLED = False

# --- CORE SUBSYSTEMS ---
mem = None
brain = None

def init_subsystems():
    global mem, brain
    print("[SERVER] Initializing Memory & Brain subsystems...")
    try:
        from tools.memory import Memory
        from tools.brain import Brain
        
        mem = Memory()
        mem.get_agenda_status() 
        brain = Brain()
        print("[SERVER] ✅ Subsystems active.")
    except Exception as e:
        print(f"\n[SERVER] 🛑 FATAL SUBSYSTEM ERROR: {e}")
        traceback.print_exc()
        print("[SERVER] Server cannot start without Memory/Brain. Exiting.")
        os._exit(1)

FEEDBACK_FILE = "data/tactical_feedback.txt"
DEPLOY_FOLDER = "data/deployments"

# Ultra-Compressed CSS for strict 1-page limits
RESUME_CSS = """
<style>
    @page { 
        size: letter; 
        margin: 0.2in 0.3in; /* Tighter vertical bounds to capture orphans */
    }
    body { 
        font-family: 'Calibri', 'Carlito', 'Helvetica', 'Arial', sans-serif; 
        font-size: 8.5pt; /* Reduced by 0.5pt to ensure 1-page fit */
        line-height: 1.1; 
        color: #000; 
    }
    .header-block { text-align: center; margin-bottom: 4px; }
    
    .name-text { 
        font-family: 'Calibri', 'Carlito', 'Helvetica', 'Arial', sans-serif; 
        font-size: 13pt; 
        font-weight: bold; 
        text-transform: uppercase; 
        margin-bottom: 2px; 
        color: #000;
        letter-spacing: 1px;
    }
    
    .target-title-box { 
        font-size: 9pt; 
        font-weight: bold; 
        margin-bottom: 2px; 
        width: 100%; 
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .contact-text { 
        font-size: 8.5pt; 
        font-weight: normal; 
        margin-top: 0px; 
        padding-bottom: 4px;
        border-bottom: 1pt solid #000; 
        margin-bottom: 4px;
    }
    
    a { text-decoration: none; color: #000; }
    
    /* Section Headers */
    h2 { 
        font-size: 9.5pt; 
        font-weight: bold; 
        text-transform: uppercase; 
        margin-top: 3px; 
        margin-bottom: 2px; 
        border-bottom: 1pt solid #000; 
        padding-bottom: 1px; 
    }
    
    /* Fixed: Table-based alignment locked to margins */
    .entry-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 4px; 
        margin-bottom: 0px; 
        table-layout: fixed; 
    }
    .left-cell { 
        text-align: left; 
        font-weight: bold; 
        font-size: 9pt; 
        vertical-align: bottom; 
        width: 80%; 
        padding-right: 5px; 
    }
    .right-cell { 
        text-align: right; 
        font-weight: normal; 
        font-size: 8.5pt; 
        vertical-align: bottom; 
        width: 20%; 
        white-space: nowrap; 
    }
    
    /* Project Names */
    .project-header { 
        font-weight: bold; 
        font-size: 9pt; 
        margin-top: 4px; 
        margin-bottom: 0px; 
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    p { margin-top: 0; margin-bottom: 2px; text-align: left; }
    
    /* Bullet points */
    ul { 
        margin-top: 1px; 
        margin-bottom: 0px; 
        padding-left: 12px; 
    }
    li { 
        margin-bottom: 0px; 
        text-align: left; 
    } 
    
    strong { font-weight: bold; }
    .keep-together { page-break-inside: avoid; }
</style>
"""
CONTACT_INFO = """Boston, MA | (904) 304-2890 | <a href="mailto:lucas@lucasmougeot.ai">lucas@lucasmougeot.ai</a> | <a href="https://www.lucasmougeot.ai">lucasmougeot.ai</a>"""
DEFAULT_COMPETENCY = "AI Platform & Deterministic LLM Infrastructure"

def convert_to_pdf(md_path, output_path, target_role_arg=None):
    if not PDF_ENABLED: return False
    try:
        with open(md_path, 'r', encoding='utf-8') as f: md_text = f.read()
        fm_title, fm_competency = None, None
        if md_text.startswith('---'):
            try:
                parts = md_text.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    md_text = parts[2]
                    title_match = re.search(r'target_title:\s*"(.*?)"', frontmatter)
                    if title_match: fm_title = title_match.group(1)
                    comp_match = re.search(r'core_competency:\s*"(.*?)"', frontmatter)
                    if comp_match: fm_competency = comp_match.group(1)
            except Exception as e:
                print(f"[SERVER] Frontmatter Parse Error: {e}")

        final_title = fm_title if fm_title else (target_role_arg if target_role_arg else "Software Engineer")
        final_competency = fm_competency if fm_competency else DEFAULT_COMPETENCY
        header_title = f"{final_title} | {final_competency}"

        name = "LUCAS MOUGEOT" 
        lines = md_text.split('\n')
        if lines[0].strip().startswith('# '): md_text = '\n'.join(lines[1:]) 
        html_body = markdown2.markdown(md_text)
        
        def header_replacer(match):
            full_text = match.group(1)
            date_match = re.search(r'\(([^)]+)\)$', full_text)
            if date_match:
                date_str = date_match.group(1)
                title_str = full_text[:date_match.start()].strip()
                return (
                    f'<div class="keep-together">'
                    f'  <table class="entry-table">'
                    f'    <tr>'
                    f'      <td class="left-cell">{title_str}</td>'
                    f'      <td class="right-cell">{date_str}</td>'
                    f'    </tr>'
                    f'  </table>'
                    f'</div>'
                )
            else: 
                return f'<div class="project-header">{full_text}</div>'
            
        html_body = re.sub(r'<h3>(.*?)</h3>', header_replacer, html_body)

        full_html = f"""<html><head><meta charset="utf-8">{RESUME_CSS}</head><body><div class="header-block"><div class="name-text">{name}</div><div class="target-title-box">{header_title}</div><div class="contact-text">{CONTACT_INFO}</div></div>{html_body}</body></html>"""
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, "w", encoding='utf-8') as f: f.write(full_html)
        with open(output_path, "wb") as pdf_file: pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)
        if pisa_status.err: return False
        return True
    except Exception as e: return False

def perform_summary_regen(filename):
    filepath = os.path.join(MD_FOLDER, filename)
    if not os.path.exists(filepath): return None
    with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
    fm_match = re.search(r'---\ntarget_title: "(.*?)"\ncore_competency: "(.*?)"\n---', content, re.DOTALL)
    if not fm_match: return None
    target_title = fm_match.group(1)
    company = filename.split('_')[0]
    summary_match = re.search(r'## Professional Summary\n(.*?)\n\n## Relevant Experience', content, re.DOTALL)
    if not summary_match: return None
    current_summary = summary_match.group(1).strip()
    
    prompt = f"""
    Role: Ruthless, Strictly Factual Technical Resume Writer.
    Target Job Title: {target_title}
    Target Company: {company}
    Current Summary: 
    "{current_summary}"
    TASK: Rewrite the summary above to improve flow and impact.
    RULES:
    1. NARRATIVE PROSE: Write in flowing, professional resume prose using implied first-person. 
    2. GOOD: "Systems Engineer with a proven track record of architecting real-time systems..."
    3. FACT-BASED ALIGNMENT: Keep the facts the same. Just fix the sentence structure.
    4. NO HALLUCINATION: Do not invent new facts.
    Output ONLY valid JSON: {{ "summary": "..." }}
    """
    try:
        res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
        data = json.loads(res['message']['content'])
        new_summary = data.get('summary', current_summary)
        new_content = content.replace(current_summary, new_summary)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(new_content)
        pdf_path = filepath.replace('.md', '.pdf').replace('output_mds', 'deployments')
        convert_to_pdf(filepath, pdf_path)
        return new_content
    except Exception as e: return None

class CRMHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if "OPTIONS" not in args[0]:
            sys.stderr.write("%s - - [%s] %s\n" %
                             (self.address_string(),
                              self.log_date_time_string(),
                              format%args))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        try:
            if self.path.startswith('/api/health'):
                self._send_json({"status": "ok", "time": time.time()})
            elif self.path.startswith('/api/jobs'): 
                self._handle_get_jobs()
            elif self.path.startswith('/api/stats'): 
                self._handle_get_stats()
            elif self.path.startswith('/api/rules'): 
                self._handle_get_rules()
            elif self.path.startswith('/api/agenda'): 
                self._handle_get_agenda()
            elif self.path.startswith('/api/logs/all'): 
                self._handle_get_all_logs()
            elif self.path.startswith('/api/logs'): 
                self._handle_get_logs()
            elif self.path.startswith('/api/resume'): 
                self._handle_get_resume()
            elif self.path.startswith('/api/recruiters'):
                self._handle_get_recruiters()
            elif self.path.startswith('/api/agent_state'): 
                status = {
                    "active": mem.get_agent_state() if mem else False,
                    "activity": mem.get_system_activity() if mem else {"source": "SYSTEM", "message": "Memory Offline"}
                }
                self._send_json(status)
            else: 
                super().do_GET()
        except Exception as e:
            print(f"[SERVER] Error in GET {self.path}: {e}")
            traceback.print_exc()
            self.send_error(500, str(e))

    def _handle_get_jobs(self):
        status_filter = None
        if "?" in self.path:
            query = self.path.split("?")[1]
            if "status=" in query: status_filter = query.split("status=")[1].split("&")[0]
        jobs = mem.get_jobs(status_filter)
        self._send_json(jobs)

    def _handle_get_stats(self): 
        self._send_json(mem.get_global_stats())

    def _handle_get_rules(self):
        if not os.path.exists(FEEDBACK_FILE):
            self._send_json({"rules": ""})
            return
        with open(FEEDBACK_FILE, "r") as f: self._send_json({"rules": f.read()})

    def _handle_get_agenda(self):
        conn = mem._get_conn()
        conn.row_factory = lambda cursor, row: row[0]
        terms = conn.execute("SELECT term FROM agenda WHERE status='PENDING' ORDER BY added_at ASC").fetchall()
        conn.close()
        self._send_json({"agenda": terms, "count": len(terms)})

    def _handle_get_logs(self): 
        self._send_json(mem.get_mission_logs(limit=50))
        
    def _handle_get_all_logs(self): 
        self._send_json(mem.get_all_mission_logs())

    def _handle_get_resume(self):
        if "?" not in self.path or "name=" not in self.path:
            self.send_error(400, "Missing name parameter")
            return
        query = self.path.split("?")[1]
        name_param =[p.split("=")[1] for p in query.split("&") if p.startswith("name=")][0]
        if not name_param:
             self.send_error(400, "Empty name parameter")
             return
        clean_name = os.path.basename(name_param) 
        target_path = os.path.join(MD_FOLDER, f"{clean_name}.md")
        content = ""
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f: content = f.read()
        else:
            matches = glob.glob(os.path.join(MD_FOLDER, "**", f"{clean_name}.md"), recursive=True)
            if matches:
                with open(matches[0], "r", encoding="utf-8") as f: content = f.read()
            else: content = "# Resume Not Found on Disk"
        self._send_json({"content": content})

    def _handle_get_recruiters(self):
        if "?" not in self.path:
            self.send_error(400, "Missing query parameters")
            return
            
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        company = query_components.get('company', [''])[0]
        
        if not company:
            self.send_error(400, "Missing company parameter")
            return

        cached = mem.get_recruiters_for_company(company)
        self._send_json({"recruiters": cached if cached else[]})

    def _handle_save_resume(self, data):
        name = data.get('name')
        content = data.get('content')
        if not name or content is None:
            self.send_error(400, "Missing name or content")
            return
        clean_name = os.path.basename(name)
        if not clean_name.endswith('.md'): clean_name += '.md'
        try:
            with open(os.path.join(MD_FOLDER, clean_name), "w", encoding="utf-8") as f: f.write(content)
            self._send_json({"success": True})
        except Exception as e: self.send_error(500, f"Save failed: {e}")

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            if self.path == '/api/agent_state':
                data = json.loads(post_data)
                mem.set_agent_state(data.get('active', False))
                self._send_json({"success": True})

            elif self.path == '/api/update_status':
                data = json.loads(post_data)
                mem.update_status(data.get('id'), data.get('status'))
                self._send_json({"success": True})

            elif self.path == '/api/star':
                data = json.loads(post_data)
                mem.toggle_star(data.get('id'), data.get('starred'))
                self._send_json({"success": True})

            elif self.path == '/api/rules':
                data = json.loads(post_data)
                with open(FEEDBACK_FILE, "w") as f: f.write(data.get('rules', ''))
                self._send_json({"success": True})
            
            elif self.path == '/api/rescore':
                try:
                    import reweigh_queue
                    threading.Thread(target=reweigh_queue.run_assimilation, daemon=True).start()
                    self._send_json({"success": True})
                except ImportError:
                     print("[SERVER] 'reweigh_queue.py' not found. Skipping assimilation.")
                     self._send_json({"success": False, "error": "Module missing"})
            
            elif self.path == '/api/agenda':
                data = json.loads(post_data)
                if 'command' in data:
                    terms = brain.parse_command(data.get('command'))
                    mem.add_to_agenda(terms, source='USER')
                    mem.flag_purge_queue()
                    self._send_json({"success": True, "terms": terms})
                elif 'term' in data:
                    mem.add_to_agenda(data.get('term'), source='USER')
                    self._send_json({"success": True})
                else: 
                    self.send_error(400)
                    
            elif self.path == '/api/deploy':
                data = json.loads(post_data)
                resume_name = data.get('resume')
                if resume_name:
                    clean_name = os.path.basename(resume_name)
                    if not clean_name.endswith('.md'): clean_name += '.md'
                    src_path = os.path.join(MD_FOLDER, clean_name)
                    dest_md = os.path.join(DEPLOY_FOLDER, clean_name)
                    dest_pdf = os.path.join(DEPLOY_FOLDER, clean_name.replace('.md', '.pdf'))
                    if os.path.exists(src_path):
                        shutil.copy2(src_path, dest_md)
                        pdf_success = convert_to_pdf(src_path, dest_pdf, data.get('target_role', None))
                        self._send_json({
                            "success": True, 
                            "path": dest_pdf if pdf_success else dest_md,
                            "url": f"/{DEPLOY_FOLDER}/{clean_name.replace('.md', '.pdf')}" if pdf_success else f"/{DEPLOY_FOLDER}/{clean_name.replace('.md', '.html')}",
                            "format": "PDF" if pdf_success else "HTML"
                        })
                    else: 
                        self._send_json({"success": False, "error": "Source resume not found"})
                else: 
                    self.send_error(400, "Missing resume parameter")
            
            elif self.path == '/api/save_resume': 
                self._handle_save_resume(json.loads(post_data))
                
            elif self.path == '/api/regenerate_summary':
                data = json.loads(post_data)
                if data.get('name'):
                    new_content = perform_summary_regen(data.get('name'))
                    if new_content: 
                        self._send_json({"success": True, "content": new_content})
                    else: 
                        self.send_error(500, "Regeneration failed")
                else: 
                    self.send_error(400, "Missing name")

            elif self.path == '/api/regenerate_resume':
                data = json.loads(post_data)
                job_id = data.get('job_id')
                if job_id:
                    jobs = mem.get_jobs(status="ALL")
                    target_job = next((j for j in jobs if j['id'] == job_id), None)
                    if target_job:
                        try:
                            filename, _ = brain.build_jit_resume(target_job)
                            clean_name = os.path.basename(filename)
                            if not clean_name.endswith('.md'): clean_name += '.md'
                            filepath = os.path.join(MD_FOLDER, clean_name)
                            if os.path.exists(filepath):
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                self._send_json({"success": True, "content": content, "filename": clean_name})
                            else:
                                self.send_error(500, "Generated file not found on disk.")
                        except Exception as e:
                            print(f"[SERVER] Regeneration error: {e}")
                            self.send_error(500, f"Regeneration failed: {e}")
                    else:
                        self.send_error(404, "Job not found")
                else:
                    self.send_error(400, "Missing job_id")
            
            elif self.path == '/api/intel/update':
                data = json.loads(post_data)
                job_id = data.get('id')
                desc = data.get('description')
                
                if job_id and desc:
                    try:
                        mem.update_job_description(job_id, desc)
                        job = mem.get_job_by_id(job_id)
                        
                        if job:
                            analysis = brain.extract_metadata(desc, job['title'], job['company'])
                            
                            new_score = int(analysis.get('score', 0))
                            reason = analysis.get('reason', 'Updated via manual edit')
                            
                            mem.update_job(job['url'], new_score, reason, job['selected_resume'], analysis)
                            
                            updated_job = mem.get_job_by_id(job_id)
                            self._send_json({"success": True, "job": dict(updated_job)})
                        else:
                             self.send_error(404, "Job not found after update")
                    except Exception as e:
                        print(f"[SERVER] Intel update failed: {e}")
                        traceback.print_exc()
                        self.send_error(500, f"Update failed: {e}")
                else:
                    self.send_error(400, "Missing id or description")

            elif self.path == '/api/recruiters/status':
                data = json.loads(post_data)
                mem.toggle_recruiter_outreach(data.get('job_id'), data.get('url'), data.get('contacted'))
                self._send_json({"success": True})
            elif self.path == '/api/recruiters/add':
                data = json.loads(post_data)
                mem.add_manual_recruiter(data.get('job_id'), data.get('url'))
                self._send_json({"success": True})
            elif self.path == '/api/outreach/generate':
                data = json.loads(post_data)
                job_id = data.get('job_id')
                jobs = mem.get_jobs(status="ALL")
                target_job = next((j for j in jobs if j['id'] == job_id), None)
                if target_job:
                    msg = brain.generate_outreach(target_job)
                    mem.update_outreach_message(job_id, msg)
                    self._send_json({"success": True, "message": msg})
                else:
                    self.send_error(404, "Job not found")
            else: 
                self.send_error(404)
        except Exception as e: 
            print(f"[SERVER] Error in POST {self.path}: {e}")
            traceback.print_exc()
            self.send_error(500)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    def handle_error(self, request, client_address): pass

def start_server():
    if os.path.basename(os.getcwd()) == "tools": os.chdir("..")
    
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists(DEPLOY_FOLDER): os.makedirs(DEPLOY_FOLDER)
    if not os.path.exists(FEEDBACK_FILE): 
        with open(FEEDBACK_FILE, "w") as f: f.write("")

    init_subsystems()

    try:
        with ThreadedHTTPServer(("0.0.0.0", PORT), CRMHandler) as httpd:
            print(f"[SERVER] 🚀 API Online (Threaded): http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[SERVER] ❌ FAILED TO BIND to Port {PORT}: {e}")