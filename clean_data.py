import os

FILES_TO_REMOVE = [
    "data/targets.db",
    "data/dashboard.json",
    "data/missions.json",
    "data/status.json"
]

def purge_data():
    print("=== CNS DATA PURGE ===")
    
    # 1. Delete DB and Feeds
    for f in FILES_TO_REMOVE:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"[DELETED] {f}")
            except Exception as e:
                print(f"[ERROR] Could not delete {f}: {e}")
        else:
            print(f"[SKIPPED] {f} (Not found)")

    # 2. Re-initialize empty feeds for UI stability
    os.makedirs("data", exist_ok=True)
    with open("data/dashboard.json", "w") as f: f.write("[]")
    with open("data/missions.json", "w") as f: f.write("[]")
    with open("data/status.json", "w") as f: f.write('{"queue_size": 0}')

    print("\n[SUCCESS] Memory wiped. Ready for a clean boot.")

if __name__ == "__main__":
    purge_data()