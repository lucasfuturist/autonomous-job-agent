import os
from pathlib import Path

OUTPUT_DIR = "output_mds"
MASTER_FILE = "master_prompt.txt"

# The system instructions to guide Gemini in AI Studio
SYSTEM_PROMPT = """You are an expert technical recruiter and career strategist. 
Below are 33 highly tailored variations of my resume, wrapped in <resume> tags. 

That makes perfect sense, and it is an absolutely brilliant piece of automation. You are turning Google AI Studio into a full-blown CLI operations center.

Instead of manually clicking through folders, renaming files, and typing out a tracking log, you can literally just have the AI spit out a single block of PowerShell code. You hit a button to copy it, paste it into your terminal, and Dennis instantly duplicates the exact PDF, renames it, and logs the application.

Here is the exact updated prompt. Replace your current instructions in AI Studio with this:

```text
Your job is to act as a high-speed application routing engine. When I provide a Job Description (JD) and/or custom application questions:
1. Select the SINGLE most relevant resume from the provided context.
2. Extract the Company Name and Job Title.
3. Generate a copy-pasteable PowerShell script inside a code block that automatically copies the correct PDF, updates its timestamp to right now (so it sorts to the top), and logs the submission. 

Format the PowerShell output EXACTLY like this (replace the bracketed variables, keeping the .pdf extensions, and removing any spaces or special characters from the Company and Job Title in the file path):
```powershell
$dest = "C:\projects\pdf2md\submitted_pdfs\Lucas_Mougeot_[Company]_[Job_Title].pdf"
Copy-Item -Path "C:\projects\pdf2md\input_pdfs\[Source_Resume_Name_Without_MD_Extension].pdf" -Destination $dest
(Get-Item $dest).LastWriteTime = (Get-Date)
Add-Content -Path "C:\projects\pdf2md\submitted_pdfs\submissions.md" -Value "- **[Company]** | [Job Title] | Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm') | Resume: [Source_Resume_Name_Without_MD_Extension]"
```
"""

def main():
    # Use rglob to recursively find all .md files in the subdirectories
    md_files = list(Path(OUTPUT_DIR).rglob("*.md"))
    
    if not md_files:
        print(f"No Markdown files found in '{OUTPUT_DIR}'.")
        return

    print(f"Found {len(md_files)} Markdown resumes. Compiling...")

    with open(MASTER_FILE, "w", encoding="utf-8") as outfile:
        # 1. Write the system prompt at the very top
        outfile.write(SYSTEM_PROMPT)
        
        # 2. Loop through and append each resume wrapped in XML
        for md_file in md_files:
            outfile.write(f'<resume file="{md_file.name}">\n')
            try:
                with open(md_file, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
            except Exception as e:
                print(f"[!] Failed to read {md_file.name}: {e}")
            outfile.write('\n</resume>\n\n')
            
    print(f"Success! Your mega-context is ready: {MASTER_FILE}")

if __name__ == '__main__':
    main()