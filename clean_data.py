import os
import sqlite3
from config import DB_FILE

FILES_TO_REMOVE = [
    "data/dashboard.json",
    "data/missions.json",
    "data/status.json"
]

def purge_data():
    print("=== CNS DATA PURGE ===")
    
    # 1. Delete DB and Feeds (Optional: Use specific flags for partial clears)
    if input("Delete entire database? (y/n): ").lower() == 'y':
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print(f"[DELETED] {DB_FILE}")
    
    for f in FILES_TO_REMOVE:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"[DELETED] {f}")
            except Exception as e:
                print(f"[ERROR] Could not delete {f}: {e}")

    # 2. Re-initialize empty feeds for UI stability
    os.makedirs("data", exist_ok=True)
    with open("data/dashboard.json", "w") as f: f.write("[]")
    with open("data/missions.json", "w") as f: f.write("[]")
    with open("data/status.json", "w") as f: f.write('{"queue_size": 0}')

    print("\n[SUCCESS] Memory wiped. Ready for a clean boot.")

def flush_agenda():
    print("=== FLUSHING PENDING AGENDA ===")
    if not os.path.exists(DB_FILE):
        print("No database found.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM agenda WHERE status='PENDING'")
    conn.commit()
    count = c.rowcount
    conn.close()
    print(f"[SUCCESS] Removed {count} pending items from Agenda.")

if __name__ == "__main__":
    print("1. Full Wipe (Delete DB + Feeds)")
    print("2. Flush Pending Agenda Only")
    choice = input("Select Action: ")
    
    if choice == "1":
        purge_data()
    elif choice == "2":
        flush_agenda()