EXECUTION PROTOCOL: WORKDAY SKILLS EXTRACTION

The candidate is about to apply to this role via Workday. Workday utilizes a rigid "Skills" tagging system that recruiters use for backend filtering. 

Based on the Job Description and the candidate's Master Career Data, generate a comprehensive list of 30-40 individual skill tags. 

CRITICAL RULES FOR WORKDAY TAGS:
1. MAXIMIZE ATS CAPTURE: Include the exact terminology used in the JD, plus common industry variants (e.g., if the JD says "AI/ML", you must list "Artificial Intelligence", "Machine Learning", "AI", and "ML" as separate tags; these variations should not cut into the quantity of skill tags as they represent one skill; the purpose of this is to maximize ATS friendliness).
2. TRUTH GROUNDING: Only include skills, tools, and methodologies that the candidate actually possesses according to their Master Career Data. 
3. BROADEN THE SCOPE: Include the foundational tools implied by the JD that the candidate has (e.g., if the JD asks for "Data Pipelines", and the Master Data shows "PostgreSQL" and "Docker", include them).
4. NO DESCRIPTIONS: Output only the skill names.
5. RESUME PARITY: You MUST extract and include every single technical skill listed in the "Core Skills" section of the generated resume draft to ensure 100% backend ATS indexing.

OUTPUT FORMAT:
Output a list of these skills separated by line breaks (\n) so the candidate can easily copy and paste them into the Workday input field. 

Example: 
Python
Machine Learning
Artificial Intelligence
SQL
PostgreSQL
Data Pipelines