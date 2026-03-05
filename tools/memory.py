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
        
        # Core Jobs Table
        c.execute('''CREATE TABLE IF NOT EXISTS jobs
                     (id TEXT PRIMARY KEY, company TEXT, title TEXT, description TEXT, 
                      url TEXT, location TEXT, score INTEGER DEFAULT 0, reason TEXT,
                      selected_resume TEXT, status TEXT DEFAULT 'PENDING',
                      found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # MIGRATION: Add 'starred' column if missing
        try:
            c.execute("ALTER TABLE jobs ADD COLUMN starred INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Column likely exists

        # Missions/Strategy
        c.execute('''CREATE TABLE IF NOT EXISTS missions
                     (term TEXT PRIMARY KEY,
                      last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      times_searched INTEGER DEFAULT 0,
                      total_found INTEGER DEFAULT 0,
                      avg_score REAL DEFAULT 0.0)''')
        
        # Audit Logs
        c.execute('''CREATE TABLE IF NOT EXISTS mission_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      term TEXT,
                      run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      items_found INTEGER,
                      items_new INTEGER)''')
        
        # Persistent Agenda
        c.execute('''CREATE TABLE IF NOT EXISTS agenda
                     (term TEXT PRIMARY KEY,
                      added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      source TEXT DEFAULT 'SYSTEM',
                      status TEXT DEFAULT 'PENDING')''')
        conn.commit()
        conn.close()

    # --- READ OPERATIONS ---
    def get_jobs(self, status=None):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        
        if status and status != "ALL":
            rows = conn.execute("SELECT * FROM jobs WHERE status = ? ORDER BY found_at DESC", (status,)).fetchall()
        else:
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
    
    def get_mission_logs(self, limit=50):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM mission_logs ORDER BY run_at DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

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

    def toggle_star(self, job_id, starred_status):
        conn = self._get_conn()
        # Ensure we write 1 or 0
        val = 1 if starred_status else 0
        conn.execute("UPDATE jobs SET starred = ? WHERE id = ?", (val, job_id))
        conn.commit()
        conn.close()
        self.export_dashboard()

    # --- AGENDA OPERATIONS ---
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
        if count > 0:
            print(f"[MEMORY] 📅 Added {count} terms to Persistent Agenda.")

    def get_next_agenda_item(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT term FROM agenda WHERE status='PENDING' ORDER BY added_at ASC LIMIT 1").fetchone()
        
        term = None
        if row:
            term = row['term']
            conn.execute("DELETE FROM agenda WHERE term = ?", (term,))
            conn.commit()
            
        conn.close()
        return term

    def get_agenda_status(self):
        conn = self._get_conn()
        count = conn.execute("SELECT COUNT(*) FROM agenda WHERE status='PENDING'").fetchone()[0]
        conn.close()
        return count

    # --- HISTORY & STRATEGY ---
    def get_gravitational_term(self, cooldown_hours=24):
        conn = self._get_conn()
        query = f'''SELECT term FROM missions 
                    WHERE avg_score >= 5 
                    AND total_found > 0
                    AND last_searched < datetime('now', '-{cooldown_hours} hours')
                    ORDER BY (total_found * avg_score) DESC 
                    LIMIT 5'''
        rows = conn.execute(query).fetchall()
        conn.close()
        if rows: return random.choice(rows)[0]
        return None

    def filter_cooldown_terms(self, terms, hours=24):
        if not terms: return []
        conn = self._get_conn()
        placeholders = ','.join('?' for _ in terms)
        query = f'''SELECT term FROM missions 
                    WHERE term IN ({placeholders}) 
                    AND last_searched > datetime('now', '-{hours} hours')'''
        
        recently_searched = {row[0] for row in conn.execute(query, terms).fetchall()}
        conn.close()
        
        return [t for t in terms if t not in recently_searched]

    def get_stale_jobs(self):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''SELECT * FROM jobs WHERE status = 'PENDING' ''').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def log_mission_results(self, term, found_count, new_count, avg_score=0):
        conn = self._get_conn()
        
        conn.execute('''INSERT INTO missions (term, times_searched, total_found, avg_score) 
                        VALUES (?, 1, ?, ?)
                        ON CONFLICT(term) DO UPDATE SET 
                        last_searched=CURRENT_TIMESTAMP,
                        times_searched=times_searched + 1,
                        total_found=total_found + ?''',
                     (term, found_count, avg_score, found_count))
        
        conn.execute("INSERT INTO mission_logs (term, items_found, items_new) VALUES (?, ?, ?)", 
                     (term, found_count, new_count))
        
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
        with open(JSON_FEED + ".tmp", "w") as f: json.dump(jobs[:500], f)
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