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
from config import PORT, MD_FOLDER

# --- OPTIONAL PDF DEPENDENCIES ---
try:
    import markdown2
    from xhtml2pdf import pisa
    PDF_ENABLED = True
except ImportError:
    print("[SERVER] ⚠️  PDF libs missing. Run: 'pip install markdown2 xhtml2pdf'")
    PDF_ENABLED = False

# --- ROBUST IMPORT LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.memory import Memory
    mem = Memory()
    from tools.brain import Brain
    brain = Brain()
    import reweigh_queue
except Exception as e:
    print(f"[SERVER] ⚠️ CRITICAL: Could not load Memory/Brain module.\nError: {e}")
    traceback.print_exc()

FEEDBACK_FILE = "data/tactical_feedback.txt"
DEPLOY_FOLDER = "data/deployments"

# --- CALIBRI DOUBLE-RULE RESUME STYLING (TABLE LAYOUT) ---
RESUME_CSS = """
<style>
    @page { 
        size: letter; 
        margin: 0.5in; 
        margin-top: 0.5in;
        margin-bottom: 0.5in;
    }
    body { 
        font-family: 'Calibri', 'Carlito', 'Helvetica', 'Arial', sans-serif; 
        font-size: 10.5pt; 
        line-height: 1.35; 
        color: #000; 
    }
    
    /* --- HEADER SECTION --- */
    .header-block {
        text-align: center;
        margin-bottom: 12px;
    }
    
    .name-text {
        font-family: 'Calibri', 'Carlito', 'Helvetica', 'Arial', sans-serif; 
        font-size: 18pt;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 8px;
        color: #000;
    }

    /* The "Sandwich" Target Title */
    .target-title-box {
        font-size: 11pt;
        font-weight: bold;
        border-top: 1.5pt solid #000;    
        border-bottom: 1.5pt solid #000;
        padding-top: 4px;
        padding-bottom: 4px;
        margin-bottom: 6px;
        width: 100%;
    }

    .contact-text {
        font-size: 10pt;
        font-weight: normal;
        margin-top: 4px;
    }
    
    a { text-decoration: none; color: #000; }

    /* --- SECTIONS --- */
    h2 { 
        font-family: 'Calibri', 'Carlito', 'Helvetica', 'Arial', sans-serif; 
        font-size: 12pt; 
        font-weight: bold; 
        text-transform: uppercase; 
        margin-top: 15px;      
        margin-bottom: 8px; 
        border-bottom: 1pt solid #000; 
        padding-bottom: 2px;
    }

    /* --- JOB ENTRIES (TABLE LAYOUT) --- */
    .entry-table {
        width: 100%;
        margin-top: 8px;
        margin-bottom: 2px;
        border: none;
    }
    .left-cell {
        text-align: left;
        font-weight: bold;
        font-size: 11pt;
        vertical-align: bottom;
    }
    .right-cell {
        text-align: right;
        font-weight: normal;
        font-size: 10.5pt;
        vertical-align: bottom;
        white-space: nowrap; 
    }
    
    /* --- CONTENT --- */
    p { margin-top: 0; margin-bottom: 4px; text-align: justify; }
    ul { margin-top: 2px; margin-bottom: 8px; padding-left: 12px; }
    li { margin-bottom: 3px; } 
    strong { font-weight: bold; }

    .keep-together {
        page-break-inside: avoid;
    }
    
</style>
"""

CONTACT_INFO = """Boston, MA | (904) 304-2890 | <a href="mailto:lucas@lucasmougeot.ai">lucas@lucasmougeot.ai</a> | <a href="https://www.lucasmougeot.ai">lucasmougeot.ai</a>"""
DEFAULT_COMPETENCY = "AI Platform & Deterministic LLM Infrastructure"

