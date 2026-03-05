import sqlite3
import os
import sys

# Configuration
DB_PATH = "data/targets.db"

def verify_missions():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found at {DB_PATH}")
        return

    print(f"--- INSPECTING STRATEGY LAYER: {DB_PATH} ---")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check Table Schema
        cursor.execute("PRAGMA table_info(missions)")
        columns = [row['name'] for row in cursor.fetchall()]
        
        if 'avg_score' not in columns:
            print("[FAIL] Schema outdated. Missing 'avg_score'.")
            return

        # Dump Data
        cursor.execute("SELECT * FROM missions ORDER BY avg_score DESC, total_found DESC LIMIT 15")
        rows = cursor.fetchall()
        
        if not rows:
            print("[INFO] 'missions' table exists but is empty.")
        else:
            print(f"\n[DATA] Strategy Performance (Sorted by Quality):\n")
            print(f"{'TERM':<45} | {'RUNS':<5} | {'FOUND':<6} | {'AVG SCORE':<10} | {'LAST RUN'}")
            print("-" * 95)
            for row in rows:
                score = round(row['avg_score'], 2)
                print(f"{row['term']:<45} | {row['times_searched']:<5} | {row['total_found']:<6} | {score:<10} | {row['last_searched']}")

    except sqlite3.OperationalError as e:
        print(f"[ERROR] SQL Error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    verify_missions()