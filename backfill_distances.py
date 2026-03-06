import time
from tools.memory import Memory

def backfill():
    print("=== DISTANCE BACKFILL PROTOCOL ===")
    mem = Memory()
    conn = mem._get_conn()
    
    # 1. Find all distinct locations that don't have a distance yet
    # We look for NULL. The migration adds 'distance' as NULL by default.
    cursor = conn.execute("SELECT DISTINCT location FROM jobs WHERE distance IS NULL AND location != '' AND location IS NOT NULL")
    unique_locations = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    total = len(unique_locations)
    print(f"[NAV] Found {total} unique locations needing geocoding.")
    if total == 0:
        print("[NAV] Everything is up to date!")
        return

    print("[NAV] Beginning secure lookup. This honors Nominatim's 1 req/sec limit. Please wait...")
    
    # 2. Prime the cache sequentially
    for i, loc in enumerate(unique_locations):
        print(f"  [{i+1}/{total}] Locating: {loc} ... ", end="")
        dist = mem.get_or_fetch_distance(loc)
        
        if dist == -1.0:
            print("Remote")
        elif dist is not None:
            print(f"{dist} miles")
        else:
            print("Not Found")
            
    # 3. Bulk update the jobs table from the cache
    print("\n[NAV] Caching complete. Syncing jobs table...")
    conn = mem._get_conn()
    
    # Update jobs where distance is still null by joining with loc_cache
    # SQLite doesn't support UPDATE...JOIN easily, so we use a subquery
    update_sql = """
        UPDATE jobs 
        SET distance = (
            SELECT distance FROM loc_cache 
            WHERE loc_cache.loc = LOWER(TRIM(jobs.location))
        )
        WHERE distance IS NULL
    """
    
    cursor = conn.execute(update_sql)
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    
    print(f"[SUCCESS] {rows_updated} job records updated with distance metrics.")
    print("=== PROTOCOL COMPLETE ===")

if __name__ == "__main__":
    backfill()