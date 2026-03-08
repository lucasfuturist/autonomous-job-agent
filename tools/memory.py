# tools/memory.py
import sqlite3
import json
import os
import random
import math
import time
import urllib.parse
import urllib.request
from config import DB_FILE, JSON_FEED, MISSIONS_FEED, STATUS_FEED, MIN_SCORE

class Memory:
    def __init__(self):
        self.home_coords = (42.3601, -71.0589) # Boston, MA
        self.purge_flag_file = "data/signal_purge.flag"
        self.activity_file = "data/system_activity.json"
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30.0)

    def _init_db(self):
        conn = self._get_conn()
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS jobs
                     (id TEXT PRIMARY KEY, company TEXT, title TEXT, description TEXT, 
                      url TEXT, location TEXT, score INTEGER DEFAULT 0, reason TEXT,
                      selected_resume TEXT, status TEXT DEFAULT 'PENDING',
                      found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # --- MIGRATIONS ---
        migrations =[
            ("starred", "INTEGER DEFAULT 0"),
            ("distance", "REAL"),
            ("salary_base_min", "INTEGER"),
            ("salary_base_max", "INTEGER"),
            ("work_mode", "TEXT"),
            ("travel_pct_max", "INTEGER"),
            ("clearance_required", "TEXT"),
            ("itar_ear_restricted", "INTEGER"),
            ("tech_stack_core", "TEXT"),
            ("hardware_physical_tools", "TEXT"),
            ("yoe_actual", "INTEGER"),
            ("red_flags", "TEXT"),
            ("recruiters", "TEXT"),
            ("outreach_message", "TEXT")
        ]

        for col, dtype in migrations:
            try:
                c.execute(f"ALTER TABLE jobs ADD COLUMN {col} {dtype}")
            except sqlite3.OperationalError:
                pass 

        c.execute('''CREATE TABLE IF NOT EXISTS missions
                     (term TEXT PRIMARY KEY, last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      times_searched INTEGER DEFAULT 0, total_found INTEGER DEFAULT 0, avg_score REAL DEFAULT 0.0)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS mission_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT, run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      items_found INTEGER, items_new INTEGER)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS agenda
                     (term TEXT PRIMARY KEY, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      source TEXT DEFAULT 'SYSTEM', status TEXT DEFAULT 'PENDING')''')
        
        # Geocoding Cache
        c.execute('''CREATE TABLE IF NOT EXISTS loc_cache
                     (loc TEXT PRIMARY KEY, distance REAL)''')

        conn.commit()
        conn.close()

    # --- AGENT STATE & ACTIVITY ---
    def get_agent_state(self):
        state_file = "data/agent_state.json"
        if not os.path.exists(state_file):
            self.set_agent_state(False)
            return False
        try:
            with open(state_file, "r") as f:
                return json.load(f).get("active", False)
        except:
            return False

    def set_agent_state(self, is_active):
        with open("data/agent_state.json", "w") as f:
            json.dump({"active": is_active}, f)

    def set_system_activity(self, source, message):
        """Writes ephemeral status to a JSON file for the UI to poll."""
        try:
            data = {
                "source": source,
                "message": message,
                "timestamp": time.time()
            }
            # Atomic write not strictly necessary for this visualization but good practice
            tmp_file = self.activity_file + ".tmp"
            with open(tmp_file, "w") as f:
                json.dump(data, f)
            os.replace(tmp_file, self.activity_file)
        except Exception:
            pass # Non-critical logging

    def get_system_activity(self):
        if not os.path.exists(self.activity_file):
            return {"source": "SYSTEM", "message": "Idle", "timestamp": time.time()}
        try:
            with open(self.activity_file, "r") as f:
                return json.load(f)
        except:
            return {"source": "SYSTEM", "message": "Idle", "timestamp": time.time()}

    # --- SIGNALING ---
    def flag_purge_queue(self):
        with open(self.purge_flag_file, 'w') as f:
            f.write("1")

    def check_and_clear_purge_flag(self):
        if os.path.exists(self.purge_flag_file):
            try:
                os.remove(self.purge_flag_file)
                return True
            except:
                return False
        return False

    # --- GEOCODING ENGINE ---
    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 3958.8 
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def get_or_fetch_distance(self, loc_str):
        if not loc_str: return None
        loc_clean = loc_str.lower().strip()
        
        if 'remote' in loc_clean or 'anywhere' in loc_clean:
            return -1.0 

        conn = self._get_conn()
        res = conn.execute("SELECT distance FROM loc_cache WHERE loc = ?", (loc_clean,)).fetchone()
        
        if res:
            conn.close()
            return res[0]

        dist = None
        try:
            print(f"  [NAV] Uncached location detected: '{loc_str}'. Pinging satellite (1s delay)...")
            time.sleep(1.1) 
            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(loc_str)}&format=json&limit=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'CNS_Tactical_Agent/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    dist = round(self._haversine(self.home_coords[0], self.home_coords[1], lat, lon), 1)
        except Exception as e:
            print(f"[NAV] Geocoding failed for '{loc_str}': {e}")
        
        conn.execute("INSERT OR REPLACE INTO loc_cache (loc, distance) VALUES (?, ?)", (loc_clean, dist))
        conn.commit()
        conn.close()
        
        return dist

    # --- READ OPERATIONS ---
    def get_jobs(self, status=None):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        if status and status != "ALL":
            rows = conn.execute("SELECT * FROM jobs WHERE status = ? ORDER BY found_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM jobs WHERE status IN ('TARGET', 'APPLIED', 'INTERVIEW', 'OFFER') ORDER BY found_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    
    def get_job_by_id(self, job_id):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_recruiters_for_company(self, company):
        if not company: return None
        conn = self._get_conn()
        row = conn.execute("SELECT recruiters FROM jobs WHERE company = ? AND recruiters IS NOT NULL AND recruiters != '' LIMIT 1", (company,)).fetchone()
        conn.close()
        if row and row[0]:
            try:
                return json.loads(row[0])
            except:
                return None
        return None

    def get_global_stats(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        stats = {}
        rows = conn.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status").fetchall()
        stats['pipeline'] = {r['status']: r['count'] for r in rows}
        stats['total_scanned'] = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        stats['avg_quality'] = conn.execute("SELECT AVG(score) FROM jobs WHERE status != 'REJECTED'").fetchone()[0] or 0
        mission_rows = conn.execute("SELECT term, avg_score, total_found FROM missions ORDER BY avg_score DESC LIMIT 5").fetchall()
        stats['strategies'] = [dict(r) for r in mission_rows]
        conn.close()
        return stats
    
    def get_mission_logs(self, limit=50):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM mission_logs ORDER BY run_at DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_mission_logs(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM mission_logs ORDER BY run_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- WRITE OPERATIONS ---
    def job_exists(self, url, company, title):
        conn = self._get_conn()
        res = conn.execute('''SELECT 1 FROM jobs WHERE url = ? OR (company = ? AND title = ?)''', (url, company, title)).fetchone()
        conn.close()
        return res is not None

    def save_job(self, job):
        if self.job_exists(job['url'], job['company'], job['title']): return False
        
        distance = self.get_or_fetch_distance(job.get('location', ''))

        conn = self._get_conn()
        try:
            conn.execute('''INSERT INTO jobs (id, company, title, description, url, location, distance)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (job['id'], job['company'], job['title'], job['description'], job['url'], job['location'], distance))
            conn.commit()
            return True
        except: return False
        finally: conn.close()
        
    def update_job_description(self, job_id, description):
        conn = self._get_conn()
        conn.execute("UPDATE jobs SET description = ? WHERE id = ?", (description, job_id))
        conn.commit()
        conn.close()

    def update_job(self, url, score, reason, resume, analysis_data=None):
        if analysis_data is None: analysis_data = {}
        
        salary_min = analysis_data.get('salary_base_min')
        salary_max = analysis_data.get('salary_base_max')
        work_mode = analysis_data.get('work_mode')
        travel = analysis_data.get('travel_pct_max')
        clearance = analysis_data.get('clearance_required')
        itar = 1 if analysis_data.get('itar_ear_restricted') else 0
        tech_stack = json.dumps(analysis_data.get('tech_stack_core',[]))
        hardware = json.dumps(analysis_data.get('hardware_physical_tools',[]))
        yoe = analysis_data.get('yoe_actual')
        red_flags = json.dumps(analysis_data.get('red_flags',[]))

        conn = self._get_conn()
        
        # We only update status logic if score is provided and above threshold. 
        # If score is None (partial update), we skip status logic.
        status_update_sql = ""
        if score is not None:
             status_update_sql = f", status = CASE WHEN status = 'PENDING' AND {score} >= {MIN_SCORE} THEN 'TARGET' WHEN status = 'PENDING' THEN 'REJECTED' ELSE status END"
        
        sql = f"""
            UPDATE jobs SET 
                reason=?, selected_resume=?,
                salary_base_min=?, salary_base_max=?, work_mode=?, travel_pct_max=?,
                clearance_required=?, itar_ear_restricted=?, tech_stack_core=?,
                hardware_physical_tools=?, yoe_actual=?, red_flags=?
                {", score=?" if score is not None else ""}
                {status_update_sql}
            WHERE url=?
        """
        
        params = [
            reason, resume,
            salary_min, salary_max, work_mode, travel,
            clearance, itar, tech_stack,
            hardware, yoe, red_flags
        ]
        
        if score is not None:
            params.append(score)
            
        params.append(url)
        
        conn.execute(sql, tuple(params))
        conn.commit()
        conn.close()
        if score is not None and score >= MIN_SCORE: self.export_dashboard()
        else: self.export_dashboard() # Always export on manual updates

    def update_recruiters_for_company(self, company, recruiters_list):
        if not company or not recruiters_list: return
        data = json.dumps(recruiters_list)
        conn = self._get_conn()
        conn.execute("UPDATE jobs SET recruiters = ? WHERE company = ?", (data, company))
        conn.commit()
        conn.close()
        self.export_dashboard()

    def update_recruiters_by_id(self, job_id, recruiters_list):
        if not job_id: return
        data = json.dumps(recruiters_list)
        conn = self._get_conn()
        conn.execute("UPDATE jobs SET recruiters = ? WHERE id = ?", (data, job_id))
        conn.commit()
        conn.close()
        self.export_dashboard()

    def toggle_recruiter_outreach(self, job_id, url, contacted):
        conn = self._get_conn()
        row = conn.execute("SELECT recruiters FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row and row[0]:
            try:
                recruiters = json.loads(row[0])
                updated = False
                for r in recruiters:
                    if r.get('url') == url:
                        r['contacted'] = contacted
                        updated = True
                if updated:
                    conn.execute("UPDATE jobs SET recruiters = ? WHERE id = ?", (json.dumps(recruiters), job_id))
                    conn.commit()
            except:
                pass
        conn.close()
        self.export_dashboard()

    def add_manual_recruiter(self, job_id, url):
        if not job_id or not url: return
        conn = self._get_conn()
        row = conn.execute("SELECT recruiters FROM jobs WHERE id = ?", (job_id,)).fetchone()
        recruiters = []
        if row and row[0]:
            try:
                recruiters = json.loads(row[0])
            except:
                pass
        
        if not any(r.get('url') == url for r in recruiters):
            recruiters.append({
                "name": "Manually Added Profile",
                "title": "Recruiter / Talent",
                "url": url,
                "contacted": True
            })
            conn.execute("UPDATE jobs SET recruiters = ? WHERE id = ?", (json.dumps(recruiters), job_id))
            conn.commit()
        conn.close()
        self.export_dashboard()
        
    def update_outreach_message(self, job_id, message):
        if not job_id or not message: return
        conn = self._get_conn()
        conn.execute("UPDATE jobs SET outreach_message = ? WHERE id = ?", (message, job_id))
        conn.commit()
        conn.close()
        self.export_dashboard()

    def update_status(self, job_id, new_status):
        conn = self._get_conn()
        conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
        conn.commit()
        conn.close()
        self.export_dashboard() 

    def toggle_star(self, job_id, starred_status):
        conn = self._get_conn()
        val = 1 if starred_status else 0
        conn.execute("UPDATE jobs SET starred = ? WHERE id = ?", (val, job_id))
        conn.commit()
        conn.close()
        self.export_dashboard()

    def bulk_reject(self, purge_list):
        if not purge_list: return
        conn = self._get_conn()
        try:
            conn.executemany("UPDATE jobs SET score=0, status='REJECTED', reason=? WHERE id=?", purge_list)
            conn.commit()
        finally:
            conn.close()
        self.export_dashboard()

    # --- AGENDA & HISTORY ---
    def add_to_agenda(self, terms, source='SYSTEM'):
        if not terms: return
        if isinstance(terms, str): terms = [terms]
        conn = self._get_conn()
        count = 0
        for term in terms:
            try:
                conn.execute("INSERT OR IGNORE INTO agenda (term, source) VALUES (?, ?)", (term, source))
                count += 1
            except: pass
        conn.commit()
        conn.close()

    def recover_agenda(self):
        conn = self._get_conn()
        conn.execute("UPDATE agenda SET status='PENDING', source='RECOVERY' WHERE status='PROCESSING'")
        conn.commit()
        conn.close()

    def peek_next_agenda_item(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        query = """
            SELECT term, source FROM agenda 
            WHERE status='PENDING' 
            ORDER BY 
                CASE 
                    WHEN source='USER' THEN 0 
                    WHEN source='RECOVERY' THEN 1 
                    ELSE 2 
                END, 
                added_at ASC 
            LIMIT 1
        """
        row = conn.execute(query).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_next_agenda_item(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        query = """
            SELECT term, source FROM agenda 
            WHERE status='PENDING' 
            ORDER BY 
                CASE 
                    WHEN source='USER' THEN 0 
                    WHEN source='RECOVERY' THEN 1 
                    ELSE 2 
                END, 
                added_at ASC 
            LIMIT 1
        """
        row = conn.execute(query).fetchone()
        term = None
        if row:
            term = row['term']
            conn.execute("UPDATE agenda SET status='PROCESSING' WHERE term = ?", (term,))
            conn.commit()
        conn.close()
        return term

    def mark_agenda_complete(self, term):
        conn = self._get_conn()
        conn.execute("DELETE FROM agenda WHERE term = ?", (term,))
        conn.commit()
        conn.close()

    def reset_mission_status(self, term):
        conn = self._get_conn()
        conn.execute("UPDATE agenda SET status='PENDING' WHERE term = ?", (term,))
        conn.commit()
        conn.close()

    def get_agenda_status(self):
        conn = self._get_conn()
        count = conn.execute("SELECT COUNT(*) FROM agenda WHERE status='PENDING'").fetchone()[0]
        conn.close()
        return count

    def get_gravitational_term(self, cooldown_hours=24):
        conn = self._get_conn()
        query = f'''SELECT term FROM missions 
                    WHERE avg_score >= 5 AND total_found > 0 AND last_searched < datetime('now', '-{cooldown_hours} hours')
                    ORDER BY (total_found * avg_score) DESC LIMIT 5'''
        rows = conn.execute(query).fetchall()
        conn.close()
        if rows: return random.choice(rows)[0]
        return None

    def filter_cooldown_terms(self, terms, hours=24):
        if not terms: return[]
        conn = self._get_conn()
        placeholders = ','.join('?' for _ in terms)
        query = f'''SELECT term FROM missions WHERE term IN ({placeholders}) AND last_searched > datetime('now', '-{hours} hours')'''
        recently_searched = {row[0] for row in conn.execute(query, terms).fetchall()}
        conn.close()
        return [t for t in terms if t not in recently_searched]

    def get_stale_jobs(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''SELECT * FROM jobs WHERE status = 'PENDING' ''').fetchall()
        conn.close()
        return[dict(r) for r in rows]

    def log_mission_results(self, term, found_count, new_count, avg_score=0):
        conn = self._get_conn()
        conn.execute('''INSERT INTO missions (term, times_searched, total_found, avg_score) 
                        VALUES (?, 1, ?, ?)
                        ON CONFLICT(term) DO UPDATE SET last_searched=CURRENT_TIMESTAMP, times_searched=times_searched + 1, total_found=total_found + ?''',
                     (term, found_count, avg_score, found_count))
        conn.execute("INSERT INTO mission_logs (term, items_found, items_new) VALUES (?, ?, ?)", (term, found_count, new_count))
        conn.commit()
        conn.close()
        self.export_missions()

    def feedback_mission_quality(self, term, score):
        if not term: return
        conn = self._get_conn()
        conn.execute("UPDATE missions SET avg_score = (avg_score * 0.9) + (? * 0.1) WHERE term=?", (score, term))
        conn.commit()
        conn.close()

    def export_dashboard(self):
        jobs = self.get_jobs()
        with open(JSON_FEED + ".tmp", "w") as f: json.dump(jobs[:500], f)
        os.replace(JSON_FEED + ".tmp", JSON_FEED)

    def export_missions(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM missions ORDER BY (total_found * avg_score) DESC LIMIT 15").fetchall()
        conn.close()
        with open(MISSIONS_FEED + ".tmp", "w") as f: json.dump([dict(r) for r in rows], f)
        os.replace(MISSIONS_FEED + ".tmp", MISSIONS_FEED)
        
    def export_status(self, queue_size):
        with open(STATUS_FEED + ".tmp", "w") as f: json.dump({"queue_size": queue_size}, f)
        os.replace(STATUS_FEED + ".tmp", STATUS_FEED)