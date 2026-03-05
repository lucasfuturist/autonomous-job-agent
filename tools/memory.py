import sqlite3
import json
import os
import random
from config import DB_FILE, JSON_FEED, MISSIONS_FEED, STATUS_FEED, MIN_SCORE

class Memory:
    def __init__(self):
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
        
        c.execute('''CREATE TABLE IF NOT EXISTS missions
                     (term TEXT PRIMARY KEY,
                      last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      times_searched INTEGER DEFAULT 0,
                      total_found INTEGER DEFAULT 0,
                      avg_score REAL DEFAULT 0.0)''')
        conn.commit()
        conn.close()

    # --- READ OPERATIONS (API) ---
    def get_jobs(self, status=None):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        
        if status and status != "ALL":
            rows = conn.execute("SELECT * FROM jobs WHERE status = ? ORDER BY found_at DESC", (status,)).fetchall()
        else:
            # REMOVED LIMIT 500. UI now handles rendering limits for performance.
            rows = conn.execute("""
                SELECT * FROM jobs 
                WHERE status IN ('TARGET', 'APPLIED', 'INTERVIEW', 'OFFER') 
                ORDER BY found_at DESC
            """).fetchall()
            
        conn.close()
        return [dict(r) for r in rows]

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

    # --- WRITE OPERATIONS ---
    def job_exists(self, url, company, title):
        conn = self._get_conn()
        res = conn.execute('''SELECT 1 FROM jobs 
                              WHERE url = ? OR (company = ? AND title = ?)''', 
                           (url, company, title)).fetchone()
        conn.close()
        return res is not None

    def save_job(self, job):
        if self.job_exists(job['url'], job['company'], job['title']): return False
        conn = self._get_conn()
        try:
            conn.execute('''INSERT INTO jobs (id, company, title, description, url, location)
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                         (job['id'], job['company'], job['title'], job['description'], job['url'], job['location']))
            conn.commit()
            return True
        except: return False
        finally: conn.close()

    def update_job(self, url, score, reason, resume):
        conn = self._get_conn()
        status_logic = f"CASE WHEN status = 'PENDING' AND {score} >= {MIN_SCORE} THEN 'TARGET' WHEN status = 'PENDING' THEN 'REJECTED' ELSE status END"
        conn.execute(f"UPDATE jobs SET score=?, reason=?, selected_resume=?, status={status_logic} WHERE url=?", 
                     (score, reason, resume, url))
        conn.commit()
        conn.close()
        if score >= MIN_SCORE: self.export_dashboard()

    def update_status(self, job_id, new_status):
        conn = self._get_conn()
        conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
        conn.commit()
        conn.close()
        self.export_dashboard() 

    # --- INTERNAL ---
    def get_gravitational_term(self):
        conn = self._get_conn()
        rows = conn.execute('''SELECT term FROM missions 
                               WHERE avg_score >= 5 AND total_found > 0
                               ORDER BY (total_found * avg_score) DESC 
                               LIMIT 5''').fetchall()
        conn.close()
        if rows: return random.choice(rows)[0]
        return None

    def get_stale_jobs(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''SELECT * FROM jobs WHERE status = 'PENDING' ''').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def log_mission_results(self, term, found_count, avg_score):
        conn = self._get_conn()
        conn.execute('''INSERT INTO missions (term, times_searched, total_found, avg_score) 
                        VALUES (?, 1, ?, ?)
                        ON CONFLICT(term) DO UPDATE SET 
                        last_searched=CURRENT_TIMESTAMP,
                        times_searched=times_searched + 1,
                        total_found=total_found + ?''',
                     (term, found_count, avg_score, found_count))
        conn.commit()
        conn.close()
        self.export_missions()

    def feedback_mission_quality(self, term, score):
        if not term: return
        conn = self._get_conn()
        conn.execute("UPDATE missions SET avg_score = (avg_score * 0.9) + (? * 0.1) WHERE term=?", (score, term))
        conn.commit()
        conn.close()
        self.export_missions()

    def export_dashboard(self):
        jobs = self.get_jobs()
        with open(JSON_FEED + ".tmp", "w") as f: json.dump(jobs[:500], f) # Cap JSON backup, API is uncapped
        os.replace(JSON_FEED + ".tmp", JSON_FEED)

    def export_missions(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM missions ORDER BY (total_found * avg_score) DESC LIMIT 15").fetchall()
        conn.close()
        data = [dict(row) for row in rows]
        with open(MISSIONS_FEED + ".tmp", "w") as f: json.dump(data, f)
        os.replace(MISSIONS_FEED + ".tmp", MISSIONS_FEED)
        
    def export_status(self, queue_size):
        data = {"queue_size": queue_size}
        with open(STATUS_FEED + ".tmp", "w") as f: json.dump(data, f)
        os.replace(STATUS_FEED + ".tmp", STATUS_FEED)