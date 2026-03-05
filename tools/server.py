import http.server
import socketserver
import sys
import json
import os
import traceback
import threading
import glob
import subprocess
import tempfile
from config import PORT, MD_FOLDER

# --- ROBUST IMPORT LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.memory import Memory
    mem = Memory()
    import reweigh_queue
except Exception as e:
    print(f"[SERVER] ⚠️ CRITICAL: Could not load Memory module.\nError: {e}")
    traceback.print_exc()

FEEDBACK_FILE = "data/tactical_feedback.txt"

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
                term = data.get('term')
                if term:
                    print(f"[SERVER] 📥 Manual Mission Injection: {term}")
                    mem.add_to_agenda(term, source='USER')
                    self._send_json({"success": True})
                else:
                    self.send_error(400)
                    
            elif self.path == '/api/run_script':
                data = json.loads(post_data)
                script_content = data.get('script', '')
                if script_content:
                    # Append command to open explorer and highlight the target file
                    script_content += "\nexplorer.exe /select,$dest"
                    
                    # Create a temporary ps1 file
                    fd, path = tempfile.mkstemp(suffix=".ps1")
                    with os.fdopen(fd, 'w') as f:
                        f.write(script_content)
                    
                    try:
                        print("[SERVER] Executing Deployment Script...")
                        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", path], check=True)
                        os.remove(path)
                        self._send_json({"success": True})
                    except Exception as e:
                        print(f"[SERVER] Error running script: {e}")
                        self.send_error(500, str(e))
                else:
                    self.send_error(400)
                    
            else:
                self.send_error(404)
        except Exception as e:
            print(f"[SERVER POST ERROR] {e}")
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
    
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f: f.write("")

    try:
        with ThreadedHTTPServer(("0.0.0.0", PORT), CRMHandler) as httpd:
            print(f"[SERVER] API Online (Threaded): http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[SERVER] ❌ FAILED TO BIND: {e}")