import sqlite3
from config import DB_FILE

def migrate():
    print("=== MIGRATING DATABASE FILENAMES ===")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get all jobs with resumes that might need fixing
        cursor.execute("SELECT id, selected_resume FROM jobs WHERE selected_resume IS NOT NULL AND selected_resume != 'N/A' AND selected_resume != 'Default'")
        rows = cursor.fetchall()
        
        updates = []
        
        for job_id, resume in rows:
            original = resume
            new_name = original
            
            # 1. Strip 'nan' prefix/substring (matching rebuild_pdfs.py logic)
            if 'nan' in new_name:
                new_name = new_name.replace('nan_', '').replace('_nan', '')
                if new_name.startswith('_'): new_name = new_name[1:]

            # 2. Migrate JIT -> Lucas_Mougeot
            if '_JIT' in new_name:
                new_name = new_name.replace('_JIT', '_Lucas_Mougeot')
                
            if new_name != original:
                updates.append((new_name, job_id))
                # print(f"  [DB] {original} -> {new_name}") # Uncomment for verbose logs
                
        if updates:
            print(f"[DB] Found {len(updates)} records pointing to old filenames.")
            cursor.executemany("UPDATE jobs SET selected_resume = ? WHERE id = ?", updates)
            conn.commit()
            print(f"[SUCCESS] Database sync complete. Pointers updated.")
        else:
            print("[INFO] Database is already in sync with file system.")
            
        conn.close()
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")

if __name__ == "__main__":
    migrate()