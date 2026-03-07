import os
import glob
import re
import json
import ollama
from config import HEAVY_MODEL, MD_FOLDER
from tools.server import convert_to_pdf

# Backfill script to fix "Weird Tense" summaries on existing MD files
# without regenerating the entire resume or skills section.

def regenerate_summary(target_title, company, current_summary):
    # This prompt matches the updated Brain.py logic for "Narrative Prose"
    prompt = f"""
    Role: Ruthless, Strictly Factual Technical Resume Writer.
    Target Job Title: {target_title}
    Target Company: {company}
    
    Current Draft Summary (BAD TENSE): 
    "{current_summary}"

    TASK: Rewrite the summary above to fix the tense.
    
    RULES:
    1. NARRATIVE PROSE: Write in flowing, professional resume prose using implied first-person. 
    2. BAD: "Architect and implement real-time systems." (Floating Verb)
    3. GOOD: "Systems Engineer with a proven track record of architecting real-time systems..."
    4. FACT-BASED ALIGNMENT: Keep the facts the same. Just fix the sentence structure.
    5. NO HALLUCINATION: Do not invent new facts.

    Output ONLY valid JSON: {{ "summary": "..." }}
    """
    
    try:
        res = ollama.chat(model=HEAVY_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json')
        data = json.loads(res['message']['content'])
        return data.get('summary', current_summary)
    except Exception as e:
        print(f"  [ERROR] LLM Failed: {e}")
        return current_summary

def run_backfill():
    files = glob.glob(os.path.join(MD_FOLDER, "*.md"))
    print(f"[BACKFILL] Found {len(files)} Markdown resumes to process.")
    
    count = 0
    for f in files:
        filename = os.path.basename(f)
        
        # 1. Parse Frontmatter & Body
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Regex to extract frontmatter
        fm_match = re.search(r'---\ntarget_title: "(.*?)"\ncore_competency: "(.*?)"\n---', content, re.DOTALL)
        if not fm_match:
            print(f"  [SKIP] {filename} - No Frontmatter found")
            continue
            
        target_title = fm_match.group(1)
        # Try to guess company from filename since it's not in frontmatter
        # Filename format: Company_Title_Lucas_Mougeot.md
        company = filename.split('_')[0] 
        
        # Extract existing summary
        # Look for content between "## Professional Summary" and "## Relevant Experience"
        summary_match = re.search(r'## Professional Summary\n(.*?)\n\n## Relevant Experience', content, re.DOTALL)
        
        if summary_match:
            old_summary = summary_match.group(1).strip()
            
            # Check if it starts with a verb (Heuristic for "Bad Tense")
            first_word = old_summary.split(' ')[0]
            if first_word.endswith('s') or first_word in ["Architect", "Design", "Implement", "Develop", "Build"]:
                print(f"  -> Fixing: {filename} ({company}) ... ", end="")
                
                new_summary = regenerate_summary(target_title, company, old_summary)
                
                # Replace in content
                new_content = content.replace(old_summary, new_summary)
                
                with open(f, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                    
                # Regenerate PDF
                pdf_path = f.replace('.md', '.pdf').replace('output_mds', 'deployments')
                convert_to_pdf(f, pdf_path)
                
                print("DONE")
                count += 1
            else:
                # print(f"  [OK] {filename} seems fine.")
                pass
        else:
            print(f"  [SKIP] {filename} - Could not parse summary structure")

    print(f"\n[BACKFILL] Complete. {count} summaries updated to Narrative Prose.")

if __name__ == "__main__":
    run_backfill()