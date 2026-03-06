import os
import glob
from tools.server import convert_to_pdf

# Utility to batch regenerate PDFs from existing Markdown files.
# Useful when updating CSS/Styling logic without burning LLM tokens.

def run_rebuild():
    md_folder = "data/output_mds"
    deploy_folder = "data/deployments"
    
    if not os.path.exists(deploy_folder):
        os.makedirs(deploy_folder)
        
    files = glob.glob(os.path.join(md_folder, "*.md"))
    print(f"[REBUILD] Found {len(files)} Markdown resumes to process.")
    
    success_count = 0
    for f in files:
        filename = os.path.basename(f)
        pdf_name = filename.replace('.md', '.pdf')
        output_path = os.path.join(deploy_folder, pdf_name)
        
        print(f"  -> Converting: {filename} ... ", end="")
        try:
            # Call the standalone function directly
            res = convert_to_pdf(f, output_path)
            if res:
                print("OK")
                success_count += 1
            else:
                print("FAIL")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\n[REBUILD] Complete. {success_count}/{len(files)} PDFs regenerated with new styling.")

if __name__ == "__main__":
    run_rebuild()