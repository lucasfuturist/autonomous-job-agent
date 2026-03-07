import os
import glob
from tools.server import convert_to_pdf

# Utility to batch regenerate PDFs from existing Markdown files.
# Also handles migration of filenames from legacy _JIT format to _Lucas_Mougeot.

def run_rebuild():
    md_folder = "data/output_mds"
    deploy_folder = "data/deployments"
    
    if not os.path.exists(deploy_folder):
        os.makedirs(deploy_folder)
        
    files = glob.glob(os.path.join(md_folder, "*.md"))
    print(f"[REBUILD] Found {len(files)} Markdown resumes to process.")
    
    success_count = 0
    renamed_count = 0
    
    for f in files:
        filename = os.path.basename(f)
        new_filename = filename
        
        # 1. Strip 'nan' prefix/substring (Pandas artifact)
        if 'nan' in new_filename:
            new_filename = new_filename.replace('nan_', '').replace('_nan', '')
            # If the file started with nan and now starts with _, strip it
            if new_filename.startswith('_'): new_filename = new_filename[1:]

        # 2. Migrate JIT -> Lucas_Mougeot
        if '_JIT.md' in new_filename:
            new_filename = new_filename.replace('_JIT.md', '_Lucas_Mougeot.md')
            
        # Execute Rename if needed
        source_path = f
        if new_filename != filename:
            new_source_path = os.path.join(md_folder, new_filename)
            os.rename(f, new_source_path)
            print(f"  -> Renamed: {filename} -> {new_filename}")
            source_path = new_source_path
            renamed_count += 1
            filename = new_filename # Update for PDF generation

        pdf_name = filename.replace('.md', '.pdf')
        output_path = os.path.join(deploy_folder, pdf_name)
        
        print(f"  -> Converting: {filename} ... ", end="")
        try:
            # Call the standalone function directly
            res = convert_to_pdf(source_path, output_path)
            if res:
                print("OK")
                success_count += 1
            else:
                print("FAIL")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\n[REBUILD] Complete. {success_count} PDFs rebuilt. {renamed_count} files renamed.")

if __name__ == "__main__":
    run_rebuild()