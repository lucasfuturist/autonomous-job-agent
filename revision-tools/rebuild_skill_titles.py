import os
import glob
from config import MD_FOLDER
from tools.server import convert_to_pdf

# Fast string replacement script to fix ".title()" capitalization errors
# in the Core Skills section of existing Markdown resumes.

REPLACEMENTS = {
    "**Ai And Machine Learning:**": "**AI and Machine Learning:**",
    "**Backend Data And Infrastructure:**": "**Backend Data and Infrastructure:**",
    "**Robotics Edge And Autonomy:**": "**Robotics Edge and Autonomy:**",
    "**Hardware And Thermal Processing:**": "**Hardware and Thermal Processing:**",
    "**Electrochemistry And Lab Techniques:**": "**Electrochemistry and Lab Techniques:**"
}

def run_backfill():
    files = glob.glob(os.path.join(MD_FOLDER, "*.md"))
    print(f"[BACKFILL] Checking {len(files)} Markdown resumes for grammar fixes...")
    
    count = 0
    for f in files:
        filename = os.path.basename(f)
        
        with open(f, 'r', encoding='utf-8') as file:
            original_content = file.read()
            
        new_content = original_content
        
        # Apply all known grammar fixes
        for bad_str, good_str in REPLACEMENTS.items():
            new_content = new_content.replace(bad_str, good_str)
            
        # Only rewrite and re-PDF if an actual change was made
        if new_content != original_content:
            print(f"  -> Fixing Grammar: {filename} ... ", end="")
            
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
                
            # Regenerate PDF
            pdf_path = f.replace('.md', '.pdf').replace('output_mds', 'deployments')
            convert_to_pdf(f, pdf_path)
            
            print("DONE")
            count += 1

    print(f"\n[BACKFILL] Complete. {count} resumes updated with correct capitalization.")

if __name__ == "__main__":
    run_backfill()