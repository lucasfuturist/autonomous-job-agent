import os
import glob
from config import MD_FOLDER
from tools.server import convert_to_pdf

# Backfill script to detect if the "Stealth Platform" employment block
# is entirely missing from a generated resume, and forcibly inject it
# to prevent showing a 6-month employment gap.

STEALTH_INJECTION = """### Founding Systems Engineer at Stealth Platform (2024 – Present)
- Architected and implemented a production-grade AI-assisted compliance and decision platform using Python, TypeScript, and PostgreSQL, spanning structured intake, rule evaluation, and auditable decision workflows.
- Designed a deterministic ingestion engine in Python that compiles arbitrary repositories into immutable structural and dependency graphs via AST-based analysis and state machines orchestrated via LangGraph.
- Built LLM orchestration and observability tooling including prompt versioning, configuration management, structured input/output logging for latency and cost, and evaluation pipelines for controlled iteration.

"""

def run_backfill():
    files = glob.glob(os.path.join(MD_FOLDER, "*.md"))
    print(f"[BACKFILL] Scanning {len(files)} resumes for missing current employment...")
    
    count = 0
    for f in files:
        filename = os.path.basename(f)
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Check if Stealth Platform is present anywhere in the text
        if "Stealth Platform" not in content:
            print(f"  -> Anti-Gap Trigger: Injecting Stealth Platform into {filename} ... ", end="")
            
            # Find the Relevant Experience header and inject right beneath it
            if "## Relevant Experience\n" in content:
                # The trailing \n in the injection handles spacing to the next job
                new_content = content.replace(
                    "## Relevant Experience\n", 
                    f"## Relevant Experience\n{STEALTH_INJECTION}"
                )
                
                with open(f, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                    
                # Regenerate PDF silently
                pdf_path = f.replace('.md', '.pdf').replace('output_mds', 'deployments')
                convert_to_pdf(f, pdf_path)
                
                print("DONE")
                count += 1
            else:
                print("FAILED (No Experience Header found)")
                
    print(f"\n[BACKFILL] Complete. {count} resumes patched to remove employment gaps.")

if __name__ == "__main__":
    run_backfill()