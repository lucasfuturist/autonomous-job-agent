import http.server
import socketserver
import sys
import json
import os
import traceback
import threading
from config import PORT

# --- ROBUST IMPORT LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.memory import Memory
    mem = Memory()
except Exception as e:
    print(f"[SERVER] ⚠️ CRITICAL: Could not load Memory module.\nError: {e}")
    traceback.print_exc()

class CRMHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence logs to keep terminal clean
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
            else:
                super().do_GET()
        except Exception as e:
            print(f"[SERVER ERROR] Request failed: {e}")
            self.send_error(500)

    def _handle_get_jobs(self):
        # Query Params logic
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

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        try:
            if self.path == '/api/update_status':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                job_id = data.get('id')
                status = data.get('status')
                
                if job_id and status:
                    # print(f"[API] Updating Job {job_id} -> {status}")
                    mem.update_status(job_id, status)
                    self._send_json({"success": True})
                else:
                    self.send_error(400, "Missing id or status")
            else:
                self.send_error(404)
        except Exception as e:
            print(f"[SERVER POST ERROR] {e}")
            self.send_error(500)

# --- THREADED SERVER ---
# This is the critical fix. It allows multiple API calls at once.
class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    
    def handle_error(self, request, client_address):
        # prevent minor socket errors from crashing the thread
        pass

def start_server():
    if os.path.basename(os.getcwd()) == "tools":
        os.chdir("..")

    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        # Use the Threaded version
        with ThreadedHTTPServer(("0.0.0.0", PORT), CRMHandler) as httpd:
            print(f"[SERVER] API Online (Threaded): http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[SERVER] ❌ FAILED TO BIND: {e}")