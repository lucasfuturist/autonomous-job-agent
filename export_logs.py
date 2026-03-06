import csv
from tools.memory import Memory

def export():
    mem = Memory()
    logs = mem.get_all_mission_logs()
    
    filename = "data/mission_history.csv"
    
    if not logs:
        print("No logs found.")
        return

    # Use keys from first record as headers
    headers = logs[0].keys()
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(logs)
        print(f"[SUCCESS] Exported {len(logs)} records to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to export: {e}")

if __name__ == "__main__":
    export()