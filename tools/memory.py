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
        status = "TARGET" if score >= MIN_SCORE else "REJECTED"
        conn.execute("UPDATE jobs SET score=?, reason=?, selected_resume=?, status=? WHERE url=?", 
                     (score, reason, resume, status, url))
        conn.commit()
        conn.close()
        if score >= MIN_SCORE: self.export_dashboard()

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

    def get_gravitational_term(self):
        """Pulls the best performing term based on Quantity * Quality."""
        conn = self._get_conn()
        # Fetch top 5 most successful terms to add slight variation
        rows = conn.execute('''SELECT term FROM missions 
                               WHERE avg_score >= 5 AND total_found > 0
                               ORDER BY (total_found * avg_score) DESC 
                               LIMIT 5''').fetchall()
        conn.close()
        if rows:
            return random.choice(rows)[0]
        return None

    def get_stale_jobs(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''SELECT * FROM jobs 
                               WHERE status = 'PENDING' ''').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def export_dashboard(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM jobs WHERE status = 'TARGET' ORDER BY found_at DESC LIMIT 500").fetchall()
        conn.close()
        data = [dict(row) for row in rows]
        with open(JSON_FEED + ".tmp", "w") as f: json.dump(data, f)
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