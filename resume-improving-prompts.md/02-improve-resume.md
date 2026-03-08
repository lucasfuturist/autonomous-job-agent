EXECUTION PROTOCOL: ARCHITECT & PRUNE

I am providing a target Job Description (JD) and a baseline "Current Resume" drafted by a smaller model. 

Based on my Master Career Data (which you have already ingested), generate two specific resume versions targeting this JD. 

EXECUTION & BULLET BUDGETS:
1. PROOF OF AUDIT: Before generating the resumes, provide a strict 1:1 mapping of the JD's most critical requirements to my Master Data to prove auditability. Use specific quotes from the JD.
2. DRAFT A (Comprehensive): 
   - Construct the strongest possible narrative targeting the JD. Include NSF and NASA roles to prove mathematical/physical rigor.
   - Constraint: Use EXACTLY 16 to 18 total bullets combined across "Experience" and "Projects".
   - Include exactly 2 projects from the Master Data. 
3. DRAFT B (Sniper): 
   - A strict 1-page version.
   - Constraint: Use EXACTLY 14 to 16 total bullets. 
   - Math Rule: Draft B MUST be identical to Draft A, minus exactly 2 specific, least-critical bullets.
   - Keep the NASA/NSF headers (reduce to 1 bullet if necessary, but do not delete the roles).

FORMATTING RULES:
- Output Draft A inside its own complete ```markdown ... ``` block. 
- Output Draft B inside its own complete ```markdown ... ``` block.
- BULLET INTEGRITY (CRITICAL): Do NOT concatenate project bullets into a single paragraph. Every single bullet point under "Relevant Experience" and "Selected Projects" MUST start on a new line with a hyphen `- `.
- NO CODE STYLING (CRITICAL): Do NOT use backticks ( ` ) or monospaced font styling for technical terms like ltree, pgvector, Pydantic, or function names. These must be rendered as standard professional text.
- INTENTIONAL BOLDING: There is no maximum limit, but bolding must be strategic. Ruthlessly bold key technical and domain-specific terms that intersect between the JD and the bullets to create a highly visible visual scan-path for recruiters. Ensure that the sequence tells a narrative that qualifies the candidate for an interview. Bold these directly within the sentences of the experience and projects. Bold relevant skills within the skills section. Sparsely bold the summary to ensure both superficial understanding and readability for the curious recruiter.
- SKILLS: Ensure that the skills titles are not in title case; for example "Ai And Machine Learning" should be "AI and Machine Learning". If deemed appropriate, take the liberty to update the skills titles to match the overall resume with respect to the job description.
- Use this exact Markdown structure for both drafts:

### PROOF OF AUDIT
1. **JD Requirement:** "[Exact quote from JD]"
   **Mapped Experience:** [Bullet ID or Project Name]
   **Rationale:** [1-sentence explanation of why this proves exact competency]
*(Repeat for 4-5 critical JD requirements)*

[BEGIN DRAFT A]
```markdown
---
target_title: "[Role Title Based on JD]"
core_competency: "[3-5 Word Competency]"
---

## Professional Summary[2-sentence high-impact technical thesis statement. Connect dots via transferable technology. No seniority inflation. Synthesize, do not use fluff words.]

## Relevant Experience

### [Job Title] at [Company] ([Dates])
- [Bullet text from Master Data] 
- [Bullet text from Master Data]

## Selected Projects

### [Project Name]
*[Project Context String from Master Data]*

- [Bullet text from Master Data]
- [Bullet text from Master Data]

## Core Skills
- **[Formatted Category Name]:**[Skill 1], [Skill 2]... (Convert JSON snake_case keys to Clean Title Case, e.g., 'programming_languages' -> 'Programming Languages'. Individual skills must remain exact strings from JSON).

## Education
- **[Degree]** | [Institution]<br>*[Details]*
- **[Degree]** |[Institution]<br>*[Details]*
```

[BEGIN DRAFT B]
```markdown
(Same structure as Draft A, strictly minus 2 bullets)
```