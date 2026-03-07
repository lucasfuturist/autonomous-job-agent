import os
import glob
import json
from config import MD_FOLDER
from tools.server import convert_to_pdf

# Backfill script to detect if any historical job roles were entirely dropped
# by the LLM in existing resumes. It forcefully injects the top 2 bullets
# for any missing role at the bottom of the "Relevant Experience" section
# to ensure the candidate's full chronological timeline is represented.

def run_backfill():
    # 1. Load Master Data
    master_path = "data/master_career_data.json"
    if not os.path.exists(master_path):
        print("[ERROR] Master data JSON not found.")
        return
        
    with open(master_path, 'r', encoding='utf-8') as f:
        master = json.load(f)
        
    experiences = master.get('experience', [])
    
    files = glob.glob(os.path.join(MD_FOLDER, "*.md"))
    print(f"[BACKFILL] Scanning {len(files)} resumes for truncated timelines...")
    
    count = 0
    for f in files:
        filename = os.path.basename(f)
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        missing_blocks = ""
        
        # 2. Check each job title
        for exp in experiences:
            # We check by exact title match (e.g. "Undergraduate Researcher — Computational Geometry")
            if exp['title'] not in content:
                print(f"  -> Anti-Truncation Trigger: Injecting '{exp['title']}' into {filename}")
                
                missing_blocks += f"### {exp['title']} at {exp['company']} ({exp.get('dates', '')})\n"
                # Add exactly 2 bullets to keep it concise but present
                for b in exp.get('standardized_bullets', [])[:2]:
                    missing_blocks += f"- {b['text']}\n"
                missing_blocks += "\n"
                
        # 3. Inject missing blocks if any were found
        if missing_blocks:
            # Inject right before the Core Skills header so it stays in the Experience section
            if "## Core Skills\n" in content:
                new_content = content.replace("## Core Skills\n", missing_blocks + "## Core Skills\n")
                
                with open(f, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                    
                # Regenerate PDF silently
                pdf_path = f.replace('.md', '.pdf').replace('output_mds', 'deployments')
                convert_to_pdf(f, pdf_path)
                
                count += 1
            else:
                print(f"  [ERROR] Could not find anchor '## Core Skills' in {filename}")

    print(f"\n[BACKFILL] Complete. {count} resumes patched to reflect full 2020-Present timeline.")

if __name__ == "__main__":
    run_backfill()