# --- STANDALONE PDF CONVERTER ---
def convert_to_pdf(md_path, output_path, target_role_arg=None):
    if not PDF_ENABLED:
        return False
        
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # --- 1. PARSE FRONTMATTER ---
        fm_title = None
        fm_competency = None
        
        if md_text.startswith('---'):
            try:
                parts = md_text.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    md_text = parts[2] # Strip frontmatter from body
                    
                    title_match = re.search(r'target_title:\s*"(.*?)"', frontmatter)
                    if title_match: fm_title = title_match.group(1)
                    
                    comp_match = re.search(r'core_competency:\s*"(.*?)"', frontmatter)
                    if comp_match: fm_competency = comp_match.group(1)
            except Exception as e:
                print(f"[SERVER] Frontmatter Parse Error: {e}")

        # --- 2. HEADER CONSTRUCTION STRATEGY ---
        final_title = fm_title if fm_title else (target_role_arg if target_role_arg else "Software Engineer")
        final_competency = fm_competency if fm_competency else DEFAULT_COMPETENCY
        
        header_title = f"{final_title} | {final_competency}"

        # --- 3. STANDARD CONVERSION ---
        name = "LUCAS MOUGEOT" 
        lines = md_text.split('\n')
        if lines[0].strip().startswith('# '):
            md_text = '\n'.join(lines[1:]) 
        
        html_body = markdown2.markdown(md_text)
        
        def header_replacer(match):
            full_text = match.group(1)
            date_match = re.search(r'\(([^)]+)\)$', full_text)
            
            if date_match:
                date_text = date_match.group(1)
                title_text = full_text[:date_match.start()].strip()
                return f"""
                <div class="keep-together">
                    <table class="entry-table">
                        <tr>
                            <td class="left-cell">{title_text}</td>
                            <td class="right-cell">{date_text}</td>
                        </tr>
                    </table>
                """ 
            else:
                return f'<div class="entry-header"><strong>{full_text}</strong></div>'

        html_body = re.sub(r'<h3>(.*?)</h3>', header_replacer, html_body)

        full_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            {RESUME_CSS}
        </head>
        <body>
            <div class="header-block">
                <div class="name-text">{name}</div>
                <div class="target-title-box">{header_title}</div>
                <div class="contact-text">{CONTACT_INFO}</div>
            </div>
            {html_body}
        </body>
        </html>
        """
        
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, "w", encoding='utf-8') as f:
            f.write(full_html)

        with open(output_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)
            
        if pisa_status.err:
            print(f"[SERVER] PDF Generation Error: {pisa_status.err}")
            return False
            
        return True
    except Exception as e:
        print(f"[SERVER] PDF Conversion Exception: {e}")
        traceback.print_exc()
        return False

class CRMHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

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
            if self.path.startswith('/api/jobs'):
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
            else:
                super().do_GET()
        except Exception as e:
            print(f"[SERVER ERROR] Request failed: {e}")
            self.send_error(500)

    def _handle_get_jobs(self):
        status_filter = None
        if "?" in self.path:
            query = self.path.split("?")[1]
            if "status=" in query:
                status_filter = query.split("status=")[1].split("&")[0]
        jobs = mem.get_jobs(status_filter)
        self._send_json(jobs)

    def _handle_get_stats(self):
        stats = mem.get_global_stats()
        self._send_json(stats)

    def _handle_get_rules(self):
        if not os.path.exists(FEEDBACK_FILE):
            self._send_json({"rules": ""})
            return
        with open(FEEDBACK_FILE, "r") as f:
            self._send_json({"rules": f.read()})

    def _handle_get_agenda(self):
        conn = mem._get_conn()
        conn.row_factory = lambda cursor, row: row[0]
        terms = conn.execute("SELECT term FROM agenda WHERE status='PENDING' ORDER BY added_at ASC").fetchall()
        conn.close()
        self._send_json({"agenda": terms, "count": len(terms)})

    def _handle_get_logs(self):
        logs = mem.get_mission_logs(limit=50)
        self._send_json(logs)

    def _handle_get_all_logs(self):
        logs = mem.get_all_mission_logs()
        self._send_json(logs)

    def _handle_get_resume(self):
        if "?" not in self.path or "name=" not in self.path:
            self.send_error(400, "Missing name parameter")
            return
            
        query = self.path.split("?")[1]
        name_param = [p.split("=")[1] for p in query.split("&") if p.startswith("name=")][0]
        clean_name = os.path.basename(name_param) 
        
        target_path = os.path.join(MD_FOLDER, f"{clean_name}.md")
        
        content = ""
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f: content = f.read()
        else:
            search_pattern = os.path.join(MD_FOLDER, "**", f"{clean_name}.md")
            matches = glob.glob(search_pattern, recursive=True)
            if matches:
                with open(matches[0], "r", encoding="utf-8") as f: content = f.read()
            else:
                content = "# Resume Not Found on Disk"
        
        self._send_json({"content": content})

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            if self.path == '/api/update_status':
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
                threading.Thread(target=reweigh_queue.run_assimilation, daemon=True).start()
                self._send_json({"success": True})
            
            elif self.path == '/api/agenda':
                data = json.loads(post_data)
                if 'command' in data:
                    command_text = data.get('command')
                    print(f"[COMMANDER] Parsing Intent: '{command_text}'")
                    terms = brain.parse_command(command_text)
                    print(f"[COMMANDER] Extracted Missions: {terms}")
                    mem.add_to_agenda(terms, source='USER')
                    mem.flag_purge_queue()
                    print(f"[COMMANDER] PURGE SIGNAL RAISED. Clearing deck for {len(terms)} new missions.")
                    self._send_json({"success": True, "terms": terms})
                elif 'term' in data:
                    mem.add_to_agenda(data.get('term'), source='USER')
                    self._send_json({"success": True})
                else:
                    self.send_error(400)
                    
            elif self.path == '/api/deploy':
                data = json.loads(post_data)
                resume_name = data.get('resume')
                target_role = data.get('target_role', None)

                if resume_name:
                    clean_name = os.path.basename(resume_name)
                    if not clean_name.endswith('.md'):
                        clean_name += '.md'
                        
                    src_path = os.path.join(MD_FOLDER, clean_name)
                    
                    if not os.path.exists(DEPLOY_FOLDER):
                        os.makedirs(DEPLOY_FOLDER)
                    
                    dest_md = os.path.join(DEPLOY_FOLDER, clean_name)
                    dest_pdf = os.path.join(DEPLOY_FOLDER, clean_name.replace('.md', '.pdf'))
                    
                    if os.path.exists(src_path):
                        shutil.copy2(src_path, dest_md)
                        
                        # USE NEW STANDALONE FUNCTION
                        pdf_success = convert_to_pdf(src_path, dest_pdf, target_role)
                        
                        pdf_url = f"/{DEPLOY_FOLDER}/{clean_name.replace('.md', '.pdf')}"
                        html_url = f"/{DEPLOY_FOLDER}/{clean_name.replace('.md', '.html')}"
                        
                        response = {
                            "success": True, 
                            "path": dest_pdf if pdf_success else dest_md,
                            "url": pdf_url if pdf_success else html_url,
                            "format": "PDF" if pdf_success else "HTML"
                        }
                        self._send_json(response)
                    else:
                        self._send_json({"success": False, "error": "Source resume not found"})
                else:
                    self.send_error(400, "Missing resume parameter")
                    
            else:
                self.send_error(404)
        except Exception as e:
            print(f"[SERVER POST ERROR] {e}")
            traceback.print_exc()
            self.send_error(500)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    
    def handle_error(self, request, client_address):
        pass

def start_server():
    if os.path.basename(os.getcwd()) == "tools":
        os.chdir("..")

    if not os.path.exists("data"):
        os.makedirs("data")
        
    if not os.path.exists(DEPLOY_FOLDER):
        os.makedirs(DEPLOY_FOLDER)
    
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f: f.write("")

    try:
        with ThreadedHTTPServer(("0.0.0.0", PORT), CRMHandler) as httpd:
            print(f"[SERVER] API Online (Threaded): http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[SERVER] ❌ FAILED TO BIND: {e}")