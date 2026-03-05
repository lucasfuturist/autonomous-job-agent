import os
import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm

INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_mds"
FAILED_DIR = "failed_pdfs"

def main():
    pdf_files = list(Path(INPUT_DIR).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in '{INPUT_DIR}'. Please drop your resumes there.")
        return
    
    print(f"Found {len(pdf_files)} PDFs. Firing up the batch conversion...")
    
    # Run Marker's batch command using 8 workers
    cmd = ["marker", INPUT_DIR, OUTPUT_DIR, "--workers", "8"]
    
    try:
        # Hide the messy default console output so we can use our own progress tracking
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Warning: Marker batch process encountered an issue: {e}")
    
    print("\nVerifying outputs and formatting files...")
    
    failed_count = 0
    # Add a progress bar for the verification step
    for pdf_path in tqdm(pdf_files, desc="Processing Resumes", unit="file"):
        base_name = pdf_path.stem
        expected_md_file = Path(OUTPUT_DIR) / base_name / f"{base_name}.md"
        
        if not expected_md_file.exists():
            shutil.move(str(pdf_path), str(Path(FAILED_DIR) / pdf_path.name))
            failed_count += 1
            
    print(f"\nDone! Successfully processed {len(pdf_files) - failed_count} files.")
    if failed_count > 0:
        print(f"Moved {failed_count} corrupt or unreadable PDFs to '{FAILED_DIR}'.")

if __name__ == '__main__':
    main()