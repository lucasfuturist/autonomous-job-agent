# File Scan

**Roots:**

- `C:\projects\repo-runner`


## Tree: C:\projects\repo-runner

```
repo-runner/

├── .dev-prompts/
│   ├── .context-compressor-prompt.md
│   ├── commands.md
│   ├── compressed/
│   │   ├── 00-compressed-codebase-ingest-prompt.md
│   │   ├── 01-next-steps-prompt.md
│   │   ├── 02-requested-files.md
│   │   ├── 03-code-conventions-prompt.md
│   ├── raw/
│   │   ├── 00-raw-codebase-ingest-prompt.md
│   │   ├── 01-next-steps-prompt.md
│   │   ├── 02-code-conventions-prompt.md
│   ├── repo-runner-flattened.md
├── .gitignore
├── README.md
├── documents/
│   ├── ARCHITECTURE.md
│   ├── CONFIG_SPEC.md
│   ├── CONTRIBUTING.md
│   ├── DETERMINISM_RULES.md
│   ├── ID_SPEC.md
│   ├── LANGUAGE_SUPPORT.md
│   ├── REPO_LAYOUT.md
│   ├── ROADMAP.md
│   ├── SNAPSHOT_SPEC.md
│   ├── TESTING_STRATEGY.md
│   ├── VERSIONING_POLICY.md
├── fixtures/
├── scripts/
│   ├── export-signal.ps1
│   ├── package-repo.ps1
├── src/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   ├── exporters/
│   │   ├── flatten_markdown_exporter.py
│   ├── fingerprint/
│   │   ├── file_fingerprint.py
│   ├── normalize/
│   │   ├── path_normalizer.py
│   ├── scanner/
│   │   ├── filesystem_scanner.py
│   ├── snapshot/
│   │   ├── snapshot_loader.py
│   │   ├── snapshot_writer.py
│   ├── structure/
│   │   ├── structure_builder.py
├── tests/
│   ├── golden/
│   ├── integration/
│   ├── unit/

```

## Files

### `C:/projects/repo-runner/.dev-prompts/.context-compressor-prompt.md`

```md
### The "Context Compressor" Prompt

Use this prompt when you want to convert raw code into your "Tree + Explanations" format.

> **System / Prompt:**
>
> I am providing a file scan of a module in my monorepo. The input contains the full file tree and source code.
>
> **Your Goal:** Create a **"High-Resolution Interface Map"** of this module to save tokens for future context.
>
> **Output Format:**
> 1.  **The Tree:** Copy the directory tree exactly as provided.
> 2.  **File Summaries:** For every significant file (`.ts`, `.tsx`, `.prisma`), provide a summary using this exact schema:
>
> ```markdown
> ### `[File Name]`
> **Role:** [1 sentence on what this file is responsible for]
> **Key Exports:**
> - `functionName(params): ReturnType` - [1 sentence on purpose. Do NOT explain implementation steps.]
> - `VariableName` - [Explain what state/config this holds]
> **Dependencies:** [List critical internal services/repos it imports]
> ```
>
> **Compression Rules (Strict):**
> 1.  **Ignore Implementation:** I do not want to see `if`, `for`, or logic steps. I only want inputs, outputs, and intent.
> 2.  **Ignore Operational Vars:** Do not list loop counters (`i`), temp variables, or local booleans. Only list **State** (React `useState`, stores), **Config** (constants), or **Database Models**.
> 3.  **Focus on Architecture:** If a file connects `API` to `Repo`, explicitly state that relationship.

NOTE: include all test files in your output architectural report
```

### `C:/projects/repo-runner/.dev-prompts/commands.md`

```md
python "C:\dev-utils\list_tree.py"  "C:\projects\repo-runner" --ignore dist __pycache__ .next node_modules .git .vercel .context package-lock.json --list-scripts .py .md .json .ts .tsx .js .mjs .css .txt --include-readme --output "C:\projects\repo-runner\.dev-prompts\repo-runner-flattened.md"


```

### `C:/projects/repo-runner/.dev-prompts/compressed/00-compressed-codebase-ingest-prompt.md`

```md
# Compressed Context Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a codebase that has been flattened into a series of **Context Markdown Files** (e.g., `MODULE-CORE-context.md`, `SRC-API-context.md`, `TREE-ROOT-context.md`).

**Ingest ALL provided Markdown artifacts in full.** These files contain directory trees, file summaries, and raw code blocks. Treat the **content within these blocks** as the absolute source of truth.

Your immediate tasks are:

### 1. Reconstruct & Analyze Ground Truth
*   **Virtualize the Structure:**
    *   Use the `## Tree` sections in the Markdown files to map the full project topology.
    *   Use the `## Files` or `## Summaries` sections to map specific logic to specific paths.
*   **Analyze System Boundaries:**
    *   Identify the high-level architecture based on configuration files present (e.g., `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `pom.xml`, or `Makefile`).
    *   Map the primary boundaries:
        *   **Entry Points:** (e.g., HTTP Servers, CLI roots, GUI Mains).
        *   **Modules/Packages:** (e.g., Shared libraries, Domain logic, Utilities).
        *   **Infrastructure:** (e.g., Database migrations, Docker configs, IaC).
*   **Trace Data Flow:**
    *   Map how data moves through the stack: **Input/Interface** (API Controllers/UI) → **Business Logic** (Services/Use Cases) → **Persistence** (Repositories/ORM/SQL).

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any `progress/*.md` or `TODO` lists found in the context.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists in a file block, dependencies resolve, and logic appears complete.
    *   **Partial/Stubbed:** Functions/Classes exist but return mocks, `NotImplemented` errors, or pass-throughs.
    *   **Missing:** Feature is mentioned in documentation/comments but no corresponding file block exists.
    *   **Divergent:** Implementation contradicts the documentation or apparent architectural intent.
*   *Output a corrected Status Log based on the actual code present.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly? (e.g., Is Domain logic leaking into the View/Controller layer? Are circular dependencies avoided?)
    *   **Security:** Are authorization/authentication checks present at critical boundaries? Is input validation visible?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, unoptimized loops, heavy payloads without DTOs)?
    *   **Type/Memory Safety:** Are types/interfaces consistent across module boundaries? Is error handling robust (e.g., `try/catch`, `Result` types, panic recovery)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across module boundaries.

### 4. System Synthesis
*   Provide a high-level technical summary:
    *   **Core Domain:** What does this specific codebase do? (e.g., "Financial Ledger", "Embedded Control System", "E-commerce Backend").
    *   **Current Capabilities:** What user flows are fully coded? (e.g., "User can login", "Data processing pipeline is active").
    *   **Architecture Quality:** Is the project structure actually being used effectively, or is it just folder organization without modular enforcement?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** files not present in the Markdown context. If a file is referenced in an import but its code block is missing from the context files, mark it as "External/Missing Context."
*   **Citation:** When making a claim, reference the **File Path** provided in the Markdown header (e.g., `src/modules/auth/service.go` or `lib/core/processor.py`).
```

### `C:/projects/repo-runner/.dev-prompts/compressed/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/.dev-prompts/compressed/02-requested-files.md`

```md
### The "Context Manifest Request" Prompt

> **System / Prompt:**
>
> I have decided to proceed with **Option [X]: [Insert Track Name]**.
>
> To execute this plan, you need to transition from high-level architecture to low-level implementation.
>
> **Your Task:**
> Analyze the file tree and summaries you currently have. Identify the **critical path files** required to build this feature.
>
> **Output a "Context Manifest" list:**
> Please list the exact file paths I need to copy-paste into this chat so you have the **Ground Truth** (raw source code) necessary to write the implementation.
>
> *   **Group 1: Logic & State** (Files that need functional changes)
> *   **Group 2: UI & Views** (Files that need visual/markup changes)
> *   **Group 3: Data & Config** (Files defining types, schemas, or constants)
>
> *Only request files that are strictly necessary for this specific task.*
```

### `C:/projects/repo-runner/.dev-prompts/compressed/03-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.
```

### `C:/projects/repo-runner/.dev-prompts/raw/00-raw-codebase-ingest-prompt.md`

```md
# Universal Codebase Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a flattened representation of a software repository (code files, configuration, and documentation).

**Ingest ALL provided materials in full.** Treat the **actual code** as the absolute source of truth; documentation, comments, and file names are secondary and may be outdated.

Your immediate tasks are:

### 1. Establish Architectural Ground Truth
*   **Analyze the System Boundaries:**
    *   Identify the high-level architecture (Monorepo, Monolith, Microservices, etc.).
    *   Map the primary boundaries: Frontend vs. Backend, Core Logic vs. Infrastructure, Public API vs. Internal Implementation.
    *   Identify the key frameworks, languages, and runtime environments in use.
*   **Trace the Data Flow:**
    *   Map how data moves through the system (e.g., Client → API/Action → Controller/Service → Database/Store).
    *   Identify how modules communicate (HTTP, RPC, Imports, Events).
*   **Verify Data Models:**
    *   Compare the **Persistence Layer** (SQL schemas, ORM definitions, Store interfaces) against the **Application Layer** (Types, DTOs, Classes).
    *   Identify if data shapes are consistent or if ad-hoc transformations are occurring.

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any provided **Progress Logs, Roadmaps, or TODOs**.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists, is wired up, and appears functional.
    *   **Partial/Stubbed:** Function signatures or UI shells exist, but logic is mocked or incomplete.
    *   **Missing:** Feature is mentioned in docs but no code exists.
    *   **Divergent:** Implementation contradicts the documentation or intent.
*   *Output a corrected Progress Log based on reality.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly (e.g., View logic mixed with DB calls)?
    *   **Security:** Are authorization checks centralized or scattered? Are secrets handled via environment variables?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, large payload selections, blocking operations)?
    *   **Type Safety (if applicable):** Is the type system being used strictly, or bypassed (e.g., `any`, `interface{}`)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across boundaries, or where technical debt is accumulating.

### 4. System Synthesis
*   Provide a high-level technical summary of the system:
    *   **Core Domain:** What is the primary problem this software solves?
    *   **Key Capabilities:** What can the system actually *do* right now?
    *   **Infrastructure:** How is the system configured to run (Docker, Serverless, Node, Go, etc.)?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** features or patterns not present in the file dumps.
*   **Focus on Structural Integrity:** Prioritize architectural health over minor syntax details.
*   **Citation:** When making a claim about the architecture, reference the specific directory or file pattern that proves it.
```

### `C:/projects/repo-runner/.dev-prompts/raw/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/.dev-prompts/raw/02-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code.
```

### `C:/projects/repo-runner/.dev-prompts/repo-runner-flattened.md`

```md
# File Scan

**Roots:**

- `C:\projects\repo-runner`


## Tree: C:\projects\repo-runner

```
repo-runner/

├── .dev-prompts/
│   ├── .context-compressor-prompt.md
│   ├── commands.md
│   ├── compressed/
│   │   ├── 00-compressed-codebase-ingest-prompt.md
│   │   ├── 01-next-steps-prompt.md
│   │   ├── 02-requested-files.md
│   │   ├── 03-code-conventions-prompt.md
│   ├── raw/
│   │   ├── 00-raw-codebase-ingest-prompt.md
│   │   ├── 01-next-steps-prompt.md
│   │   ├── 02-code-conventions-prompt.md
├── .gitignore
├── README.md
├── dist/
│   ├── repo-copy/
│   │   ├── .dev-prompts/
│   │   │   ├── .context-compressor-prompt.md
│   │   │   ├── commands.md
│   │   │   ├── compressed/
│   │   │   │   ├── 00-compressed-codebase-ingest-prompt.md
│   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   ├── 02-requested-files.md
│   │   │   │   ├── 03-code-conventions-prompt.md
│   │   │   ├── raw/
│   │   │   │   ├── 00-raw-codebase-ingest-prompt.md
│   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   ├── 02-code-conventions-prompt.md
│   │   ├── .gitignore
│   │   ├── README.md
│   │   ├── dist/
│   │   │   ├── repo-copy/
│   │   │   │   ├── .dev-prompts/
│   │   │   │   │   ├── .context-compressor-prompt.md
│   │   │   │   │   ├── commands.md
│   │   │   │   │   ├── compressed/
│   │   │   │   │   │   ├── 00-compressed-codebase-ingest-prompt.md
│   │   │   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   │   │   ├── 02-requested-files.md
│   │   │   │   │   │   ├── 03-code-conventions-prompt.md
│   │   │   │   │   ├── raw/
│   │   │   │   │   │   ├── 00-raw-codebase-ingest-prompt.md
│   │   │   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   │   │   ├── 02-code-conventions-prompt.md
│   │   │   │   ├── .gitignore
│   │   │   │   ├── README.md
│   │   │   │   ├── dist/
│   │   │   │   │   ├── repo-copy/
│   │   │   │   │   │   ├── .dev-prompts/
│   │   │   │   │   │   │   ├── .context-compressor-prompt.md
│   │   │   │   │   │   │   ├── commands.md
│   │   │   │   │   │   │   ├── compressed/
│   │   │   │   │   │   │   │   ├── 00-compressed-codebase-ingest-prompt.md
│   │   │   │   │   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   │   │   │   │   ├── 02-requested-files.md
│   │   │   │   │   │   │   │   ├── 03-code-conventions-prompt.md
│   │   │   │   │   │   │   ├── raw/
│   │   │   │   │   │   │   │   ├── 00-raw-codebase-ingest-prompt.md
│   │   │   │   │   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   │   │   │   │   ├── 02-code-conventions-prompt.md
│   │   │   │   │   │   ├── .gitignore
│   │   │   │   │   │   ├── README.md
│   │   │   │   │   │   ├── dist/
│   │   │   │   │   │   │   ├── repo-copy/
│   │   │   │   │   │   │   │   ├── .dev-prompts/
│   │   │   │   │   │   │   │   │   ├── .context-compressor-prompt.md
│   │   │   │   │   │   │   │   │   ├── commands.md
│   │   │   │   │   │   │   │   │   ├── compressed/
│   │   │   │   │   │   │   │   │   │   ├── 00-compressed-codebase-ingest-prompt.md
│   │   │   │   │   │   │   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   │   │   │   │   │   │   ├── 02-requested-files.md
│   │   │   │   │   │   │   │   │   │   ├── 03-code-conventions-prompt.md
│   │   │   │   │   │   │   │   │   ├── raw/
│   │   │   │   │   │   │   │   │   │   ├── 00-raw-codebase-ingest-prompt.md
│   │   │   │   │   │   │   │   │   │   ├── 01-next-steps-prompt.md
│   │   │   │   │   │   │   │   │   │   ├── 02-code-conventions-prompt.md
│   │   │   │   │   │   │   │   ├── .gitignore
│   │   │   │   │   │   │   │   ├── README.md
│   │   │   │   │   │   │   │   ├── dist/
│   │   │   │   │   │   │   │   │   ├── repo-copy/
│   │   │   │   │   │   │   │   │   │   ├── .dev-prompts/
│   │   │   │   │   │   │   │   │   │   ├── .gitignore
│   │   │   │   │   │   │   │   │   │   ├── README.md
│   │   │   │   │   │   │   │   │   │   ├── dist/
│   │   ├── documents/
│   │   │   ├── ARCHITECTURE.md
│   │   │   ├── CONFIG_SPEC.md
│   │   │   ├── CONTRIBUTING.md
│   │   │   ├── DETERMINISM_RULES.md
│   │   │   ├── ID_SPEC.md
│   │   │   ├── LANGUAGE_SUPPORT.md
│   │   │   ├── REPO_LAYOUT.md
│   │   │   ├── ROADMAP.md
│   │   │   ├── SNAPSHOT_SPEC.md
│   │   │   ├── TESTING_STRATEGY.md
│   │   │   ├── VERSIONING_POLICY.md
│   │   ├── fixtures/
│   │   ├── scripts/
│   │   │   ├── package-repo.ps1
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── cli/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   ├── exporters/
│   │   │   │   ├── flatten_markdown_exporter.py
│   │   │   ├── fingerprint/
│   │   │   │   ├── file_fingerprint.py
│   │   │   ├── normalize/
│   │   │   │   ├── path_normalizer.py
│   │   │   ├── scanner/
│   │   │   │   ├── filesystem_scanner.py
│   │   │   ├── snapshot/
│   │   │   │   ├── snapshot_loader.py
│   │   │   │   ├── snapshot_writer.py
│   │   │   ├── structure/
│   │   │   │   ├── structure_builder.py
│   │   ├── tests/
│   │   │   ├── golden/
│   │   │   ├── integration/
│   │   │   ├── unit/
│   ├── robocopy.log
│   ├── signal/
├── documents/
│   ├── ARCHITECTURE.md
│   ├── CONFIG_SPEC.md
│   ├── CONTRIBUTING.md
│   ├── DETERMINISM_RULES.md
│   ├── ID_SPEC.md
│   ├── LANGUAGE_SUPPORT.md
│   ├── REPO_LAYOUT.md
│   ├── ROADMAP.md
│   ├── SNAPSHOT_SPEC.md
│   ├── TESTING_STRATEGY.md
│   ├── VERSIONING_POLICY.md
├── fixtures/
├── scripts/
│   ├── export-signal.ps1
│   ├── package-repo.ps1
├── src/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   ├── exporters/
│   │   ├── flatten_markdown_exporter.py
│   ├── fingerprint/
│   │   ├── file_fingerprint.py
│   ├── normalize/
│   │   ├── path_normalizer.py
│   ├── scanner/
│   │   ├── filesystem_scanner.py
│   ├── snapshot/
│   │   ├── snapshot_loader.py
│   │   ├── snapshot_writer.py
│   ├── structure/
│   │   ├── structure_builder.py
├── tests/
│   ├── golden/
│   ├── integration/
│   ├── unit/

```

## Files

### `C:/projects/repo-runner/.dev-prompts/.context-compressor-prompt.md`

```md
### The "Context Compressor" Prompt

Use this prompt when you want to convert raw code into your "Tree + Explanations" format.

> **System / Prompt:**
>
> I am providing a file scan of a module in my monorepo. The input contains the full file tree and source code.
>
> **Your Goal:** Create a **"High-Resolution Interface Map"** of this module to save tokens for future context.
>
> **Output Format:**
> 1.  **The Tree:** Copy the directory tree exactly as provided.
> 2.  **File Summaries:** For every significant file (`.ts`, `.tsx`, `.prisma`), provide a summary using this exact schema:
>
> ```markdown
> ### `[File Name]`
> **Role:** [1 sentence on what this file is responsible for]
> **Key Exports:**
> - `functionName(params): ReturnType` - [1 sentence on purpose. Do NOT explain implementation steps.]
> - `VariableName` - [Explain what state/config this holds]
> **Dependencies:** [List critical internal services/repos it imports]
> ```
>
> **Compression Rules (Strict):**
> 1.  **Ignore Implementation:** I do not want to see `if`, `for`, or logic steps. I only want inputs, outputs, and intent.
> 2.  **Ignore Operational Vars:** Do not list loop counters (`i`), temp variables, or local booleans. Only list **State** (React `useState`, stores), **Config** (constants), or **Database Models**.
> 3.  **Focus on Architecture:** If a file connects `API` to `Repo`, explicitly state that relationship.

NOTE: include all test files in your output architectural report
```

### `C:/projects/repo-runner/.dev-prompts/commands.md`

```md
python "C:\dev-utils\list_tree.py"  "C:\projects\repo-runner" --ignore __pycache__ .next node_modules .git .vercel .context package-lock.json --list-scripts .py .md .json .ts .tsx .js .mjs .css .txt --include-readme --output "C:\projects\repo-runner\.dev-prompts\repo-runner-flattened.md"


```

### `C:/projects/repo-runner/.dev-prompts/compressed/00-compressed-codebase-ingest-prompt.md`

```md
# Compressed Context Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a codebase that has been flattened into a series of **Context Markdown Files** (e.g., `MODULE-CORE-context.md`, `SRC-API-context.md`, `TREE-ROOT-context.md`).

**Ingest ALL provided Markdown artifacts in full.** These files contain directory trees, file summaries, and raw code blocks. Treat the **content within these blocks** as the absolute source of truth.

Your immediate tasks are:

### 1. Reconstruct & Analyze Ground Truth
*   **Virtualize the Structure:**
    *   Use the `## Tree` sections in the Markdown files to map the full project topology.
    *   Use the `## Files` or `## Summaries` sections to map specific logic to specific paths.
*   **Analyze System Boundaries:**
    *   Identify the high-level architecture based on configuration files present (e.g., `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `pom.xml`, or `Makefile`).
    *   Map the primary boundaries:
        *   **Entry Points:** (e.g., HTTP Servers, CLI roots, GUI Mains).
        *   **Modules/Packages:** (e.g., Shared libraries, Domain logic, Utilities).
        *   **Infrastructure:** (e.g., Database migrations, Docker configs, IaC).
*   **Trace Data Flow:**
    *   Map how data moves through the stack: **Input/Interface** (API Controllers/UI) → **Business Logic** (Services/Use Cases) → **Persistence** (Repositories/ORM/SQL).

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any `progress/*.md` or `TODO` lists found in the context.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists in a file block, dependencies resolve, and logic appears complete.
    *   **Partial/Stubbed:** Functions/Classes exist but return mocks, `NotImplemented` errors, or pass-throughs.
    *   **Missing:** Feature is mentioned in documentation/comments but no corresponding file block exists.
    *   **Divergent:** Implementation contradicts the documentation or apparent architectural intent.
*   *Output a corrected Status Log based on the actual code present.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly? (e.g., Is Domain logic leaking into the View/Controller layer? Are circular dependencies avoided?)
    *   **Security:** Are authorization/authentication checks present at critical boundaries? Is input validation visible?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, unoptimized loops, heavy payloads without DTOs)?
    *   **Type/Memory Safety:** Are types/interfaces consistent across module boundaries? Is error handling robust (e.g., `try/catch`, `Result` types, panic recovery)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across module boundaries.

### 4. System Synthesis
*   Provide a high-level technical summary:
    *   **Core Domain:** What does this specific codebase do? (e.g., "Financial Ledger", "Embedded Control System", "E-commerce Backend").
    *   **Current Capabilities:** What user flows are fully coded? (e.g., "User can login", "Data processing pipeline is active").
    *   **Architecture Quality:** Is the project structure actually being used effectively, or is it just folder organization without modular enforcement?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** files not present in the Markdown context. If a file is referenced in an import but its code block is missing from the context files, mark it as "External/Missing Context."
*   **Citation:** When making a claim, reference the **File Path** provided in the Markdown header (e.g., `src/modules/auth/service.go` or `lib/core/processor.py`).
```

### `C:/projects/repo-runner/.dev-prompts/compressed/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/.dev-prompts/compressed/02-requested-files.md`

```md
### The "Context Manifest Request" Prompt

> **System / Prompt:**
>
> I have decided to proceed with **Option [X]: [Insert Track Name]**.
>
> To execute this plan, you need to transition from high-level architecture to low-level implementation.
>
> **Your Task:**
> Analyze the file tree and summaries you currently have. Identify the **critical path files** required to build this feature.
>
> **Output a "Context Manifest" list:**
> Please list the exact file paths I need to copy-paste into this chat so you have the **Ground Truth** (raw source code) necessary to write the implementation.
>
> *   **Group 1: Logic & State** (Files that need functional changes)
> *   **Group 2: UI & Views** (Files that need visual/markup changes)
> *   **Group 3: Data & Config** (Files defining types, schemas, or constants)
>
> *Only request files that are strictly necessary for this specific task.*
```

### `C:/projects/repo-runner/.dev-prompts/compressed/03-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.
```

### `C:/projects/repo-runner/.dev-prompts/raw/00-raw-codebase-ingest-prompt.md`

```md
# Universal Codebase Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a flattened representation of a software repository (code files, configuration, and documentation).

**Ingest ALL provided materials in full.** Treat the **actual code** as the absolute source of truth; documentation, comments, and file names are secondary and may be outdated.

Your immediate tasks are:

### 1. Establish Architectural Ground Truth
*   **Analyze the System Boundaries:**
    *   Identify the high-level architecture (Monorepo, Monolith, Microservices, etc.).
    *   Map the primary boundaries: Frontend vs. Backend, Core Logic vs. Infrastructure, Public API vs. Internal Implementation.
    *   Identify the key frameworks, languages, and runtime environments in use.
*   **Trace the Data Flow:**
    *   Map how data moves through the system (e.g., Client → API/Action → Controller/Service → Database/Store).
    *   Identify how modules communicate (HTTP, RPC, Imports, Events).
*   **Verify Data Models:**
    *   Compare the **Persistence Layer** (SQL schemas, ORM definitions, Store interfaces) against the **Application Layer** (Types, DTOs, Classes).
    *   Identify if data shapes are consistent or if ad-hoc transformations are occurring.

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any provided **Progress Logs, Roadmaps, or TODOs**.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists, is wired up, and appears functional.
    *   **Partial/Stubbed:** Function signatures or UI shells exist, but logic is mocked or incomplete.
    *   **Missing:** Feature is mentioned in docs but no code exists.
    *   **Divergent:** Implementation contradicts the documentation or intent.
*   *Output a corrected Progress Log based on reality.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly (e.g., View logic mixed with DB calls)?
    *   **Security:** Are authorization checks centralized or scattered? Are secrets handled via environment variables?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, large payload selections, blocking operations)?
    *   **Type Safety (if applicable):** Is the type system being used strictly, or bypassed (e.g., `any`, `interface{}`)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across boundaries, or where technical debt is accumulating.

### 4. System Synthesis
*   Provide a high-level technical summary of the system:
    *   **Core Domain:** What is the primary problem this software solves?
    *   **Key Capabilities:** What can the system actually *do* right now?
    *   **Infrastructure:** How is the system configured to run (Docker, Serverless, Node, Go, etc.)?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** features or patterns not present in the file dumps.
*   **Focus on Structural Integrity:** Prioritize architectural health over minor syntax details.
*   **Citation:** When making a claim about the architecture, reference the specific directory or file pattern that proves it.
```

### `C:/projects/repo-runner/.dev-prompts/raw/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/.dev-prompts/raw/02-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code.
```

### `C:/projects/repo-runner/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/.context-compressor-prompt.md`

```md
### The "Context Compressor" Prompt

Use this prompt when you want to convert raw code into your "Tree + Explanations" format.

> **System / Prompt:**
>
> I am providing a file scan of a module in my monorepo. The input contains the full file tree and source code.
>
> **Your Goal:** Create a **"High-Resolution Interface Map"** of this module to save tokens for future context.
>
> **Output Format:**
> 1.  **The Tree:** Copy the directory tree exactly as provided.
> 2.  **File Summaries:** For every significant file (`.ts`, `.tsx`, `.prisma`), provide a summary using this exact schema:
>
> ```markdown
> ### `[File Name]`
> **Role:** [1 sentence on what this file is responsible for]
> **Key Exports:**
> - `functionName(params): ReturnType` - [1 sentence on purpose. Do NOT explain implementation steps.]
> - `VariableName` - [Explain what state/config this holds]
> **Dependencies:** [List critical internal services/repos it imports]
> ```
>
> **Compression Rules (Strict):**
> 1.  **Ignore Implementation:** I do not want to see `if`, `for`, or logic steps. I only want inputs, outputs, and intent.
> 2.  **Ignore Operational Vars:** Do not list loop counters (`i`), temp variables, or local booleans. Only list **State** (React `useState`, stores), **Config** (constants), or **Database Models**.
> 3.  **Focus on Architecture:** If a file connects `API` to `Repo`, explicitly state that relationship.

NOTE: include all test files in your output architectural report
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/commands.md`

```md
python "C:\projects\repo-runner" --ignore __pycache__ .next node_modules .git .vercel .context package-lock.json --list-scripts .py .md .json .ts .tsx .js .mjs .css .txt --include-readme --output "C:\projects\repo-runner\.dev-prompts\repo-runner-flattened.md"


```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/compressed/00-compressed-codebase-ingest-prompt.md`

```md
# Compressed Context Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a codebase that has been flattened into a series of **Context Markdown Files** (e.g., `MODULE-CORE-context.md`, `SRC-API-context.md`, `TREE-ROOT-context.md`).

**Ingest ALL provided Markdown artifacts in full.** These files contain directory trees, file summaries, and raw code blocks. Treat the **content within these blocks** as the absolute source of truth.

Your immediate tasks are:

### 1. Reconstruct & Analyze Ground Truth
*   **Virtualize the Structure:**
    *   Use the `## Tree` sections in the Markdown files to map the full project topology.
    *   Use the `## Files` or `## Summaries` sections to map specific logic to specific paths.
*   **Analyze System Boundaries:**
    *   Identify the high-level architecture based on configuration files present (e.g., `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `pom.xml`, or `Makefile`).
    *   Map the primary boundaries:
        *   **Entry Points:** (e.g., HTTP Servers, CLI roots, GUI Mains).
        *   **Modules/Packages:** (e.g., Shared libraries, Domain logic, Utilities).
        *   **Infrastructure:** (e.g., Database migrations, Docker configs, IaC).
*   **Trace Data Flow:**
    *   Map how data moves through the stack: **Input/Interface** (API Controllers/UI) → **Business Logic** (Services/Use Cases) → **Persistence** (Repositories/ORM/SQL).

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any `progress/*.md` or `TODO` lists found in the context.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists in a file block, dependencies resolve, and logic appears complete.
    *   **Partial/Stubbed:** Functions/Classes exist but return mocks, `NotImplemented` errors, or pass-throughs.
    *   **Missing:** Feature is mentioned in documentation/comments but no corresponding file block exists.
    *   **Divergent:** Implementation contradicts the documentation or apparent architectural intent.
*   *Output a corrected Status Log based on the actual code present.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly? (e.g., Is Domain logic leaking into the View/Controller layer? Are circular dependencies avoided?)
    *   **Security:** Are authorization/authentication checks present at critical boundaries? Is input validation visible?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, unoptimized loops, heavy payloads without DTOs)?
    *   **Type/Memory Safety:** Are types/interfaces consistent across module boundaries? Is error handling robust (e.g., `try/catch`, `Result` types, panic recovery)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across module boundaries.

### 4. System Synthesis
*   Provide a high-level technical summary:
    *   **Core Domain:** What does this specific codebase do? (e.g., "Financial Ledger", "Embedded Control System", "E-commerce Backend").
    *   **Current Capabilities:** What user flows are fully coded? (e.g., "User can login", "Data processing pipeline is active").
    *   **Architecture Quality:** Is the project structure actually being used effectively, or is it just folder organization without modular enforcement?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** files not present in the Markdown context. If a file is referenced in an import but its code block is missing from the context files, mark it as "External/Missing Context."
*   **Citation:** When making a claim, reference the **File Path** provided in the Markdown header (e.g., `src/modules/auth/service.go` or `lib/core/processor.py`).
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/compressed/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/compressed/02-requested-files.md`

```md
### The "Context Manifest Request" Prompt

> **System / Prompt:**
>
> I have decided to proceed with **Option [X]: [Insert Track Name]**.
>
> To execute this plan, you need to transition from high-level architecture to low-level implementation.
>
> **Your Task:**
> Analyze the file tree and summaries you currently have. Identify the **critical path files** required to build this feature.
>
> **Output a "Context Manifest" list:**
> Please list the exact file paths I need to copy-paste into this chat so you have the **Ground Truth** (raw source code) necessary to write the implementation.
>
> *   **Group 1: Logic & State** (Files that need functional changes)
> *   **Group 2: UI & Views** (Files that need visual/markup changes)
> *   **Group 3: Data & Config** (Files defining types, schemas, or constants)
>
> *Only request files that are strictly necessary for this specific task.*
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/compressed/03-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/raw/00-raw-codebase-ingest-prompt.md`

```md
# Universal Codebase Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a flattened representation of a software repository (code files, configuration, and documentation).

**Ingest ALL provided materials in full.** Treat the **actual code** as the absolute source of truth; documentation, comments, and file names are secondary and may be outdated.

Your immediate tasks are:

### 1. Establish Architectural Ground Truth
*   **Analyze the System Boundaries:**
    *   Identify the high-level architecture (Monorepo, Monolith, Microservices, etc.).
    *   Map the primary boundaries: Frontend vs. Backend, Core Logic vs. Infrastructure, Public API vs. Internal Implementation.
    *   Identify the key frameworks, languages, and runtime environments in use.
*   **Trace the Data Flow:**
    *   Map how data moves through the system (e.g., Client → API/Action → Controller/Service → Database/Store).
    *   Identify how modules communicate (HTTP, RPC, Imports, Events).
*   **Verify Data Models:**
    *   Compare the **Persistence Layer** (SQL schemas, ORM definitions, Store interfaces) against the **Application Layer** (Types, DTOs, Classes).
    *   Identify if data shapes are consistent or if ad-hoc transformations are occurring.

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any provided **Progress Logs, Roadmaps, or TODOs**.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists, is wired up, and appears functional.
    *   **Partial/Stubbed:** Function signatures or UI shells exist, but logic is mocked or incomplete.
    *   **Missing:** Feature is mentioned in docs but no code exists.
    *   **Divergent:** Implementation contradicts the documentation or intent.
*   *Output a corrected Progress Log based on reality.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly (e.g., View logic mixed with DB calls)?
    *   **Security:** Are authorization checks centralized or scattered? Are secrets handled via environment variables?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, large payload selections, blocking operations)?
    *   **Type Safety (if applicable):** Is the type system being used strictly, or bypassed (e.g., `any`, `interface{}`)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across boundaries, or where technical debt is accumulating.

### 4. System Synthesis
*   Provide a high-level technical summary of the system:
    *   **Core Domain:** What is the primary problem this software solves?
    *   **Key Capabilities:** What can the system actually *do* right now?
    *   **Infrastructure:** How is the system configured to run (Docker, Serverless, Node, Go, etc.)?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** features or patterns not present in the file dumps.
*   **Focus on Structural Integrity:** Prioritize architectural health over minor syntax details.
*   **Citation:** When making a claim about the architecture, reference the specific directory or file pattern that proves it.
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/raw/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/.dev-prompts/raw/02-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code.
```

### `C:/projects/repo-runner/dist/repo-copy/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/.context-compressor-prompt.md`

```md
### The "Context Compressor" Prompt

Use this prompt when you want to convert raw code into your "Tree + Explanations" format.

> **System / Prompt:**
>
> I am providing a file scan of a module in my monorepo. The input contains the full file tree and source code.
>
> **Your Goal:** Create a **"High-Resolution Interface Map"** of this module to save tokens for future context.
>
> **Output Format:**
> 1.  **The Tree:** Copy the directory tree exactly as provided.
> 2.  **File Summaries:** For every significant file (`.ts`, `.tsx`, `.prisma`), provide a summary using this exact schema:
>
> ```markdown
> ### `[File Name]`
> **Role:** [1 sentence on what this file is responsible for]
> **Key Exports:**
> - `functionName(params): ReturnType` - [1 sentence on purpose. Do NOT explain implementation steps.]
> - `VariableName` - [Explain what state/config this holds]
> **Dependencies:** [List critical internal services/repos it imports]
> ```
>
> **Compression Rules (Strict):**
> 1.  **Ignore Implementation:** I do not want to see `if`, `for`, or logic steps. I only want inputs, outputs, and intent.
> 2.  **Ignore Operational Vars:** Do not list loop counters (`i`), temp variables, or local booleans. Only list **State** (React `useState`, stores), **Config** (constants), or **Database Models**.
> 3.  **Focus on Architecture:** If a file connects `API` to `Repo`, explicitly state that relationship.

NOTE: include all test files in your output architectural report
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/commands.md`

```md
python "C:\projects\repo-runner" --ignore __pycache__ .next node_modules .git .vercel .context package-lock.json --list-scripts .py .md .json .ts .tsx .js .mjs .css .txt --include-readme --output "C:\projects\repo-runner\.dev-prompts\repo-runner-flattened.md"


```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/00-compressed-codebase-ingest-prompt.md`

```md
# Compressed Context Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a codebase that has been flattened into a series of **Context Markdown Files** (e.g., `MODULE-CORE-context.md`, `SRC-API-context.md`, `TREE-ROOT-context.md`).

**Ingest ALL provided Markdown artifacts in full.** These files contain directory trees, file summaries, and raw code blocks. Treat the **content within these blocks** as the absolute source of truth.

Your immediate tasks are:

### 1. Reconstruct & Analyze Ground Truth
*   **Virtualize the Structure:**
    *   Use the `## Tree` sections in the Markdown files to map the full project topology.
    *   Use the `## Files` or `## Summaries` sections to map specific logic to specific paths.
*   **Analyze System Boundaries:**
    *   Identify the high-level architecture based on configuration files present (e.g., `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `pom.xml`, or `Makefile`).
    *   Map the primary boundaries:
        *   **Entry Points:** (e.g., HTTP Servers, CLI roots, GUI Mains).
        *   **Modules/Packages:** (e.g., Shared libraries, Domain logic, Utilities).
        *   **Infrastructure:** (e.g., Database migrations, Docker configs, IaC).
*   **Trace Data Flow:**
    *   Map how data moves through the stack: **Input/Interface** (API Controllers/UI) → **Business Logic** (Services/Use Cases) → **Persistence** (Repositories/ORM/SQL).

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any `progress/*.md` or `TODO` lists found in the context.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists in a file block, dependencies resolve, and logic appears complete.
    *   **Partial/Stubbed:** Functions/Classes exist but return mocks, `NotImplemented` errors, or pass-throughs.
    *   **Missing:** Feature is mentioned in documentation/comments but no corresponding file block exists.
    *   **Divergent:** Implementation contradicts the documentation or apparent architectural intent.
*   *Output a corrected Status Log based on the actual code present.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly? (e.g., Is Domain logic leaking into the View/Controller layer? Are circular dependencies avoided?)
    *   **Security:** Are authorization/authentication checks present at critical boundaries? Is input validation visible?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, unoptimized loops, heavy payloads without DTOs)?
    *   **Type/Memory Safety:** Are types/interfaces consistent across module boundaries? Is error handling robust (e.g., `try/catch`, `Result` types, panic recovery)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across module boundaries.

### 4. System Synthesis
*   Provide a high-level technical summary:
    *   **Core Domain:** What does this specific codebase do? (e.g., "Financial Ledger", "Embedded Control System", "E-commerce Backend").
    *   **Current Capabilities:** What user flows are fully coded? (e.g., "User can login", "Data processing pipeline is active").
    *   **Architecture Quality:** Is the project structure actually being used effectively, or is it just folder organization without modular enforcement?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** files not present in the Markdown context. If a file is referenced in an import but its code block is missing from the context files, mark it as "External/Missing Context."
*   **Citation:** When making a claim, reference the **File Path** provided in the Markdown header (e.g., `src/modules/auth/service.go` or `lib/core/processor.py`).
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/02-requested-files.md`

```md
### The "Context Manifest Request" Prompt

> **System / Prompt:**
>
> I have decided to proceed with **Option [X]: [Insert Track Name]**.
>
> To execute this plan, you need to transition from high-level architecture to low-level implementation.
>
> **Your Task:**
> Analyze the file tree and summaries you currently have. Identify the **critical path files** required to build this feature.
>
> **Output a "Context Manifest" list:**
> Please list the exact file paths I need to copy-paste into this chat so you have the **Ground Truth** (raw source code) necessary to write the implementation.
>
> *   **Group 1: Logic & State** (Files that need functional changes)
> *   **Group 2: UI & Views** (Files that need visual/markup changes)
> *   **Group 3: Data & Config** (Files defining types, schemas, or constants)
>
> *Only request files that are strictly necessary for this specific task.*
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/03-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/00-raw-codebase-ingest-prompt.md`

```md
# Universal Codebase Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a flattened representation of a software repository (code files, configuration, and documentation).

**Ingest ALL provided materials in full.** Treat the **actual code** as the absolute source of truth; documentation, comments, and file names are secondary and may be outdated.

Your immediate tasks are:

### 1. Establish Architectural Ground Truth
*   **Analyze the System Boundaries:**
    *   Identify the high-level architecture (Monorepo, Monolith, Microservices, etc.).
    *   Map the primary boundaries: Frontend vs. Backend, Core Logic vs. Infrastructure, Public API vs. Internal Implementation.
    *   Identify the key frameworks, languages, and runtime environments in use.
*   **Trace the Data Flow:**
    *   Map how data moves through the system (e.g., Client → API/Action → Controller/Service → Database/Store).
    *   Identify how modules communicate (HTTP, RPC, Imports, Events).
*   **Verify Data Models:**
    *   Compare the **Persistence Layer** (SQL schemas, ORM definitions, Store interfaces) against the **Application Layer** (Types, DTOs, Classes).
    *   Identify if data shapes are consistent or if ad-hoc transformations are occurring.

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any provided **Progress Logs, Roadmaps, or TODOs**.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists, is wired up, and appears functional.
    *   **Partial/Stubbed:** Function signatures or UI shells exist, but logic is mocked or incomplete.
    *   **Missing:** Feature is mentioned in docs but no code exists.
    *   **Divergent:** Implementation contradicts the documentation or intent.
*   *Output a corrected Progress Log based on reality.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly (e.g., View logic mixed with DB calls)?
    *   **Security:** Are authorization checks centralized or scattered? Are secrets handled via environment variables?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, large payload selections, blocking operations)?
    *   **Type Safety (if applicable):** Is the type system being used strictly, or bypassed (e.g., `any`, `interface{}`)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across boundaries, or where technical debt is accumulating.

### 4. System Synthesis
*   Provide a high-level technical summary of the system:
    *   **Core Domain:** What is the primary problem this software solves?
    *   **Key Capabilities:** What can the system actually *do* right now?
    *   **Infrastructure:** How is the system configured to run (Docker, Serverless, Node, Go, etc.)?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** features or patterns not present in the file dumps.
*   **Focus on Structural Integrity:** Prioritize architectural health over minor syntax details.
*   **Citation:** When making a claim about the architecture, reference the specific directory or file pattern that proves it.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/02-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/.context-compressor-prompt.md`

```md
### The "Context Compressor" Prompt

Use this prompt when you want to convert raw code into your "Tree + Explanations" format.

> **System / Prompt:**
>
> I am providing a file scan of a module in my monorepo. The input contains the full file tree and source code.
>
> **Your Goal:** Create a **"High-Resolution Interface Map"** of this module to save tokens for future context.
>
> **Output Format:**
> 1.  **The Tree:** Copy the directory tree exactly as provided.
> 2.  **File Summaries:** For every significant file (`.ts`, `.tsx`, `.prisma`), provide a summary using this exact schema:
>
> ```markdown
> ### `[File Name]`
> **Role:** [1 sentence on what this file is responsible for]
> **Key Exports:**
> - `functionName(params): ReturnType` - [1 sentence on purpose. Do NOT explain implementation steps.]
> - `VariableName` - [Explain what state/config this holds]
> **Dependencies:** [List critical internal services/repos it imports]
> ```
>
> **Compression Rules (Strict):**
> 1.  **Ignore Implementation:** I do not want to see `if`, `for`, or logic steps. I only want inputs, outputs, and intent.
> 2.  **Ignore Operational Vars:** Do not list loop counters (`i`), temp variables, or local booleans. Only list **State** (React `useState`, stores), **Config** (constants), or **Database Models**.
> 3.  **Focus on Architecture:** If a file connects `API` to `Repo`, explicitly state that relationship.

NOTE: include all test files in your output architectural report
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/commands.md`

```md
python "C:\projects\repo-runner" --ignore __pycache__ .next node_modules .git .vercel .context package-lock.json --list-scripts .py .md .json .ts .tsx .js .mjs .css .txt --include-readme --output "C:\projects\repo-runner\.dev-prompts\repo-runner-flattened.md"


```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/00-compressed-codebase-ingest-prompt.md`

```md
# Compressed Context Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a codebase that has been flattened into a series of **Context Markdown Files** (e.g., `MODULE-CORE-context.md`, `SRC-API-context.md`, `TREE-ROOT-context.md`).

**Ingest ALL provided Markdown artifacts in full.** These files contain directory trees, file summaries, and raw code blocks. Treat the **content within these blocks** as the absolute source of truth.

Your immediate tasks are:

### 1. Reconstruct & Analyze Ground Truth
*   **Virtualize the Structure:**
    *   Use the `## Tree` sections in the Markdown files to map the full project topology.
    *   Use the `## Files` or `## Summaries` sections to map specific logic to specific paths.
*   **Analyze System Boundaries:**
    *   Identify the high-level architecture based on configuration files present (e.g., `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `pom.xml`, or `Makefile`).
    *   Map the primary boundaries:
        *   **Entry Points:** (e.g., HTTP Servers, CLI roots, GUI Mains).
        *   **Modules/Packages:** (e.g., Shared libraries, Domain logic, Utilities).
        *   **Infrastructure:** (e.g., Database migrations, Docker configs, IaC).
*   **Trace Data Flow:**
    *   Map how data moves through the stack: **Input/Interface** (API Controllers/UI) → **Business Logic** (Services/Use Cases) → **Persistence** (Repositories/ORM/SQL).

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any `progress/*.md` or `TODO` lists found in the context.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists in a file block, dependencies resolve, and logic appears complete.
    *   **Partial/Stubbed:** Functions/Classes exist but return mocks, `NotImplemented` errors, or pass-throughs.
    *   **Missing:** Feature is mentioned in documentation/comments but no corresponding file block exists.
    *   **Divergent:** Implementation contradicts the documentation or apparent architectural intent.
*   *Output a corrected Status Log based on the actual code present.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly? (e.g., Is Domain logic leaking into the View/Controller layer? Are circular dependencies avoided?)
    *   **Security:** Are authorization/authentication checks present at critical boundaries? Is input validation visible?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, unoptimized loops, heavy payloads without DTOs)?
    *   **Type/Memory Safety:** Are types/interfaces consistent across module boundaries? Is error handling robust (e.g., `try/catch`, `Result` types, panic recovery)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across module boundaries.

### 4. System Synthesis
*   Provide a high-level technical summary:
    *   **Core Domain:** What does this specific codebase do? (e.g., "Financial Ledger", "Embedded Control System", "E-commerce Backend").
    *   **Current Capabilities:** What user flows are fully coded? (e.g., "User can login", "Data processing pipeline is active").
    *   **Architecture Quality:** Is the project structure actually being used effectively, or is it just folder organization without modular enforcement?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** files not present in the Markdown context. If a file is referenced in an import but its code block is missing from the context files, mark it as "External/Missing Context."
*   **Citation:** When making a claim, reference the **File Path** provided in the Markdown header (e.g., `src/modules/auth/service.go` or `lib/core/processor.py`).
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/02-requested-files.md`

```md
### The "Context Manifest Request" Prompt

> **System / Prompt:**
>
> I have decided to proceed with **Option [X]: [Insert Track Name]**.
>
> To execute this plan, you need to transition from high-level architecture to low-level implementation.
>
> **Your Task:**
> Analyze the file tree and summaries you currently have. Identify the **critical path files** required to build this feature.
>
> **Output a "Context Manifest" list:**
> Please list the exact file paths I need to copy-paste into this chat so you have the **Ground Truth** (raw source code) necessary to write the implementation.
>
> *   **Group 1: Logic & State** (Files that need functional changes)
> *   **Group 2: UI & Views** (Files that need visual/markup changes)
> *   **Group 3: Data & Config** (Files defining types, schemas, or constants)
>
> *Only request files that are strictly necessary for this specific task.*
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/03-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/00-raw-codebase-ingest-prompt.md`

```md
# Universal Codebase Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a flattened representation of a software repository (code files, configuration, and documentation).

**Ingest ALL provided materials in full.** Treat the **actual code** as the absolute source of truth; documentation, comments, and file names are secondary and may be outdated.

Your immediate tasks are:

### 1. Establish Architectural Ground Truth
*   **Analyze the System Boundaries:**
    *   Identify the high-level architecture (Monorepo, Monolith, Microservices, etc.).
    *   Map the primary boundaries: Frontend vs. Backend, Core Logic vs. Infrastructure, Public API vs. Internal Implementation.
    *   Identify the key frameworks, languages, and runtime environments in use.
*   **Trace the Data Flow:**
    *   Map how data moves through the system (e.g., Client → API/Action → Controller/Service → Database/Store).
    *   Identify how modules communicate (HTTP, RPC, Imports, Events).
*   **Verify Data Models:**
    *   Compare the **Persistence Layer** (SQL schemas, ORM definitions, Store interfaces) against the **Application Layer** (Types, DTOs, Classes).
    *   Identify if data shapes are consistent or if ad-hoc transformations are occurring.

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any provided **Progress Logs, Roadmaps, or TODOs**.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists, is wired up, and appears functional.
    *   **Partial/Stubbed:** Function signatures or UI shells exist, but logic is mocked or incomplete.
    *   **Missing:** Feature is mentioned in docs but no code exists.
    *   **Divergent:** Implementation contradicts the documentation or intent.
*   *Output a corrected Progress Log based on reality.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly (e.g., View logic mixed with DB calls)?
    *   **Security:** Are authorization checks centralized or scattered? Are secrets handled via environment variables?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, large payload selections, blocking operations)?
    *   **Type Safety (if applicable):** Is the type system being used strictly, or bypassed (e.g., `any`, `interface{}`)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across boundaries, or where technical debt is accumulating.

### 4. System Synthesis
*   Provide a high-level technical summary of the system:
    *   **Core Domain:** What is the primary problem this software solves?
    *   **Key Capabilities:** What can the system actually *do* right now?
    *   **Infrastructure:** How is the system configured to run (Docker, Serverless, Node, Go, etc.)?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** features or patterns not present in the file dumps.
*   **Focus on Structural Integrity:** Prioritize architectural health over minor syntax details.
*   **Citation:** When making a claim about the architecture, reference the specific directory or file pattern that proves it.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/02-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/.context-compressor-prompt.md`

```md
### The "Context Compressor" Prompt

Use this prompt when you want to convert raw code into your "Tree + Explanations" format.

> **System / Prompt:**
>
> I am providing a file scan of a module in my monorepo. The input contains the full file tree and source code.
>
> **Your Goal:** Create a **"High-Resolution Interface Map"** of this module to save tokens for future context.
>
> **Output Format:**
> 1.  **The Tree:** Copy the directory tree exactly as provided.
> 2.  **File Summaries:** For every significant file (`.ts`, `.tsx`, `.prisma`), provide a summary using this exact schema:
>
> ```markdown
> ### `[File Name]`
> **Role:** [1 sentence on what this file is responsible for]
> **Key Exports:**
> - `functionName(params): ReturnType` - [1 sentence on purpose. Do NOT explain implementation steps.]
> - `VariableName` - [Explain what state/config this holds]
> **Dependencies:** [List critical internal services/repos it imports]
> ```
>
> **Compression Rules (Strict):**
> 1.  **Ignore Implementation:** I do not want to see `if`, `for`, or logic steps. I only want inputs, outputs, and intent.
> 2.  **Ignore Operational Vars:** Do not list loop counters (`i`), temp variables, or local booleans. Only list **State** (React `useState`, stores), **Config** (constants), or **Database Models**.
> 3.  **Focus on Architecture:** If a file connects `API` to `Repo`, explicitly state that relationship.

NOTE: include all test files in your output architectural report
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/commands.md`

```md
python "C:\projects\repo-runner" --ignore __pycache__ .next node_modules .git .vercel .context package-lock.json --list-scripts .py .md .json .ts .tsx .js .mjs .css .txt --include-readme --output "C:\projects\repo-runner\.dev-prompts\repo-runner-flattened.md"


```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/00-compressed-codebase-ingest-prompt.md`

```md
# Compressed Context Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a codebase that has been flattened into a series of **Context Markdown Files** (e.g., `MODULE-CORE-context.md`, `SRC-API-context.md`, `TREE-ROOT-context.md`).

**Ingest ALL provided Markdown artifacts in full.** These files contain directory trees, file summaries, and raw code blocks. Treat the **content within these blocks** as the absolute source of truth.

Your immediate tasks are:

### 1. Reconstruct & Analyze Ground Truth
*   **Virtualize the Structure:**
    *   Use the `## Tree` sections in the Markdown files to map the full project topology.
    *   Use the `## Files` or `## Summaries` sections to map specific logic to specific paths.
*   **Analyze System Boundaries:**
    *   Identify the high-level architecture based on configuration files present (e.g., `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `pom.xml`, or `Makefile`).
    *   Map the primary boundaries:
        *   **Entry Points:** (e.g., HTTP Servers, CLI roots, GUI Mains).
        *   **Modules/Packages:** (e.g., Shared libraries, Domain logic, Utilities).
        *   **Infrastructure:** (e.g., Database migrations, Docker configs, IaC).
*   **Trace Data Flow:**
    *   Map how data moves through the stack: **Input/Interface** (API Controllers/UI) → **Business Logic** (Services/Use Cases) → **Persistence** (Repositories/ORM/SQL).

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any `progress/*.md` or `TODO` lists found in the context.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists in a file block, dependencies resolve, and logic appears complete.
    *   **Partial/Stubbed:** Functions/Classes exist but return mocks, `NotImplemented` errors, or pass-throughs.
    *   **Missing:** Feature is mentioned in documentation/comments but no corresponding file block exists.
    *   **Divergent:** Implementation contradicts the documentation or apparent architectural intent.
*   *Output a corrected Status Log based on the actual code present.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly? (e.g., Is Domain logic leaking into the View/Controller layer? Are circular dependencies avoided?)
    *   **Security:** Are authorization/authentication checks present at critical boundaries? Is input validation visible?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, unoptimized loops, heavy payloads without DTOs)?
    *   **Type/Memory Safety:** Are types/interfaces consistent across module boundaries? Is error handling robust (e.g., `try/catch`, `Result` types, panic recovery)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across module boundaries.

### 4. System Synthesis
*   Provide a high-level technical summary:
    *   **Core Domain:** What does this specific codebase do? (e.g., "Financial Ledger", "Embedded Control System", "E-commerce Backend").
    *   **Current Capabilities:** What user flows are fully coded? (e.g., "User can login", "Data processing pipeline is active").
    *   **Architecture Quality:** Is the project structure actually being used effectively, or is it just folder organization without modular enforcement?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** files not present in the Markdown context. If a file is referenced in an import but its code block is missing from the context files, mark it as "External/Missing Context."
*   **Citation:** When making a claim, reference the **File Path** provided in the Markdown header (e.g., `src/modules/auth/service.go` or `lib/core/processor.py`).
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/02-requested-files.md`

```md
### The "Context Manifest Request" Prompt

> **System / Prompt:**
>
> I have decided to proceed with **Option [X]: [Insert Track Name]**.
>
> To execute this plan, you need to transition from high-level architecture to low-level implementation.
>
> **Your Task:**
> Analyze the file tree and summaries you currently have. Identify the **critical path files** required to build this feature.
>
> **Output a "Context Manifest" list:**
> Please list the exact file paths I need to copy-paste into this chat so you have the **Ground Truth** (raw source code) necessary to write the implementation.
>
> *   **Group 1: Logic & State** (Files that need functional changes)
> *   **Group 2: UI & Views** (Files that need visual/markup changes)
> *   **Group 3: Data & Config** (Files defining types, schemas, or constants)
>
> *Only request files that are strictly necessary for this specific task.*
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/compressed/03-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/00-raw-codebase-ingest-prompt.md`

```md
# Universal Codebase Ingestion & Architecture Audit Prompt

You are acting as the **Principal Systems Architect**. You have been provided with a flattened representation of a software repository (code files, configuration, and documentation).

**Ingest ALL provided materials in full.** Treat the **actual code** as the absolute source of truth; documentation, comments, and file names are secondary and may be outdated.

Your immediate tasks are:

### 1. Establish Architectural Ground Truth
*   **Analyze the System Boundaries:**
    *   Identify the high-level architecture (Monorepo, Monolith, Microservices, etc.).
    *   Map the primary boundaries: Frontend vs. Backend, Core Logic vs. Infrastructure, Public API vs. Internal Implementation.
    *   Identify the key frameworks, languages, and runtime environments in use.
*   **Trace the Data Flow:**
    *   Map how data moves through the system (e.g., Client → API/Action → Controller/Service → Database/Store).
    *   Identify how modules communicate (HTTP, RPC, Imports, Events).
*   **Verify Data Models:**
    *   Compare the **Persistence Layer** (SQL schemas, ORM definitions, Store interfaces) against the **Application Layer** (Types, DTOs, Classes).
    *   Identify if data shapes are consistent or if ad-hoc transformations are occurring.

### 2. Progress Reconciliation (Audit vs. Plan)
*   Compare the actual code against any provided **Progress Logs, Roadmaps, or TODOs**.
*   **Explicitly Determine Feature Status:**
    *   **Implemented:** Code exists, is wired up, and appears functional.
    *   **Partial/Stubbed:** Function signatures or UI shells exist, but logic is mocked or incomplete.
    *   **Missing:** Feature is mentioned in docs but no code exists.
    *   **Divergent:** Implementation contradicts the documentation or intent.
*   *Output a corrected Progress Log based on reality.*

### 3. Convention & Safety Audit (Critical)
*   **Inspect Pattern Compliance:**
    *   **Architectural Discipline:** Are concerns separated correctly (e.g., View logic mixed with DB calls)?
    *   **Security:** Are authorization checks centralized or scattered? Are secrets handled via environment variables?
    *   **Performance:** Are there obvious bottlenecks (e.g., N+1 queries, large payload selections, blocking operations)?
    *   **Type Safety (if applicable):** Is the type system being used strictly, or bypassed (e.g., `any`, `interface{}`)?
*   **Flag Risks:** Identify "leaks" where implementation details bleed across boundaries, or where technical debt is accumulating.

### 4. System Synthesis
*   Provide a high-level technical summary of the system:
    *   **Core Domain:** What is the primary problem this software solves?
    *   **Key Capabilities:** What can the system actually *do* right now?
    *   **Infrastructure:** How is the system configured to run (Docker, Serverless, Node, Go, etc.)?

---

**Output Constraints:**
*   **Be decisive.** Use terms like "Confirmed," "Missing," "Critical Violation," or "Standard Compliant."
*   **Do not hallucinate** features or patterns not present in the file dumps.
*   **Focus on Structural Integrity:** Prioritize architectural health over minor syntax details.
*   **Citation:** When making a claim about the architecture, reference the specific directory or file pattern that proves it.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/01-next-steps-prompt.md`

```md
# Principal Architect: Strategy & Next Steps Determination

**Context:** You have just ingested the full codebase state, including the recent architectural refactors (e.g., package extraction, auth patterns).

**Goal:** Based **strictly** on the current code reality, propose the next set of implementation targets. Do not invent features; look for gaps between the *current state* and a *production-ready state*.

---

### 1. Architectural Health Check (Pass/Fail)
Before proposing new work, verify the foundation:
*   **Auth Safety:** Is the **"Client-Write / Server-Read"** pattern for authentication fully respected? Flag any regressions immediately.
*   **Boundary Integrity:** Are the imports between `apps/` and `packages/` clean? (e.g., No `package` importing from `app`).
*   **Data Discipline:** Are DTOs being used to mask database internals in the recent features?

### 2. Strategic "Tracks" (Propose 3 Directions)
Present three distinct paths for the next session. For each, list specific files to touch and the technical value add.

#### **Option A: The "Hardening" Track (Security & Scale)**
*   *Focus:* Access Control, Type Safety, Performance.
*   *Look for:* Missing permission checks (`resolveMemorialAccess`), missing DB indexes, loose `any` types, missing pagination cursors.

#### **Option B: The "Feature Loop" Track (Completion)**
*   *Focus:* Closing open loops for the user.
*   *Look for:* "Pending" states that have no "Approve" UI (e.g., Tribute Moderation), missing Notifications for actions, stubbed Email/SMS services.

#### **Option C: The "Polish & Presence" Track (UX/SEO)**
*   *Focus:* Visuals, Discoverability, Smoothness.
*   *Look for:* Missing Metadata/JSON-LD (SEO), Skeleton loading states, transition animations, empty states.

---

### 3. Immediate Recommendation
Based on your analysis, which track do you recommend we execute **right now** to minimize technical debt accumulation?

**Constraints:**
*   Be concise.
*   Do not propose new frameworks.
*   **Wait for my confirmation** on which Track to pursue before generating code.

---

**Output Format:**
1.  **Health Check:** [Pass/Fail] + Notes.
2.  **The Options:** (Bullet points for A, B, C).
3.  **Recommendation:** [Your choice and why].
4.  **Question:** "Which track shall we execute?"
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/.dev-prompts/raw/02-code-conventions-prompt.md`

```md
# Implementation & Verification Prompt (Gemini 3 — Coding Mode)

Based on the prior analysis and agreed-upon next steps, implement the required changes **directly in code**, adhering strictly to existing project conventions.

---

## Implementation Rules (Non-Negotiable)

### 1. Full Files Only
- Unless prohibitively expensive, output **complete, self-contained files**, not partial snippets or diffs.
- Preserve:
  - existing file paths
  - naming conventions
  - import ordering
  - formatting and style
- Do **not** introduce placeholder code or TODOs unless an equivalent pattern already exists in the codebase.

### 2. Convention Preservation
- Follow the project’s established:
  - architectural layering
  - abstraction boundaries
  - naming schemes
  - error-handling patterns
- Do **not** introduce new paradigms, frameworks, or abstractions unless they already exist.
- If a requested change would violate existing conventions, **explicitly refuse** and explain why.

### 3. Scope Discipline
- Implement only what is necessary to fulfill the requested feature or fix.
- Avoid refactors unless they are:
  - unavoidable for correctness, or
  - already implied by the existing code structure.
- Do not opportunistically clean up unrelated areas.

---

## Verification & Testing Requirements

After **each set of implemented files**, provide a **clear, ordered test plan** that enables a developer to verify correctness end-to-end.

### Test Plan Requirements

#### 1. Direct Mapping to Code
- Reference concrete files, functions, endpoints, or UI elements.
- Avoid abstract or high-level testing language.

#### 2. Multi-Layer Coverage (Where Applicable)
- Unit tests (logic-level)
- Integration tests (module or service boundaries)
- Manual verification steps (runtime behavior, UI, API responses)

#### 3. Executable Steps
- Each step must be realistically executable:
  - exact commands
  - inputs to provide
  - expected outputs or state changes
- Clearly distinguish between:
  - required tests
  - optional / exploratory checks

#### 4. Failure Modes & Edge Cases
- Call out known edge cases or failure conditions introduced or touched by the change.
- Explain how to confirm those cases are handled correctly.

---

## Output Structure (Strict)

For each implementation batch, follow **exactly** this structure:

1. **Files Implemented**
   - List file paths
   - Brief description of what changed and why

2. **Full Code**
   - Provide each file **in full**
   - Use separate code blocks per file

3. **Verification Steps**
   - Numbered, ordered steps
   - Explicit expected results for each step

---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code.
```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/dist/repo-copy/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/dist/repo-copy/documents/ARCHITECTURE.md`

```md
# ARCHITECTURE.md

# Architecture (v0.1)

Repo-runner is a deterministic pipeline with strict phase boundaries. In v0.1, the output is purely structural (containment and file fingerprints).

## Pipeline Overview

Inputs:
- Root path(s)
- Config (depth, ignore, extensions, include_readme, tree_only, output root, etc.)

Phases:
1. Scan
2. Normalize
3. Fingerprint
4. Build Structure
5. Write Snapshot
6. Optional Exports

Outputs:
- `manifest.json`
- `structure.json`
- Optional export files under `exports/`

## Components

### 1) Scanner
Responsibility:
- Walk filesystem roots
- Apply ignore rules and depth limits
- Collect candidate files and directories
- Produce a raw file list (absolute paths allowed internally)

Constraints:
- Must be deterministic (sorted traversal)
- Must not depend on OS-specific ordering

### 2) Normalizer
Responsibility:
- Convert absolute paths into normalized repo-relative paths
- Enforce path normalization rules (see ID_SPEC)
- Derive module paths (directories) deterministically
- Produce canonical, comparable identifiers and paths

### 3) Fingerprinter
Responsibility:
- Compute SHA256 for each included file
- Record file size in bytes
- Record language detection (extension-based in v0.1)

Constraints:
- Hash is over file bytes only (no newline normalization)

### 4) Structure Builder
Responsibility:
- Build hierarchical containment:
  - repo root
  - modules (directories)
  - files (leaf nodes)
- Sort modules and files deterministically

### 5) Snapshot Writer
Responsibility:
- Create append-only snapshot folder
- Write `manifest.json` and `structure.json`
- Optionally write `current.json` pointer

Constraints:
- Snapshot folder is immutable once written

### 6) Exporters (Optional)
Responsibility:
- Produce auxiliary human-readable exports (e.g., flatten.md)
- Exporters must not change canonical snapshot data
- Exporters must read from the same scanned set to remain consistent

Example Exporter:
- FlattenMarkdownExporter
  - Produces a deterministic flattened tree and optional file bodies.
  - Intended for context assembly (e.g., Dennis).
  - Must not influence manifest.json or structure.json.

## Data Flow Rules

- No component may “reach backward” and mutate earlier outputs.
- Only the Snapshot Writer touches disk for canonical artifacts.
- Exports are derived and must be safe to delete/regenerate.

## Non-Goals in v0.1

- Graph edges
- Import/export parsing
- Symbol indexing
- Call graph
- Diagram projection

Those are introduced in v0.2+ with separate specs.


```

### `C:/projects/repo-runner/dist/repo-copy/documents/CONFIG_SPEC.md`

```md
# CONFIG_SPEC.md

# Config Spec (v0.1)

Repo-runner accepts configuration via CLI flags. A config file may be introduced later, but v0.1 defines CLI as canonical.

## Required Config Inputs

- One or more root paths (positional args)
- Output root directory

## Core Options

- depth (integer)
  - Maximum directory depth to traverse from each root
  - depth=0 means treat roots as explicit files/directories only (no recursion)

- ignore_names (list of directory/file names)
  - Name-based ignore (not glob)
  - Applies to directory names during traversal, and to file base names if desired
  - Example: node_modules, .git, dist, build, .next

- include_extensions (list of extensions)
  - Only include files whose extension is in this list
  - Extensions must include the dot (e.g., ".ts")

- include_readme (boolean)
  - If true: include README files even if extension filtering would exclude them
  - README detection: README, README.md, README.txt (case-insensitive)

- tree_only (boolean)
  - v0.1 affects exporters only
  - structure.json + manifest.json are unaffected by tree_only
  - tree_only may skip reading file bodies for exports

## Output Options

- output_root (path)
  - Root directory to place snapshots
  - Example: C:\repo-runner-output

- write_current_pointer (boolean)
  - If true, write/update current.json

## Precedence Rules

In v0.1:
- CLI flags are the only config source.
- Defaults apply when flags are omitted.

## Defaults (Recommended)

- depth: 25
- ignore_names: [".git", "node_modules", "__pycache__", "dist", "build", ".next", ".expo", ".venv"]
- include_extensions: common code + config (user-defined)
- include_readme: true
- tree_only: false
- write_current_pointer: true
```

### `C:/projects/repo-runner/dist/repo-copy/documents/CONTRIBUTING.md`

```md
# CONTRIBUTING.md

# Contributing (Solo Discipline)

This project is primarily for internal use, but it follows strict engineering hygiene to protect determinism and compatibility.

## Rules

1) Specs First
- Any change to snapshot formats, ID rules, or determinism rules must update the relevant spec document first.

2) Breaking Changes Require Version Bumps
- Output schema changes require VERSIONING_POLICY compliance.

3) No “Convenient” Non-Determinism
- No random IDs
- No reliance on unordered maps/sets
- No OS-specific ordering assumptions

4) Append-Only Snapshots
- Never overwrite snapshots
- Only current.json may be updated

## Branching (If Using Git)
- main: stable
- dev: active work
- feature/*: scoped changes

## Commit Hygiene
- One change category per commit where possible:
  - spec update
  - implementation
  - tests

## “Dennis Integration” Boundary
- Repo-runner stays generic and deterministic.
- Dennis-specific logic belongs in Dennis.
```

### `C:/projects/repo-runner/dist/repo-copy/documents/DETERMINISM_RULES.md`

```md
# DETERMINISM_RULES.md

# Determinism Rules (v0.1)

Repo-runner must be deterministic across runs given identical repo content and config.

## Ordering

- Directory traversal must be sorted lexicographically by entry name.
- Included file list must be sorted by normalized repo-relative path.
- Module list must be sorted by module path.
- File lists within modules must be sorted.

## Serialization

- JSON must be emitted deterministically:
  - stable key ordering
  - stable list ordering
  - no non-deterministic map iteration

## Hashing

- SHA256 computed from raw file bytes.
- No newline normalization.
- No trimming.
- If a file cannot be read, fail with explicit error.

## Normalization

- Path normalization must be applied before:
  - sorting
  - ID generation
  - JSON emission

## Allowed Non-Determinism

- snapshot_id
- created_utc timestamp

Everything else must remain stable.

## Failure Is Preferred Over Ambiguity

Repo-runner should fail hard if:
- path collisions occur after normalization
- roots escape repo boundary (if enforced)
- unreadable files in the included set
- output snapshot folder already exists

Exporters must consume the canonical scanned file set.
Exporters must not independently walk the filesystem.
```

### `C:/projects/repo-runner/dist/repo-copy/documents/ID_SPEC.md`

```md
# ID_SPEC.md

# Stable ID Spec (v0.1)

Stable IDs are required for deterministic outputs and future graph layering.

## ID Types (v0.1)

- Repository: repo:root
- Module (directory): module:{path}
- File: file:{path}

Where `{path}` is a normalized repo-relative path.

Examples:
- repo:root
- module:src/modules/catalog
- file:src/modules/catalog/index.ts

## Path Normalization

All paths stored in artifacts must be:

1) Repo-relative
- No drive letters
- No absolute paths
- No leading "./" (use plain relative)

2) Forward slashes
- Always use "/" even on Windows

3) Stable casing
- On Windows: normalize to the actual filesystem casing if available, otherwise lower-case.
- Recommended v0.1 rule: lower-case all paths to avoid case drift.
  (This can be revised later, but must be consistent.)

4) No trailing slashes for modules
- module path: "src/app", not "src/app/"

5) No redundant segments
- Remove "." segments
- Collapse ".." deterministically (or disallow roots that escape repo root)

## Stable ID Generation

Given a normalized path:
- file stable_id: "file:" + path
- module stable_id: "module:" + directory_path
- repo stable_id: "repo:root"

No UUIDs.
No random identifiers.

## Collisions

If two included files normalize to the same path (rare, but possible with case conflicts on Windows):
- Repo-runner must detect the collision and fail the run with an explicit error.
- No silent overwrites.

## Future Types (Reserved)

These are not used in v0.1, but reserved for later:
- symbol:{file_path}#{symbol_name}
- external:{package_name}
- edge IDs derived from endpoint IDs
```

### `C:/projects/repo-runner/dist/repo-copy/documents/LANGUAGE_SUPPORT.md`

```md
# LANGUAGE_SUPPORT.md

# Language Support (v0.1)

In v0.1, language support is limited to extension-based detection for metadata only.

## Detection Rules

- language is derived from file extension.
- mapping is configured internally or via a simple mapping table.

Example mapping (illustrative):
- .ts, .tsx, .js, .jsx -> "typescript" or "javascript" (choose one policy and keep it consistent)
- .py -> "python"
- .rs -> "rust"
- .go -> "go"
- .java -> "java"
- .html -> "html"
- .css -> "css"
- .sql -> "sql"
- .toml -> "toml"
- .ps1 -> "powershell"
- .md -> "markdown"

## Policy

- Unknown extensions should be labeled "unknown" and may still be included if allowed by include_extensions.
- README inclusion is controlled separately by include_readme.

## Future (v0.2+)

Language adapters (AST parsing, imports, symbols) will be added later and specified in separate documents.
```

### `C:/projects/repo-runner/dist/repo-copy/documents/REPO_LAYOUT.md`

```md
# REPO_LAYOUT.md

# Repository Layout (repo-runner)

This document defines the expected folder structure for the repo-runner repository itself. The goal is to keep specs stable, implementation modular, and outputs reproducible.

## Top-Level Layout

/
  README.md
  ARCHITECTURE.md
  SNAPSHOT_SPEC.md
  ID_SPEC.md
  CONFIG_SPEC.md
  DETERMINISM_RULES.md
  LANGUAGE_SUPPORT.md
  ROADMAP.md
  TESTING_STRATEGY.md
  VERSIONING_POLICY.md
  CONTRIBUTING.md
  REPO_LAYOUT.md

  src/
  tests/
  fixtures/
  scripts/
  dist/                (optional; build output if applicable)
  .gitignore
  LICENSE              (optional)

## Directory Purposes

### src/
Implementation code lives here.

Recommended internal modules (names are suggestions, not mandates):
- src/scanner/
- src/normalize/
- src/fingerprint/
- src/structure/
- src/snapshot/
- src/exporters/
- src/cli/

Rules:
- Keep phase boundaries clean.
- Do not mix exporters with canonical snapshot writing.

### tests/
Automated tests.

Suggested structure:
- tests/unit/
- tests/integration/
- tests/golden/

Golden tests should compare normalized outputs with snapshot_id/timestamp removed or ignored.

### fixtures/
Small, version-controlled fixture repos for testing.

Examples:
- fixtures/tiny_ts_repo/
- fixtures/mixed_repo/
- fixtures/windows_path_edgecases/

Rules:
- Fixtures must be small enough to run in CI quickly.
- Fixtures should include “annoying” cases (nested dirs, ignored dirs, mixed extensions).

### scripts/
Developer utilities and runner scripts.

Examples:
- scripts/run_fixture_tests.ps1
- scripts/run_fixture_tests.sh
- scripts/dev_snapshot.ps1

Rules:
- scripts/ must never be required for core functionality; they are convenience only.

### dist/ (optional)
Build artifacts if using a compiled language or bundler.

Rules:
- dist/ is never committed unless explicitly desired.
- dist/ should be ignored by git by default.

## Output Location Policy

Repo-runner should never write snapshots into its own repository by default.

Instead:
- Default output root should be user-specified, or
- A safe default like: {repo_root}/.repo-runner/ (for scanned repos), not the tool repo.

## Spec Discipline

All canonical contracts are the spec documents at repo root:
- SNAPSHOT_SPEC.md
- ID_SPEC.md
- CONFIG_SPEC.md
- DETERMINISM_RULES.md
- VERSIONING_POLICY.md

Implementation must follow specs. If implementation needs to change behavior, update specs first.

## Dennis Integration Boundary

Repo-runner is a standalone tool. Dennis consumes outputs.

Repo-runner must not:
- depend on Dennis code
- embed Dennis paths
- assume Dennis runtime environment beyond “local filesystem + CLI execution”

Dennis-specific orchestration belongs in Dennis.
```

### `C:/projects/repo-runner/dist/repo-copy/documents/ROADMAP.md`

```md
# ROADMAP.md

# Roadmap

This roadmap is intentionally staged to preserve determinism and keep complexity layered.

## v0.1 — Structure + Fingerprints (Current)

- structure.json (repo/module/file containment)
- manifest.json (config + file hashes)
- append-only snapshots
- optional exports (flatten.md)

## v0.2 — Dependency Extraction (Imports Only)

- symbols.json (definitions optional)
- imports.json (file-to-file/module import edges)
- external_deps.json (package usage)
- stable external IDs

## v0.3 — Graph Canonicalization

- graph.json as the canonical structure:
  - nodes: repo/module/file/external
  - edges: contains/imports/depends_on
- cycle handling policy

## v0.4 — Diagram Projection

- draw.io export:
  - diagram.drawio
  - mxgraph.xml
- deterministic layout strategy

## v0.5 — Structural Artifacts

- per-node structural artifacts:
  - file artifact
  - module artifact
  - repo artifact
- still non-semantic, template-based

## v0.6+ — Optional LLM Layer (Dennis-Owned)

- semantic compression as a separate layer
- must not break determinism of structural substrate
```

### `C:/projects/repo-runner/dist/repo-copy/documents/SNAPSHOT_SPEC.md`

```md
# SNAPSHOT_SPEC.md

# Snapshot Spec (v0.1)

This document defines the canonical snapshot format and on-disk layout.

## Output Root

Repo-runner writes into an output root directory (configurable). Within it, each run creates a new snapshot folder.

Example:

/repo-runner-output/
  /{snapshot_id}/
    manifest.json
    structure.json
    exports/
      ...
  current.json

## Snapshot Mode

Append-only snapshots are required.

- Every run creates a new `{snapshot_id}` folder.
- No run may overwrite an existing snapshot folder.
- `current.json` may be overwritten to point to the latest snapshot.

## snapshot_id Format

snapshot_id must be:
- Unique per run
- Safe as a folder name on Windows/macOS/Linux
- Deterministic *enough* to avoid collisions, but may include timestamp

Recommended format:

YYYY-MM-DDTHH-mm-ssZ_{short_hash}

Where `short_hash` is derived from:
- normalized roots
- config (ignore/ext/depth)
- optional git commit
- optional file list hash (if available after scan)

## manifest.json Schema

manifest.json describes:
- When the snapshot was made
- What inputs and config were used
- What files were included
- How to fingerprint and compare runs

Required fields:

{
  "schema_version": "1.0",
  "tool": {
    "name": "repo-runner",
    "version": "0.1.0"
  },
  "snapshot": {
    "snapshot_id": "...",
    "created_utc": "YYYY-MM-DDTHH:MM:SSZ",
    "output_root": "normalized path string"
  },
  "inputs": {
    "repo_root": "normalized path string",
    "roots": ["normalized path string", ...],
    "git": {
      "is_repo": true/false,
      "commit": "string or null"
    }
  },
  "config": {
    "depth": number,
    "ignore_names": ["node_modules", ".git", ...],
    "include_extensions": [".ts", ".tsx", ...],
    "include_readme": true/false,
    "tree_only": true/false
  },
  "stats": {
    "file_count": number,
    "total_bytes": number
  },
  "files": [
    {
      "stable_id": "file:src/app/page.tsx",
      "path": "src/app/page.tsx",
      "sha256": "hex string",
      "size_bytes": number,
      "language": "typescript"
    }
  ]
}

Rules:
- `files` must be sorted by `path` ascending.
- `sha256` must be computed from file bytes.
- `path` must follow normalization rules in ID_SPEC.md.

## structure.json Schema

structure.json is hierarchical containment only.

{
  "schema_version": "1.0",
  "repo": {
    "stable_id": "repo:root",
    "root": "repo-relative root (usually '.')",
    "modules": [
      {
        "stable_id": "module:src/app",
        "path": "src/app",
        "files": [
          "file:src/app/page.tsx",
          "file:src/app/layout.tsx"
        ]
      }
    ]
  }
}

Rules:
- `modules` sorted by `path` ascending.
- `files` entries sorted by their file path ascending.
- module membership is defined by directory containment of the file path.

## exports/ Folder

`exports/` is optional.

Anything in `exports/`:
- Must be derivable from the canonical snapshot
- Must be safe to delete and regenerate
- Must not be used as a source of truth

## current.json

Optional pointer for convenience:

{
  "schema_version": "1.0",
  "current_snapshot_id": "{snapshot_id}",
  "path": "{snapshot_id}"
}

Overwriting current.json is allowed.

## Snapshot Resolution Policy

When invoked without explicit snapshot_id:
- Repo-runner or its consumer may default to current.json pointer.

If snapshot_id is provided:
- The specified snapshot folder must exist.
- If not found, fail explicitly.

Snapshot resolution does not mutate snapshots.
```

### `C:/projects/repo-runner/dist/repo-copy/documents/TESTING_STRATEGY.md`

```md
# TESTING_STRATEGY.md

# Testing Strategy (v0.1)

Repo-runner must prove determinism and correctness under realistic repo conditions.

## Test Categories

### 1) Golden Snapshot Tests
- Run repo-runner on a small fixture repo.
- Store expected `structure.json` and `manifest.json` (excluding snapshot_id and timestamp).
- Compare normalized outputs.

### 2) Determinism Re-run Tests
- Run twice on the same fixture with identical config.
- Assert:
  - file list is identical
  - module grouping identical
  - sha256 hashes identical
  - ordering identical

### 3) Drift Detection Tests
- Modify one file byte.
- Assert only that file’s sha256 changes, and totals adjust accordingly.

### 4) Ignore Rule Tests
- Ensure ignored directories are never traversed.
- Ensure ignore list is name-based and deterministic.

### 5) Path Normalization Tests
- Windows-style input paths normalize to repo-relative forward slash format.
- Case normalization policy is enforced consistently.

### 6) Collision Tests
- Simulate two inputs that normalize to the same path.
- Assert hard failure.

## Performance Smoke Test (Non-Blocking v0.1)
- Run on a medium repo (tens of thousands of files).
- Confirm completion and stable output.
- No optimization requirements yet.

## CI Recommendation
- Run fixture tests on:
  - Windows
  - Linux
to catch path normalization and separator issues early.
```

### `C:/projects/repo-runner/dist/repo-copy/documents/VERSIONING_POLICY.md`

```md
# VERSIONING_POLICY.md

# Versioning Policy

Repo-runner uses semantic versioning: MAJOR.MINOR.PATCH.

Because Dennis will consume repo-runner outputs, output compatibility matters.

## MAJOR Version Bump (Breaking)

Any of the following requires a MAJOR bump:
- Changes to stable ID formats
- Changes to path normalization policy
- Changes to snapshot folder contract
- Changes to manifest.json or structure.json schema that are not backward compatible
- Removal/renaming of required fields

## MINOR Version Bump (Backward-Compatible Additions)

Any of the following requires a MINOR bump:
- Adding new optional fields to manifest/structure
- Adding new exporters
- Adding new CLI flags that do not change defaults
- Adding new language detection mappings (if it doesn’t alter existing labels)

## PATCH Version Bump (Fixes Only)

Any of the following requires a PATCH bump:
- Bug fixes that restore intended determinism
- Documentation corrections
- Performance improvements that do not change outputs

## Schema Versioning

Both manifest.json and structure.json include `schema_version`.
- If schema changes in a backward-compatible way: increment MINOR in schema_version (e.g., 1.1)
- If schema changes incompatibly: increment MAJOR in schema_version (e.g., 2.0)

Tool version and schema_version are related but distinct.
```

### `C:/projects/repo-runner/dist/repo-copy/src/__init__.py`

```py

```

### `C:/projects/repo-runner/dist/repo-copy/src/cli/__init__.py`

```py

```

### `C:/projects/repo-runner/dist/repo-copy/src/cli/main.py`

```py
import argparse
import os
from typing import List, Optional

from src.exporters.flatten_markdown_exporter import (
    FlattenMarkdownExporter,
    FlattenOptions,
)
from src.fingerprint.file_fingerprint import FileFingerprint
from src.normalize.path_normalizer import PathNormalizer
from src.scanner.filesystem_scanner import FileSystemScanner
from src.snapshot.snapshot_loader import SnapshotLoader
from src.snapshot.snapshot_writer import SnapshotWriter
from src.structure.structure_builder import StructureBuilder


def _parse_args():
    parser = argparse.ArgumentParser(prog="repo-runner", description="repo-runner v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    # snapshot
    snap = sub.add_parser("snapshot", help="Create a deterministic structural snapshot")
    snap.add_argument("repo_root", help="Repository root path")
    snap.add_argument("--output-root", required=True, help="Output root directory for snapshots")
    snap.add_argument("--depth", type=int, default=25)
    snap.add_argument(
        "--ignore",
        nargs="*",
        default=[".git", "node_modules", "__pycache__", "dist", "build", ".next", ".expo", ".venv"],
    )
    snap.add_argument("--include-extensions", nargs="*", default=[])
    snap.add_argument("--include-readme", action="store_true", default=True)
    snap.add_argument("--no-include-readme", action="store_false", dest="include_readme")
    snap.add_argument("--write-current-pointer", action="store_true", default=True)
    snap.add_argument("--no-write-current-pointer", action="store_false", dest="write_current_pointer")

    # export
    exp = sub.add_parser("export", help="Export derived artifacts from a snapshot")
    exp_sub = exp.add_subparsers(dest="export_command", required=True)

    flatten = exp_sub.add_parser(
        "flatten",
        help="Generate deterministic flatten markdown (list_tree alternative)",
    )
    flatten.add_argument("--output-root", required=True, help="Output root directory where snapshots live")
    flatten.add_argument(
        "--snapshot-id",
        required=False,
        default=None,
        help="Snapshot id to export from (defaults to current)",
    )
    flatten.add_argument("--repo-root", required=True, help="Repo root path (used to read file contents)")
    flatten.add_argument(
        "--output",
        required=False,
        default=None,
        help="Output path for markdown (defaults to snapshot exports/flatten.md)",
    )
    flatten.add_argument("--tree-only", action="store_true", default=False)
    flatten.add_argument("--include-readme", action="store_true", default=True)
    flatten.add_argument("--no-include-readme", action="store_false", dest="include_readme")
    flatten.add_argument("--scope", required=False, default="full")
    flatten.add_argument("--title", required=False, default=None)

    return parser.parse_args()


def _filter_by_extensions(abs_files: List[str], include_exts: List[str]) -> List[str]:
    if not include_exts:
        return abs_files

    include = set([e.lower() for e in include_exts])
    out = []

    for p in abs_files:
        ext = os.path.splitext(p)[1].lower()
        if ext in include:
            out.append(p)

    return out


def run_snapshot(
    repo_root: str,
    output_root: str,
    depth: int,
    ignore: List[str],
    include_extensions: List[str],
    include_readme: bool,
    write_current_pointer: bool,
) -> str:
    repo_root_abs = os.path.abspath(repo_root)

    scanner = FileSystemScanner(depth=depth, ignore_names=set(ignore))
    absolute_files = scanner.scan([repo_root_abs])
    absolute_files = _filter_by_extensions(absolute_files, include_extensions)

    normalizer = PathNormalizer(repo_root_abs)
    file_entries = []
    total_bytes = 0
    seen_ids = set()

    for abs_path in absolute_files:
        normalized = normalizer.normalize(abs_path)

        if not include_readme and os.path.basename(normalized).lower().startswith("readme"):
            continue

        stable_id = normalizer.file_id(normalized)

        if stable_id in seen_ids:
            raise RuntimeError(f"Path collision after normalization: {stable_id}")

        seen_ids.add(stable_id)

        module_path = normalizer.module_path(normalized)
        fp = FileFingerprint.fingerprint(abs_path)
        total_bytes += fp["size_bytes"]

        file_entries.append(
            {
                "stable_id": stable_id,
                "path": normalized,
                "module_path": module_path,
                **fp,
            }
        )

    file_entries = sorted(file_entries, key=lambda x: x["path"])

    structure = StructureBuilder().build(
        repo_id=PathNormalizer.repo_id(),
        files=file_entries,
    )

    manifest = {
        "schema_version": "1.0",
        "tool": {"name": "repo-runner", "version": "0.1.0"},
        "inputs": {
            "repo_root": repo_root_abs.replace("\\", "/"),
            "roots": [repo_root_abs.replace("\\", "/")],
            "git": {
                "is_repo": os.path.isdir(os.path.join(repo_root_abs, ".git")),
                "commit": None,
            },
        },
        "config": {
            "depth": depth,
            "ignore_names": ignore,
            "include_extensions": include_extensions,
            "include_readme": include_readme,
            "tree_only": False,
        },
        "stats": {
            "file_count": len(file_entries),
            "total_bytes": total_bytes,
        },
        "files": file_entries,
    }

    writer = SnapshotWriter(output_root)
    snapshot_id = writer.write(
        manifest,
        structure,
        write_current_pointer=write_current_pointer,
    )

    return snapshot_id


def run_export_flatten(
    output_root: str,
    repo_root: str,
    snapshot_id: Optional[str],
    output_path: Optional[str],
    tree_only: bool,
    include_readme: bool,
    scope: str,
    title: Optional[str],
) -> str:
    loader = SnapshotLoader(output_root)
    snapshot_dir = loader.resolve_snapshot_dir(snapshot_id)
    manifest = loader.load_manifest(snapshot_dir)

    exporter = FlattenMarkdownExporter()

    options = FlattenOptions(
        tree_only=tree_only,
        include_readme=include_readme,
        scope=scope,
    )

    return exporter.export(
        repo_root=os.path.abspath(repo_root),
        snapshot_dir=snapshot_dir,
        manifest=manifest,
        output_path=output_path,
        options=options,
        title=title,
    )


def main():
    args = _parse_args()

    if args.command == "snapshot":
        snap_id = run_snapshot(
            repo_root=args.repo_root,
            output_root=args.output_root,
            depth=args.depth,
            ignore=args.ignore,
            include_extensions=args.include_extensions,
            include_readme=args.include_readme,
            write_current_pointer=args.write_current_pointer,
        )
        print(f"Snapshot created: {snap_id}")
        return

    if args.command == "export" and args.export_command == "flatten":
        out = run_export_flatten(
            output_root=args.output_root,
            repo_root=args.repo_root,
            snapshot_id=args.snapshot_id,
            output_path=args.output,
            tree_only=args.tree_only,
            include_readme=args.include_readme,
            scope=args.scope,
            title=args.title,
        )
        print(f"Wrote: {out}")
        return

    raise RuntimeError("Unhandled command")


if __name__ == "__main__":
    main()
```

### `C:/projects/repo-runner/dist/repo-copy/src/exporters/flatten_markdown_exporter.py`

```py
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class FlattenOptions:
    tree_only: bool
    include_readme: bool
    scope: str  # full | module:<path> | file:<path> | list:<a,b,c> | prefix:<path>


class FlattenMarkdownExporter:
    TEXT_EXTENSIONS = {
        ".ts", ".tsx", ".js", ".jsx",
        ".py", ".rs", ".go", ".java",
        ".json", ".md", ".txt",
        ".html", ".css", ".sql", ".toml",
        ".ps1", ".ejs", ".yml", ".yaml",
        ".env", ".example", ".gitignore",
        ".d.ts",
    }

    def export(
        self,
        repo_root: str,
        snapshot_dir: str,
        manifest: Dict,
        output_path: Optional[str],
        options: FlattenOptions,
        title: Optional[str] = None,
    ) -> str:

        files = self._canonical_files_from_manifest(manifest, options)
        tree_md = self._render_tree([f["path"] for f in files])
        content_md = "" if options.tree_only else self._render_contents(repo_root, files)

        header = [
            f"# {title or 'repo-runner flatten export'}",
            "",
            f"- repo_root: `{repo_root}`",
            f"- snapshot_dir: `{snapshot_dir}`",
            f"- file_count: `{len(files)}`",
            f"- scope: `{options.scope}`",
            f"- tree_only: `{options.tree_only}`",
            "",
        ]

        final_md = "\n".join(header) + tree_md + ("\n" + content_md if content_md else "")

        if output_path is None:
            exports_dir = os.path.join(snapshot_dir, "exports")
            os.makedirs(exports_dir, exist_ok=True)
            output_path = os.path.join(exports_dir, "flatten.md")

        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(final_md)

        return output_path

    def _canonical_files_from_manifest(self, manifest: Dict, options: FlattenOptions) -> List[Dict]:
        files = manifest.get("files", [])
        entries = []

        for entry in files:
            path = entry["path"]

            if not options.include_readme and path.lower().startswith("readme"):
                continue

            entries.append(entry)

        scoped = self._apply_scope(entries, options.scope)

        scoped.sort(key=lambda x: x["path"])
        return scoped

    def _apply_scope(self, entries: List[Dict], scope: str) -> List[Dict]:
        if scope == "full":
            return list(entries)

        if scope.startswith("module:"):
            prefix = scope.split("module:", 1)[1].rstrip("/")
            return [e for e in entries if e["path"].startswith(prefix + "/")]

        if scope.startswith("prefix:"):
            prefix = scope.split("prefix:", 1)[1]
            return [e for e in entries if e["path"].startswith(prefix)]

        if scope.startswith("file:"):
            target = scope.split("file:", 1)[1]
            return [e for e in entries if e["path"] == target]

        if scope.startswith("list:"):
            raw = scope.split("list:", 1)[1]
            targets = [t.strip() for t in raw.split(",") if t.strip()]
            target_set = set(targets)
            return [e for e in entries if e["path"] in target_set]

        raise ValueError(f"Invalid scope: {scope}")

    def _render_tree(self, paths: List[str]) -> str:
        root = {}
        for p in paths:
            parts = [x for x in p.split("/") if x]
            node = root
            for part in parts:
                node = node.setdefault(part, {})

        lines = ["## Tree", "", "```"]
        lines.extend(self._tree_lines(root, ""))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def _tree_lines(self, node: Dict, prefix: str) -> List[str]:
        keys = sorted(node.keys())
        lines = []
        for i, key in enumerate(keys):
            is_last = i == len(keys) - 1
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + key)
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(self._tree_lines(node[key], child_prefix))
        return lines

    def _render_contents(self, repo_root: str, files: List[Dict]) -> str:
        blocks = ["## File Contents", ""]
        for entry in files:
            path = entry["path"]
            abs_path = os.path.join(repo_root, path.replace("/", os.sep))

            blocks.append(f"### `{path}`")
            blocks.append("")

            ext = os.path.splitext(path)[1].lower()

            if ext not in self.TEXT_EXTENSIONS or self._sniff_binary(abs_path):
                blocks.append(self._binary_placeholder(entry))
                blocks.append("")
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError as e:
                content = f"<<ERROR: {e}>>"

            blocks.append(f"```")
            blocks.append(content.rstrip("\n"))
            blocks.append("```")
            blocks.append("")

        return "\n".join(blocks)

    @staticmethod
    def _sniff_binary(abs_path: str) -> bool:
        try:
            with open(abs_path, "rb") as f:
                chunk = f.read(4096)
        except OSError:
            return False
        return b"\x00" in chunk

    @staticmethod
    def _binary_placeholder(entry: Dict) -> str:
        return "\n".join([
            "```",
            "<<BINARY_OR_SKIPPED_FILE>>",
            f"size_bytes: {entry.get('size_bytes')}",
            f"sha256: {entry.get('sha256')}",
            "```",
        ])
```

### `C:/projects/repo-runner/dist/repo-copy/src/fingerprint/file_fingerprint.py`

```py
import hashlib
import os
from typing import Dict


class FileFingerprint:
    LANGUAGE_MAP = {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".toml": "toml",
        ".ps1": "powershell",
        ".md": "markdown",
        ".json": "json",
    }

    @staticmethod
    def fingerprint(path: str) -> Dict:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)

        size = os.path.getsize(path)
        ext = os.path.splitext(path)[1].lower()
        language = FileFingerprint.LANGUAGE_MAP.get(ext, "unknown")

        return {
            "sha256": sha.hexdigest(),
            "size_bytes": size,
            "language": language,
        }
```

### `C:/projects/repo-runner/dist/repo-copy/src/normalize/path_normalizer.py`

```py
import os


class PathNormalizer:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    def normalize(self, absolute_path: str) -> str:
        relative = os.path.relpath(absolute_path, self.repo_root)

        # Normalize separators first.
        normalized = relative.replace("\\", "/")

        # Only strip a literal "./" prefix (do NOT strip leading dots from names like ".context-docs").
        if normalized.startswith("./"):
            normalized = normalized[2:]

        # Normalize any accidental leading slashes (defensive; relpath shouldn't produce these).
        while normalized.startswith("/"):
            normalized = normalized[1:]

        return normalized.lower()

    def module_path(self, file_path: str) -> str:
        directory = os.path.dirname(file_path)
        return directory.replace("\\", "/")

    @staticmethod
    def file_id(normalized_path: str) -> str:
        return f"file:{normalized_path}"

    @staticmethod
    def module_id(module_path: str) -> str:
        return f"module:{module_path}"

    @staticmethod
    def repo_id() -> str:
        return "repo:root"
```

### `C:/projects/repo-runner/dist/repo-copy/src/scanner/filesystem_scanner.py`

```py
import os
from typing import List, Set


class FileSystemScanner:
    def __init__(self, depth: int, ignore_names: Set[str]):
        self.depth = depth
        self.ignore_names = ignore_names

    def scan(self, root_paths: List[str]) -> List[str]:
        all_files = []

        for root in root_paths:
            if os.path.isfile(root):
                all_files.append(os.path.abspath(root))
                continue

            root = os.path.abspath(root)
            all_files.extend(self._walk(root, current_depth=0))

        return sorted(all_files)

    def _walk(self, directory: str, current_depth: int) -> List[str]:
        if self.depth >= 0 and current_depth > self.depth:
            return []

        results = []

        try:
            entries = sorted(os.listdir(directory))
        except OSError:
            return []

        for entry in entries:
            if entry in self.ignore_names:
                continue

            full_path = os.path.join(directory, entry)

            if os.path.isdir(full_path):
                results.extend(self._walk(full_path, current_depth + 1))
            elif os.path.isfile(full_path):
                results.append(os.path.abspath(full_path))

        return results
```

### `C:/projects/repo-runner/dist/repo-copy/src/snapshot/snapshot_loader.py`

```py
import json
import os
from typing import Optional


class SnapshotLoader:
    def __init__(self, output_root: str):
        self.output_root = output_root

    def resolve_snapshot_dir(self, snapshot_id: Optional[str]) -> str:
        if snapshot_id:
            snapshot_dir = os.path.join(self.output_root, snapshot_id)
            if not os.path.isdir(snapshot_dir):
                raise FileNotFoundError(f"Snapshot not found: {snapshot_dir}")
            return snapshot_dir

        current_path = os.path.join(self.output_root, "current.json")
        if not os.path.isfile(current_path):
            raise FileNotFoundError(
                f"current.json not found at output root: {current_path}. "
                "Run `repo-runner snapshot ...` first or pass --snapshot-id."
            )

        with open(current_path, "r", encoding="utf-8") as f:
            current = json.load(f)

        snapshot_id = current.get("current_snapshot_id")
        if not snapshot_id:
            raise ValueError("current.json missing required field: current_snapshot_id")

        snapshot_dir = os.path.join(self.output_root, snapshot_id)
        if not os.path.isdir(snapshot_dir):
            raise FileNotFoundError(f"Snapshot dir referenced by current.json not found: {snapshot_dir}")

        return snapshot_dir

    @staticmethod
    def load_manifest(snapshot_dir: str) -> dict:
        path = os.path.join(snapshot_dir, "manifest.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_structure(snapshot_dir: str) -> dict:
        path = os.path.join(snapshot_dir, "structure.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
```

### `C:/projects/repo-runner/dist/repo-copy/src/snapshot/snapshot_writer.py`

```py
import json
import os
from datetime import datetime
from typing import Dict, Optional


class SnapshotWriter:
    def __init__(self, output_root: str):
        self.output_root = output_root

    def write(
        self,
        manifest: Dict,
        structure: Dict,
        snapshot_id: Optional[str] = None,
        write_current_pointer: bool = True,
    ) -> str:
        os.makedirs(self.output_root, exist_ok=True)

        if snapshot_id is None:
            # v0.1: timestamp-based id; future: append short_hash as per SNAPSHOT_SPEC
            snapshot_id = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

        snapshot_dir = os.path.join(self.output_root, snapshot_id)
        if os.path.exists(snapshot_dir):
            raise RuntimeError(f"Snapshot directory already exists: {snapshot_dir}")

        os.makedirs(snapshot_dir, exist_ok=False)
        os.makedirs(os.path.join(snapshot_dir, "exports"), exist_ok=True)

        # Ensure manifest has snapshot metadata (non-breaking additive)
        manifest = dict(manifest)
        manifest.setdefault("snapshot", {})
        manifest["snapshot"] = dict(manifest["snapshot"])
        manifest["snapshot"].setdefault("snapshot_id", snapshot_id)
        manifest["snapshot"].setdefault("created_utc", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        manifest["snapshot"].setdefault("output_root", self.output_root)

        with open(os.path.join(snapshot_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        with open(os.path.join(snapshot_dir, "structure.json"), "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2, sort_keys=True)

        if write_current_pointer:
            current_path = os.path.join(self.output_root, "current.json")
            with open(current_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "schema_version": "1.0",
                        "current_snapshot_id": snapshot_id,
                        "path": snapshot_id,
                    },
                    f,
                    indent=2,
                    sort_keys=True,
                )

        return snapshot_id
```

### `C:/projects/repo-runner/dist/repo-copy/src/structure/structure_builder.py`

```py
from collections import defaultdict
from typing import Dict, List


class StructureBuilder:
    def build(self, repo_id: str, files: List[Dict]) -> Dict:
        modules = defaultdict(list)

        for file_entry in files:
            module_path = file_entry["module_path"]
            modules[module_path].append(file_entry["stable_id"])

        sorted_modules = sorted(modules.keys())

        module_entries = []
        for module in sorted_modules:
            module_entries.append({
                "stable_id": f"module:{module}",
                "path": module,
                "files": sorted(modules[module])
            })

        return {
            "schema_version": "1.0",
            "repo": {
                "stable_id": repo_id,
                "root": ".",
                "modules": module_entries
            }
        }
```

### `C:/projects/repo-runner/documents/ARCHITECTURE.md`

```md
# ARCHITECTURE.md

# Architecture (v0.1)

Repo-runner is a deterministic pipeline with strict phase boundaries. In v0.1, the output is purely structural (containment and file fingerprints).

## Pipeline Overview

Inputs:
- Root path(s)
- Config (depth, ignore, extensions, include_readme, tree_only, output root, etc.)

Phases:
1. Scan
2. Normalize
3. Fingerprint
4. Build Structure
5. Write Snapshot
6. Optional Exports

Outputs:
- `manifest.json`
- `structure.json`
- Optional export files under `exports/`

## Components

### 1) Scanner
Responsibility:
- Walk filesystem roots
- Apply ignore rules and depth limits
- Collect candidate files and directories
- Produce a raw file list (absolute paths allowed internally)

Constraints:
- Must be deterministic (sorted traversal)
- Must not depend on OS-specific ordering

### 2) Normalizer
Responsibility:
- Convert absolute paths into normalized repo-relative paths
- Enforce path normalization rules (see ID_SPEC)
- Derive module paths (directories) deterministically
- Produce canonical, comparable identifiers and paths

### 3) Fingerprinter
Responsibility:
- Compute SHA256 for each included file
- Record file size in bytes
- Record language detection (extension-based in v0.1)

Constraints:
- Hash is over file bytes only (no newline normalization)

### 4) Structure Builder
Responsibility:
- Build hierarchical containment:
  - repo root
  - modules (directories)
  - files (leaf nodes)
- Sort modules and files deterministically

### 5) Snapshot Writer
Responsibility:
- Create append-only snapshot folder
- Write `manifest.json` and `structure.json`
- Optionally write `current.json` pointer

Constraints:
- Snapshot folder is immutable once written

### 6) Exporters (Optional)
Responsibility:
- Produce auxiliary human-readable exports (e.g., flatten.md)
- Exporters must not change canonical snapshot data
- Exporters must read from the same scanned set to remain consistent

Example Exporter:
- FlattenMarkdownExporter
  - Produces a deterministic flattened tree and optional file bodies.
  - Intended for context assembly (e.g., Dennis).
  - Must not influence manifest.json or structure.json.

## Data Flow Rules

- No component may “reach backward” and mutate earlier outputs.
- Only the Snapshot Writer touches disk for canonical artifacts.
- Exports are derived and must be safe to delete/regenerate.

## Non-Goals in v0.1

- Graph edges
- Import/export parsing
- Symbol indexing
- Call graph
- Diagram projection

Those are introduced in v0.2+ with separate specs.


```

### `C:/projects/repo-runner/documents/CONFIG_SPEC.md`

```md
# CONFIG_SPEC.md

# Config Spec (v0.1)

Repo-runner accepts configuration via CLI flags. A config file may be introduced later, but v0.1 defines CLI as canonical.

## Required Config Inputs

- One or more root paths (positional args)
- Output root directory

## Core Options

- depth (integer)
  - Maximum directory depth to traverse from each root
  - depth=0 means treat roots as explicit files/directories only (no recursion)

- ignore_names (list of directory/file names)
  - Name-based ignore (not glob)
  - Applies to directory names during traversal, and to file base names if desired
  - Example: node_modules, .git, dist, build, .next

- include_extensions (list of extensions)
  - Only include files whose extension is in this list
  - Extensions must include the dot (e.g., ".ts")

- include_readme (boolean)
  - If true: include README files even if extension filtering would exclude them
  - README detection: README, README.md, README.txt (case-insensitive)

- tree_only (boolean)
  - v0.1 affects exporters only
  - structure.json + manifest.json are unaffected by tree_only
  - tree_only may skip reading file bodies for exports

## Output Options

- output_root (path)
  - Root directory to place snapshots
  - Example: C:\repo-runner-output

- write_current_pointer (boolean)
  - If true, write/update current.json

## Precedence Rules

In v0.1:
- CLI flags are the only config source.
- Defaults apply when flags are omitted.

## Defaults (Recommended)

- depth: 25
- ignore_names: [".git", "node_modules", "__pycache__", "dist", "build", ".next", ".expo", ".venv"]
- include_extensions: common code + config (user-defined)
- include_readme: true
- tree_only: false
- write_current_pointer: true
```

### `C:/projects/repo-runner/documents/CONTRIBUTING.md`

```md
# CONTRIBUTING.md

# Contributing (Solo Discipline)

This project is primarily for internal use, but it follows strict engineering hygiene to protect determinism and compatibility.

## Rules

1) Specs First
- Any change to snapshot formats, ID rules, or determinism rules must update the relevant spec document first.

2) Breaking Changes Require Version Bumps
- Output schema changes require VERSIONING_POLICY compliance.

3) No “Convenient” Non-Determinism
- No random IDs
- No reliance on unordered maps/sets
- No OS-specific ordering assumptions

4) Append-Only Snapshots
- Never overwrite snapshots
- Only current.json may be updated

## Branching (If Using Git)
- main: stable
- dev: active work
- feature/*: scoped changes

## Commit Hygiene
- One change category per commit where possible:
  - spec update
  - implementation
  - tests

## “Dennis Integration” Boundary
- Repo-runner stays generic and deterministic.
- Dennis-specific logic belongs in Dennis.
```

### `C:/projects/repo-runner/documents/DETERMINISM_RULES.md`

```md
# DETERMINISM_RULES.md

# Determinism Rules (v0.1)

Repo-runner must be deterministic across runs given identical repo content and config.

## Ordering

- Directory traversal must be sorted lexicographically by entry name.
- Included file list must be sorted by normalized repo-relative path.
- Module list must be sorted by module path.
- File lists within modules must be sorted.

## Serialization

- JSON must be emitted deterministically:
  - stable key ordering
  - stable list ordering
  - no non-deterministic map iteration

## Hashing

- SHA256 computed from raw file bytes.
- No newline normalization.
- No trimming.
- If a file cannot be read, fail with explicit error.

## Normalization

- Path normalization must be applied before:
  - sorting
  - ID generation
  - JSON emission

## Allowed Non-Determinism

- snapshot_id
- created_utc timestamp

Everything else must remain stable.

## Failure Is Preferred Over Ambiguity

Repo-runner should fail hard if:
- path collisions occur after normalization
- roots escape repo boundary (if enforced)
- unreadable files in the included set
- output snapshot folder already exists

Exporters must consume the canonical scanned file set.
Exporters must not independently walk the filesystem.
```

### `C:/projects/repo-runner/documents/ID_SPEC.md`

```md
# ID_SPEC.md

# Stable ID Spec (v0.1)

Stable IDs are required for deterministic outputs and future graph layering.

## ID Types (v0.1)

- Repository: repo:root
- Module (directory): module:{path}
- File: file:{path}

Where `{path}` is a normalized repo-relative path.

Examples:
- repo:root
- module:src/modules/catalog
- file:src/modules/catalog/index.ts

## Path Normalization

All paths stored in artifacts must be:

1) Repo-relative
- No drive letters
- No absolute paths
- No leading "./" (use plain relative)

2) Forward slashes
- Always use "/" even on Windows

3) Stable casing
- On Windows: normalize to the actual filesystem casing if available, otherwise lower-case.
- Recommended v0.1 rule: lower-case all paths to avoid case drift.
  (This can be revised later, but must be consistent.)

4) No trailing slashes for modules
- module path: "src/app", not "src/app/"

5) No redundant segments
- Remove "." segments
- Collapse ".." deterministically (or disallow roots that escape repo root)

## Stable ID Generation

Given a normalized path:
- file stable_id: "file:" + path
- module stable_id: "module:" + directory_path
- repo stable_id: "repo:root"

No UUIDs.
No random identifiers.

## Collisions

If two included files normalize to the same path (rare, but possible with case conflicts on Windows):
- Repo-runner must detect the collision and fail the run with an explicit error.
- No silent overwrites.

## Future Types (Reserved)

These are not used in v0.1, but reserved for later:
- symbol:{file_path}#{symbol_name}
- external:{package_name}
- edge IDs derived from endpoint IDs
```

### `C:/projects/repo-runner/documents/LANGUAGE_SUPPORT.md`

```md
# LANGUAGE_SUPPORT.md

# Language Support (v0.1)

In v0.1, language support is limited to extension-based detection for metadata only.

## Detection Rules

- language is derived from file extension.
- mapping is configured internally or via a simple mapping table.

Example mapping (illustrative):
- .ts, .tsx, .js, .jsx -> "typescript" or "javascript" (choose one policy and keep it consistent)
- .py -> "python"
- .rs -> "rust"
- .go -> "go"
- .java -> "java"
- .html -> "html"
- .css -> "css"
- .sql -> "sql"
- .toml -> "toml"
- .ps1 -> "powershell"
- .md -> "markdown"

## Policy

- Unknown extensions should be labeled "unknown" and may still be included if allowed by include_extensions.
- README inclusion is controlled separately by include_readme.

## Future (v0.2+)

Language adapters (AST parsing, imports, symbols) will be added later and specified in separate documents.
```

### `C:/projects/repo-runner/documents/REPO_LAYOUT.md`

```md
# REPO_LAYOUT.md

# Repository Layout (repo-runner)

This document defines the expected folder structure for the repo-runner repository itself. The goal is to keep specs stable, implementation modular, and outputs reproducible.

## Top-Level Layout

/
  README.md
  ARCHITECTURE.md
  SNAPSHOT_SPEC.md
  ID_SPEC.md
  CONFIG_SPEC.md
  DETERMINISM_RULES.md
  LANGUAGE_SUPPORT.md
  ROADMAP.md
  TESTING_STRATEGY.md
  VERSIONING_POLICY.md
  CONTRIBUTING.md
  REPO_LAYOUT.md

  src/
  tests/
  fixtures/
  scripts/
  dist/                (optional; build output if applicable)
  .gitignore
  LICENSE              (optional)

## Directory Purposes

### src/
Implementation code lives here.

Recommended internal modules (names are suggestions, not mandates):
- src/scanner/
- src/normalize/
- src/fingerprint/
- src/structure/
- src/snapshot/
- src/exporters/
- src/cli/

Rules:
- Keep phase boundaries clean.
- Do not mix exporters with canonical snapshot writing.

### tests/
Automated tests.

Suggested structure:
- tests/unit/
- tests/integration/
- tests/golden/

Golden tests should compare normalized outputs with snapshot_id/timestamp removed or ignored.

### fixtures/
Small, version-controlled fixture repos for testing.

Examples:
- fixtures/tiny_ts_repo/
- fixtures/mixed_repo/
- fixtures/windows_path_edgecases/

Rules:
- Fixtures must be small enough to run in CI quickly.
- Fixtures should include “annoying” cases (nested dirs, ignored dirs, mixed extensions).

### scripts/
Developer utilities and runner scripts.

Examples:
- scripts/run_fixture_tests.ps1
- scripts/run_fixture_tests.sh
- scripts/dev_snapshot.ps1

Rules:
- scripts/ must never be required for core functionality; they are convenience only.

### dist/ (optional)
Build artifacts if using a compiled language or bundler.

Rules:
- dist/ is never committed unless explicitly desired.
- dist/ should be ignored by git by default.

## Output Location Policy

Repo-runner should never write snapshots into its own repository by default.

Instead:
- Default output root should be user-specified, or
- A safe default like: {repo_root}/.repo-runner/ (for scanned repos), not the tool repo.

## Spec Discipline

All canonical contracts are the spec documents at repo root:
- SNAPSHOT_SPEC.md
- ID_SPEC.md
- CONFIG_SPEC.md
- DETERMINISM_RULES.md
- VERSIONING_POLICY.md

Implementation must follow specs. If implementation needs to change behavior, update specs first.

## Dennis Integration Boundary

Repo-runner is a standalone tool. Dennis consumes outputs.

Repo-runner must not:
- depend on Dennis code
- embed Dennis paths
- assume Dennis runtime environment beyond “local filesystem + CLI execution”

Dennis-specific orchestration belongs in Dennis.
```

### `C:/projects/repo-runner/documents/ROADMAP.md`

```md
# ROADMAP.md

# Roadmap

This roadmap is intentionally staged to preserve determinism and keep complexity layered.

## v0.1 — Structure + Fingerprints (Current)

- structure.json (repo/module/file containment)
- manifest.json (config + file hashes)
- append-only snapshots
- optional exports (flatten.md)

## v0.2 — Dependency Extraction (Imports Only)

- symbols.json (definitions optional)
- imports.json (file-to-file/module import edges)
- external_deps.json (package usage)
- stable external IDs

## v0.3 — Graph Canonicalization

- graph.json as the canonical structure:
  - nodes: repo/module/file/external
  - edges: contains/imports/depends_on
- cycle handling policy

## v0.4 — Diagram Projection

- draw.io export:
  - diagram.drawio
  - mxgraph.xml
- deterministic layout strategy

## v0.5 — Structural Artifacts

- per-node structural artifacts:
  - file artifact
  - module artifact
  - repo artifact
- still non-semantic, template-based

## v0.6+ — Optional LLM Layer (Dennis-Owned)

- semantic compression as a separate layer
- must not break determinism of structural substrate
```

### `C:/projects/repo-runner/documents/SNAPSHOT_SPEC.md`

```md
# SNAPSHOT_SPEC.md

# Snapshot Spec (v0.1)

This document defines the canonical snapshot format and on-disk layout.

## Output Root

Repo-runner writes into an output root directory (configurable). Within it, each run creates a new snapshot folder.

Example:

/repo-runner-output/
  /{snapshot_id}/
    manifest.json
    structure.json
    exports/
      ...
  current.json

## Snapshot Mode

Append-only snapshots are required.

- Every run creates a new `{snapshot_id}` folder.
- No run may overwrite an existing snapshot folder.
- `current.json` may be overwritten to point to the latest snapshot.

## snapshot_id Format

snapshot_id must be:
- Unique per run
- Safe as a folder name on Windows/macOS/Linux
- Deterministic *enough* to avoid collisions, but may include timestamp

Recommended format:

YYYY-MM-DDTHH-mm-ssZ_{short_hash}

Where `short_hash` is derived from:
- normalized roots
- config (ignore/ext/depth)
- optional git commit
- optional file list hash (if available after scan)

## manifest.json Schema

manifest.json describes:
- When the snapshot was made
- What inputs and config were used
- What files were included
- How to fingerprint and compare runs

Required fields:

{
  "schema_version": "1.0",
  "tool": {
    "name": "repo-runner",
    "version": "0.1.0"
  },
  "snapshot": {
    "snapshot_id": "...",
    "created_utc": "YYYY-MM-DDTHH:MM:SSZ",
    "output_root": "normalized path string"
  },
  "inputs": {
    "repo_root": "normalized path string",
    "roots": ["normalized path string", ...],
    "git": {
      "is_repo": true/false,
      "commit": "string or null"
    }
  },
  "config": {
    "depth": number,
    "ignore_names": ["node_modules", ".git", ...],
    "include_extensions": [".ts", ".tsx", ...],
    "include_readme": true/false,
    "tree_only": true/false
  },
  "stats": {
    "file_count": number,
    "total_bytes": number
  },
  "files": [
    {
      "stable_id": "file:src/app/page.tsx",
      "path": "src/app/page.tsx",
      "sha256": "hex string",
      "size_bytes": number,
      "language": "typescript"
    }
  ]
}

Rules:
- `files` must be sorted by `path` ascending.
- `sha256` must be computed from file bytes.
- `path` must follow normalization rules in ID_SPEC.md.

## structure.json Schema

structure.json is hierarchical containment only.

{
  "schema_version": "1.0",
  "repo": {
    "stable_id": "repo:root",
    "root": "repo-relative root (usually '.')",
    "modules": [
      {
        "stable_id": "module:src/app",
        "path": "src/app",
        "files": [
          "file:src/app/page.tsx",
          "file:src/app/layout.tsx"
        ]
      }
    ]
  }
}

Rules:
- `modules` sorted by `path` ascending.
- `files` entries sorted by their file path ascending.
- module membership is defined by directory containment of the file path.

## exports/ Folder

`exports/` is optional.

Anything in `exports/`:
- Must be derivable from the canonical snapshot
- Must be safe to delete and regenerate
- Must not be used as a source of truth

## current.json

Optional pointer for convenience:

{
  "schema_version": "1.0",
  "current_snapshot_id": "{snapshot_id}",
  "path": "{snapshot_id}"
}

Overwriting current.json is allowed.

## Snapshot Resolution Policy

When invoked without explicit snapshot_id:
- Repo-runner or its consumer may default to current.json pointer.

If snapshot_id is provided:
- The specified snapshot folder must exist.
- If not found, fail explicitly.

Snapshot resolution does not mutate snapshots.
```

### `C:/projects/repo-runner/documents/TESTING_STRATEGY.md`

```md
# TESTING_STRATEGY.md

# Testing Strategy (v0.1)

Repo-runner must prove determinism and correctness under realistic repo conditions.

## Test Categories

### 1) Golden Snapshot Tests
- Run repo-runner on a small fixture repo.
- Store expected `structure.json` and `manifest.json` (excluding snapshot_id and timestamp).
- Compare normalized outputs.

### 2) Determinism Re-run Tests
- Run twice on the same fixture with identical config.
- Assert:
  - file list is identical
  - module grouping identical
  - sha256 hashes identical
  - ordering identical

### 3) Drift Detection Tests
- Modify one file byte.
- Assert only that file’s sha256 changes, and totals adjust accordingly.

### 4) Ignore Rule Tests
- Ensure ignored directories are never traversed.
- Ensure ignore list is name-based and deterministic.

### 5) Path Normalization Tests
- Windows-style input paths normalize to repo-relative forward slash format.
- Case normalization policy is enforced consistently.

### 6) Collision Tests
- Simulate two inputs that normalize to the same path.
- Assert hard failure.

## Performance Smoke Test (Non-Blocking v0.1)
- Run on a medium repo (tens of thousands of files).
- Confirm completion and stable output.
- No optimization requirements yet.

## CI Recommendation
- Run fixture tests on:
  - Windows
  - Linux
to catch path normalization and separator issues early.
```

### `C:/projects/repo-runner/documents/VERSIONING_POLICY.md`

```md
# VERSIONING_POLICY.md

# Versioning Policy

Repo-runner uses semantic versioning: MAJOR.MINOR.PATCH.

Because Dennis will consume repo-runner outputs, output compatibility matters.

## MAJOR Version Bump (Breaking)

Any of the following requires a MAJOR bump:
- Changes to stable ID formats
- Changes to path normalization policy
- Changes to snapshot folder contract
- Changes to manifest.json or structure.json schema that are not backward compatible
- Removal/renaming of required fields

## MINOR Version Bump (Backward-Compatible Additions)

Any of the following requires a MINOR bump:
- Adding new optional fields to manifest/structure
- Adding new exporters
- Adding new CLI flags that do not change defaults
- Adding new language detection mappings (if it doesn’t alter existing labels)

## PATCH Version Bump (Fixes Only)

Any of the following requires a PATCH bump:
- Bug fixes that restore intended determinism
- Documentation corrections
- Performance improvements that do not change outputs

## Schema Versioning

Both manifest.json and structure.json include `schema_version`.
- If schema changes in a backward-compatible way: increment MINOR in schema_version (e.g., 1.1)
- If schema changes incompatibly: increment MAJOR in schema_version (e.g., 2.0)

Tool version and schema_version are related but distinct.
```

### `C:/projects/repo-runner/src/__init__.py`

```py

```

### `C:/projects/repo-runner/src/cli/__init__.py`

```py

```

### `C:/projects/repo-runner/src/cli/main.py`

```py
import argparse
import os
from typing import List, Optional

from src.exporters.flatten_markdown_exporter import (
    FlattenMarkdownExporter,
    FlattenOptions,
)
from src.fingerprint.file_fingerprint import FileFingerprint
from src.normalize.path_normalizer import PathNormalizer
from src.scanner.filesystem_scanner import FileSystemScanner
from src.snapshot.snapshot_loader import SnapshotLoader
from src.snapshot.snapshot_writer import SnapshotWriter
from src.structure.structure_builder import StructureBuilder


def _parse_args():
    parser = argparse.ArgumentParser(prog="repo-runner", description="repo-runner v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    # snapshot
    snap = sub.add_parser("snapshot", help="Create a deterministic structural snapshot")
    snap.add_argument("repo_root", help="Repository root path")
    snap.add_argument("--output-root", required=True, help="Output root directory for snapshots")
    snap.add_argument("--depth", type=int, default=25)
    snap.add_argument(
        "--ignore",
        nargs="*",
        default=[".git", "node_modules", "__pycache__", "dist", "build", ".next", ".expo", ".venv"],
    )
    snap.add_argument("--include-extensions", nargs="*", default=[])
    snap.add_argument("--include-readme", action="store_true", default=True)
    snap.add_argument("--no-include-readme", action="store_false", dest="include_readme")
    snap.add_argument("--write-current-pointer", action="store_true", default=True)
    snap.add_argument("--no-write-current-pointer", action="store_false", dest="write_current_pointer")

    # export
    exp = sub.add_parser("export", help="Export derived artifacts from a snapshot")
    exp_sub = exp.add_subparsers(dest="export_command", required=True)

    flatten = exp_sub.add_parser(
        "flatten",
        help="Generate deterministic flatten markdown (list_tree alternative)",
    )
    flatten.add_argument("--output-root", required=True, help="Output root directory where snapshots live")
    flatten.add_argument(
        "--snapshot-id",
        required=False,
        default=None,
        help="Snapshot id to export from (defaults to current)",
    )
    flatten.add_argument("--repo-root", required=True, help="Repo root path (used to read file contents)")
    flatten.add_argument(
        "--output",
        required=False,
        default=None,
        help="Output path for markdown (defaults to snapshot exports/flatten.md)",
    )
    flatten.add_argument("--tree-only", action="store_true", default=False)
    flatten.add_argument("--include-readme", action="store_true", default=True)
    flatten.add_argument("--no-include-readme", action="store_false", dest="include_readme")
    flatten.add_argument("--scope", required=False, default="full")
    flatten.add_argument("--title", required=False, default=None)

    return parser.parse_args()


def _filter_by_extensions(abs_files: List[str], include_exts: List[str]) -> List[str]:
    if not include_exts:
        return abs_files

    include = set([e.lower() for e in include_exts])
    out = []

    for p in abs_files:
        ext = os.path.splitext(p)[1].lower()
        if ext in include:
            out.append(p)

    return out


def run_snapshot(
    repo_root: str,
    output_root: str,
    depth: int,
    ignore: List[str],
    include_extensions: List[str],
    include_readme: bool,
    write_current_pointer: bool,
) -> str:
    repo_root_abs = os.path.abspath(repo_root)

    scanner = FileSystemScanner(depth=depth, ignore_names=set(ignore))
    absolute_files = scanner.scan([repo_root_abs])
    absolute_files = _filter_by_extensions(absolute_files, include_extensions)

    normalizer = PathNormalizer(repo_root_abs)
    file_entries = []
    total_bytes = 0
    seen_ids = set()

    for abs_path in absolute_files:
        normalized = normalizer.normalize(abs_path)

        if not include_readme and os.path.basename(normalized).lower().startswith("readme"):
            continue

        stable_id = normalizer.file_id(normalized)

        if stable_id in seen_ids:
            raise RuntimeError(f"Path collision after normalization: {stable_id}")

        seen_ids.add(stable_id)

        module_path = normalizer.module_path(normalized)
        fp = FileFingerprint.fingerprint(abs_path)
        total_bytes += fp["size_bytes"]

        file_entries.append(
            {
                "stable_id": stable_id,
                "path": normalized,
                "module_path": module_path,
                **fp,
            }
        )

    file_entries = sorted(file_entries, key=lambda x: x["path"])

    structure = StructureBuilder().build(
        repo_id=PathNormalizer.repo_id(),
        files=file_entries,
    )

    manifest = {
        "schema_version": "1.0",
        "tool": {"name": "repo-runner", "version": "0.1.0"},
        "inputs": {
            "repo_root": repo_root_abs.replace("\\", "/"),
            "roots": [repo_root_abs.replace("\\", "/")],
            "git": {
                "is_repo": os.path.isdir(os.path.join(repo_root_abs, ".git")),
                "commit": None,
            },
        },
        "config": {
            "depth": depth,
            "ignore_names": ignore,
            "include_extensions": include_extensions,
            "include_readme": include_readme,
            "tree_only": False,
        },
        "stats": {
            "file_count": len(file_entries),
            "total_bytes": total_bytes,
        },
        "files": file_entries,
    }

    writer = SnapshotWriter(output_root)
    snapshot_id = writer.write(
        manifest,
        structure,
        write_current_pointer=write_current_pointer,
    )

    return snapshot_id


def run_export_flatten(
    output_root: str,
    repo_root: str,
    snapshot_id: Optional[str],
    output_path: Optional[str],
    tree_only: bool,
    include_readme: bool,
    scope: str,
    title: Optional[str],
) -> str:
    loader = SnapshotLoader(output_root)
    snapshot_dir = loader.resolve_snapshot_dir(snapshot_id)
    manifest = loader.load_manifest(snapshot_dir)

    exporter = FlattenMarkdownExporter()

    options = FlattenOptions(
        tree_only=tree_only,
        include_readme=include_readme,
        scope=scope,
    )

    return exporter.export(
        repo_root=os.path.abspath(repo_root),
        snapshot_dir=snapshot_dir,
        manifest=manifest,
        output_path=output_path,
        options=options,
        title=title,
    )


def main():
    args = _parse_args()

    if args.command == "snapshot":
        snap_id = run_snapshot(
            repo_root=args.repo_root,
            output_root=args.output_root,
            depth=args.depth,
            ignore=args.ignore,
            include_extensions=args.include_extensions,
            include_readme=args.include_readme,
            write_current_pointer=args.write_current_pointer,
        )
        print(f"Snapshot created: {snap_id}")
        return

    if args.command == "export" and args.export_command == "flatten":
        out = run_export_flatten(
            output_root=args.output_root,
            repo_root=args.repo_root,
            snapshot_id=args.snapshot_id,
            output_path=args.output,
            tree_only=args.tree_only,
            include_readme=args.include_readme,
            scope=args.scope,
            title=args.title,
        )
        print(f"Wrote: {out}")
        return

    raise RuntimeError("Unhandled command")


if __name__ == "__main__":
    main()
```

### `C:/projects/repo-runner/src/exporters/flatten_markdown_exporter.py`

```py
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class FlattenOptions:
    tree_only: bool
    include_readme: bool
    scope: str  # full | module:<path> | file:<path> | list:<a,b,c> | prefix:<path>


class FlattenMarkdownExporter:
    TEXT_EXTENSIONS = {
        ".ts", ".tsx", ".js", ".jsx",
        ".py", ".rs", ".go", ".java",
        ".json", ".md", ".txt",
        ".html", ".css", ".sql", ".toml",
        ".ps1", ".ejs", ".yml", ".yaml",
        ".env", ".example", ".gitignore",
        ".d.ts",
    }

    def export(
        self,
        repo_root: str,
        snapshot_dir: str,
        manifest: Dict,
        output_path: Optional[str],
        options: FlattenOptions,
        title: Optional[str] = None,
    ) -> str:

        files = self._canonical_files_from_manifest(manifest, options)
        tree_md = self._render_tree([f["path"] for f in files])
        content_md = "" if options.tree_only else self._render_contents(repo_root, files)

        header = [
            f"# {title or 'repo-runner flatten export'}",
            "",
            f"- repo_root: `{repo_root}`",
            f"- snapshot_dir: `{snapshot_dir}`",
            f"- file_count: `{len(files)}`",
            f"- scope: `{options.scope}`",
            f"- tree_only: `{options.tree_only}`",
            "",
        ]

        final_md = "\n".join(header) + tree_md + ("\n" + content_md if content_md else "")

        if output_path is None:
            exports_dir = os.path.join(snapshot_dir, "exports")
            os.makedirs(exports_dir, exist_ok=True)
            output_path = os.path.join(exports_dir, "flatten.md")

        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(final_md)

        return output_path

    def _canonical_files_from_manifest(self, manifest: Dict, options: FlattenOptions) -> List[Dict]:
        files = manifest.get("files", [])
        entries = []

        for entry in files:
            path = entry["path"]

            if not options.include_readme and path.lower().startswith("readme"):
                continue

            entries.append(entry)

        scoped = self._apply_scope(entries, options.scope)

        scoped.sort(key=lambda x: x["path"])
        return scoped

    def _apply_scope(self, entries: List[Dict], scope: str) -> List[Dict]:
        if scope == "full":
            return list(entries)

        if scope.startswith("module:"):
            prefix = scope.split("module:", 1)[1].rstrip("/")
            return [e for e in entries if e["path"].startswith(prefix + "/")]

        if scope.startswith("prefix:"):
            prefix = scope.split("prefix:", 1)[1]
            return [e for e in entries if e["path"].startswith(prefix)]

        if scope.startswith("file:"):
            target = scope.split("file:", 1)[1]
            return [e for e in entries if e["path"] == target]

        if scope.startswith("list:"):
            raw = scope.split("list:", 1)[1]
            targets = [t.strip() for t in raw.split(",") if t.strip()]
            target_set = set(targets)
            return [e for e in entries if e["path"] in target_set]

        raise ValueError(f"Invalid scope: {scope}")

    def _render_tree(self, paths: List[str]) -> str:
        root = {}
        for p in paths:
            parts = [x for x in p.split("/") if x]
            node = root
            for part in parts:
                node = node.setdefault(part, {})

        lines = ["## Tree", "", "```"]
        lines.extend(self._tree_lines(root, ""))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def _tree_lines(self, node: Dict, prefix: str) -> List[str]:
        keys = sorted(node.keys())
        lines = []
        for i, key in enumerate(keys):
            is_last = i == len(keys) - 1
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + key)
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(self._tree_lines(node[key], child_prefix))
        return lines

    def _render_contents(self, repo_root: str, files: List[Dict]) -> str:
        blocks = ["## File Contents", ""]
        for entry in files:
            path = entry["path"]
            abs_path = os.path.join(repo_root, path.replace("/", os.sep))

            blocks.append(f"### `{path}`")
            blocks.append("")

            ext = os.path.splitext(path)[1].lower()

            if ext not in self.TEXT_EXTENSIONS or self._sniff_binary(abs_path):
                blocks.append(self._binary_placeholder(entry))
                blocks.append("")
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError as e:
                content = f"<<ERROR: {e}>>"

            blocks.append(f"```")
            blocks.append(content.rstrip("\n"))
            blocks.append("```")
            blocks.append("")

        return "\n".join(blocks)

    @staticmethod
    def _sniff_binary(abs_path: str) -> bool:
        try:
            with open(abs_path, "rb") as f:
                chunk = f.read(4096)
        except OSError:
            return False
        return b"\x00" in chunk

    @staticmethod
    def _binary_placeholder(entry: Dict) -> str:
        return "\n".join([
            "```",
            "<<BINARY_OR_SKIPPED_FILE>>",
            f"size_bytes: {entry.get('size_bytes')}",
            f"sha256: {entry.get('sha256')}",
            "```",
        ])
```

### `C:/projects/repo-runner/src/fingerprint/file_fingerprint.py`

```py
import hashlib
import os
from typing import Dict


class FileFingerprint:
    LANGUAGE_MAP = {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".toml": "toml",
        ".ps1": "powershell",
        ".md": "markdown",
        ".json": "json",
    }

    @staticmethod
    def fingerprint(path: str) -> Dict:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)

        size = os.path.getsize(path)
        ext = os.path.splitext(path)[1].lower()
        language = FileFingerprint.LANGUAGE_MAP.get(ext, "unknown")

        return {
            "sha256": sha.hexdigest(),
            "size_bytes": size,
            "language": language,
        }
```

### `C:/projects/repo-runner/src/normalize/path_normalizer.py`

```py
import os


class PathNormalizer:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    def normalize(self, absolute_path: str) -> str:
        relative = os.path.relpath(absolute_path, self.repo_root)

        # Normalize separators first.
        normalized = relative.replace("\\", "/")

        # Only strip a literal "./" prefix (do NOT strip leading dots from names like ".context-docs").
        if normalized.startswith("./"):
            normalized = normalized[2:]

        # Normalize any accidental leading slashes (defensive; relpath shouldn't produce these).
        while normalized.startswith("/"):
            normalized = normalized[1:]

        return normalized.lower()

    def module_path(self, file_path: str) -> str:
        directory = os.path.dirname(file_path)
        return directory.replace("\\", "/")

    @staticmethod
    def file_id(normalized_path: str) -> str:
        return f"file:{normalized_path}"

    @staticmethod
    def module_id(module_path: str) -> str:
        return f"module:{module_path}"

    @staticmethod
    def repo_id() -> str:
        return "repo:root"
```

### `C:/projects/repo-runner/src/scanner/filesystem_scanner.py`

```py
import os
from typing import List, Set


class FileSystemScanner:
    def __init__(self, depth: int, ignore_names: Set[str]):
        self.depth = depth
        self.ignore_names = ignore_names

    def scan(self, root_paths: List[str]) -> List[str]:
        all_files = []

        for root in root_paths:
            if os.path.isfile(root):
                all_files.append(os.path.abspath(root))
                continue

            root = os.path.abspath(root)
            all_files.extend(self._walk(root, current_depth=0))

        return sorted(all_files)

    def _walk(self, directory: str, current_depth: int) -> List[str]:
        if self.depth >= 0 and current_depth > self.depth:
            return []

        results = []

        try:
            entries = sorted(os.listdir(directory))
        except OSError:
            return []

        for entry in entries:
            if entry in self.ignore_names:
                continue

            full_path = os.path.join(directory, entry)

            if os.path.isdir(full_path):
                results.extend(self._walk(full_path, current_depth + 1))
            elif os.path.isfile(full_path):
                results.append(os.path.abspath(full_path))

        return results
```

### `C:/projects/repo-runner/src/snapshot/snapshot_loader.py`

```py
import json
import os
from typing import Optional


class SnapshotLoader:
    def __init__(self, output_root: str):
        self.output_root = output_root

    def resolve_snapshot_dir(self, snapshot_id: Optional[str]) -> str:
        if snapshot_id:
            snapshot_dir = os.path.join(self.output_root, snapshot_id)
            if not os.path.isdir(snapshot_dir):
                raise FileNotFoundError(f"Snapshot not found: {snapshot_dir}")
            return snapshot_dir

        current_path = os.path.join(self.output_root, "current.json")
        if not os.path.isfile(current_path):
            raise FileNotFoundError(
                f"current.json not found at output root: {current_path}. "
                "Run `repo-runner snapshot ...` first or pass --snapshot-id."
            )

        with open(current_path, "r", encoding="utf-8") as f:
            current = json.load(f)

        snapshot_id = current.get("current_snapshot_id")
        if not snapshot_id:
            raise ValueError("current.json missing required field: current_snapshot_id")

        snapshot_dir = os.path.join(self.output_root, snapshot_id)
        if not os.path.isdir(snapshot_dir):
            raise FileNotFoundError(f"Snapshot dir referenced by current.json not found: {snapshot_dir}")

        return snapshot_dir

    @staticmethod
    def load_manifest(snapshot_dir: str) -> dict:
        path = os.path.join(snapshot_dir, "manifest.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_structure(snapshot_dir: str) -> dict:
        path = os.path.join(snapshot_dir, "structure.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
```

### `C:/projects/repo-runner/src/snapshot/snapshot_writer.py`

```py
import json
import os
from datetime import datetime
from typing import Dict, Optional


class SnapshotWriter:
    def __init__(self, output_root: str):
        self.output_root = output_root

    def write(
        self,
        manifest: Dict,
        structure: Dict,
        snapshot_id: Optional[str] = None,
        write_current_pointer: bool = True,
    ) -> str:
        os.makedirs(self.output_root, exist_ok=True)

        if snapshot_id is None:
            # v0.1: timestamp-based id; future: append short_hash as per SNAPSHOT_SPEC
            snapshot_id = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

        snapshot_dir = os.path.join(self.output_root, snapshot_id)
        if os.path.exists(snapshot_dir):
            raise RuntimeError(f"Snapshot directory already exists: {snapshot_dir}")

        os.makedirs(snapshot_dir, exist_ok=False)
        os.makedirs(os.path.join(snapshot_dir, "exports"), exist_ok=True)

        # Ensure manifest has snapshot metadata (non-breaking additive)
        manifest = dict(manifest)
        manifest.setdefault("snapshot", {})
        manifest["snapshot"] = dict(manifest["snapshot"])
        manifest["snapshot"].setdefault("snapshot_id", snapshot_id)
        manifest["snapshot"].setdefault("created_utc", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        manifest["snapshot"].setdefault("output_root", self.output_root)

        with open(os.path.join(snapshot_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        with open(os.path.join(snapshot_dir, "structure.json"), "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2, sort_keys=True)

        if write_current_pointer:
            current_path = os.path.join(self.output_root, "current.json")
            with open(current_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "schema_version": "1.0",
                        "current_snapshot_id": snapshot_id,
                        "path": snapshot_id,
                    },
                    f,
                    indent=2,
                    sort_keys=True,
                )

        return snapshot_id
```

### `C:/projects/repo-runner/src/structure/structure_builder.py`

```py
from collections import defaultdict
from typing import Dict, List


class StructureBuilder:
    def build(self, repo_id: str, files: List[Dict]) -> Dict:
        modules = defaultdict(list)

        for file_entry in files:
            module_path = file_entry["module_path"]
            modules[module_path].append(file_entry["stable_id"])

        sorted_modules = sorted(modules.keys())

        module_entries = []
        for module in sorted_modules:
            module_entries.append({
                "stable_id": f"module:{module}",
                "path": module,
                "files": sorted(modules[module])
            })

        return {
            "schema_version": "1.0",
            "repo": {
                "stable_id": repo_id,
                "root": ".",
                "modules": module_entries
            }
        }
```


```

### `C:/projects/repo-runner/README.md`

```md
Good. This is the moment to formalize it properly.

Below is a clean, production-grade `README.md` for **repo-runner v0.1** reflecting:

* snapshot-first architecture
* deterministic guarantees
* flatten exporter (list_tree replacement)
* current snapshot defaulting
* strict separation from Dennis

You can drop this directly into the repo root.

---

# repo-runner

Deterministic repository structure compiler.

repo-runner scans a repository, produces an immutable structural snapshot, and exports derived context artifacts (such as a flattened markdown tree) for downstream systems like Dennis.

It is not an LLM tool.
It is a structural substrate generator.

---

## Design Goals

* Deterministic outputs
* Stable IDs
* Append-only snapshots
* Canonical structure first, exports second
* No semantic interpretation
* No mutation of past snapshots

repo-runner is built to be a foundational layer in a larger AI ecosystem, but remains completely standalone.

---

## Core Concepts

### 1. Snapshot-First Architecture

Every operation begins with a snapshot.

```
Filesystem
  → snapshot
    → manifest.json
    → structure.json
    → exports/
```

Snapshots are immutable.
The `current.json` pointer references the latest snapshot.

Exports are derived projections of a snapshot — never of the live filesystem.

---

### 2. Determinism

Given:

* the same repository state
* the same configuration
* the same repo-runner version

You will get:

* identical manifest.json
* identical structure.json
* identical flatten exports (byte-for-byte)

repo-runner does not rely on:

* timestamps inside exports
* random IDs
* UUIDs
* unordered traversal

All ordering is lexicographically deterministic.

---

### 3. Stable IDs

Files use canonical normalized paths:

```
file:src/app/page.tsx
module:src/app
repo:root
```

Path normalization:

* repo-relative
* forward slashes
* preserves leading dots (e.g., `.context-docs`)
* lowercase normalized IDs
* collision detection enforced

Stable IDs never use random values.

---

## Commands

### Create a Snapshot

```powershell
python -m src.cli.main snapshot C:\projects\caffeine-melts-website `
  --output-root C:\repo-runner-output `
  --depth 10 `
  --ignore node_modules .expo .git __pycache__ dist build .next
```

Produces:

```
C:\repo-runner-output\
  2026-02-18T06-16-09Z\
    manifest.json
    structure.json
    exports\
  current.json
```

`current.json` is automatically updated unless disabled.

---

### Export Flatten (list_tree replacement)

Export from the current snapshot:

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website
```

Writes:

```
<snapshot>\exports\flatten.md
```

This replaces manual `list_tree.py` workflows.

---

### Export Tree Only

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --tree-only
```

Equivalent to your old `--tree-only` usage.

---

### Export From a Specific Snapshot

```powershell
python -m src.cli.main export flatten `
  --output-root C:\repo-runner-output `
  --repo-root C:\projects\caffeine-melts-website `
  --snapshot-id 2026-02-18T06-16-09Z
```

If `--snapshot-id` is not provided, repo-runner defaults to `current.json`.

---

## Flatten Export Behavior

The flatten exporter:

* uses the canonical file set from `manifest.json`
* renders a deterministic tree
* optionally concatenates file contents
* skips binary files by default
* emits stable placeholders for binary files:

```
<<BINARY_OR_SKIPPED_FILE>>
language: unknown
size_bytes: 182343
sha256: ...
```

No binary garbage is ever inlined.

---

## Snapshot Contents

### manifest.json

Contains:

* schema_version
* tool metadata
* inputs
* config
* stats
* canonical file list (with sha256, size, language)
* snapshot metadata

### structure.json

Contains:

* schema_version
* repository node
* modules
* file containment

structure.json is structural only — no imports, no semantics.

---

## What repo-runner Is Not

* Not an LLM summarizer
* Not a semantic analyzer (yet)
* Not a code modifier
* Not a refactoring engine
* Not tied to Dennis

repo-runner produces deterministic structure.
Dennis consumes it.

---

## Architecture Overview

```
scanner/
normalize/
fingerprint/
structure/
snapshot/
exporters/
cli/
```

Flow:

```
filesystem
  → scanner
    → normalizer
      → fingerprint
        → structure builder
          → snapshot writer
            → exporter
```

Exports are projections of snapshot state.

---

## Determinism Rules

* Files sorted lexicographically
* Modules sorted lexicographically
* No random UUIDs
* No nondeterministic traversal
* No implicit filesystem rescans during export
* Exporters consume manifest, not filesystem discovery

---

## Versioning

repo-runner follows semantic versioning:

MAJOR.MINOR.PATCH

Breaking changes include:

* stable ID format changes
* path normalization changes
* snapshot schema changes
* manifest/structure schema changes

Backward-compatible additions increment MINOR.

---

## Why This Exists

repo-runner exists to create a clean, stable structural substrate for:

* context assembly
* dependency graph generation
* change impact analysis
* semantic layering
* AI orchestration

But v0.1 intentionally does only structure and flatten export.

Graph generation is planned for a future version.

---

## Roadmap (High-Level)

v0.1

* deterministic snapshot
* flatten exporter

v0.2

* import graph
* external dependency edges
* graph.json

v0.3

* draw.io exporter
* subgraph exports
* scoped context export

---

## Development Philosophy

* Deterministic first
* Structure before semantics
* Append-only snapshots
* Explicit contracts
* No hidden magic

repo-runner is infrastructure.

---

If you want, next we can:

* write a minimal CONTRIBUTING.md aligned to this readme
* or implement `--scope module:` support to eliminate your manual PowerShell zoo entirely
* or move into graph layer design cleanly without contaminating determinism

You’ve got a real substrate now.

```

### `C:/projects/repo-runner/documents/ARCHITECTURE.md`

```md
# ARCHITECTURE.md

# Architecture (v0.1)

Repo-runner is a deterministic pipeline with strict phase boundaries. In v0.1, the output is purely structural (containment and file fingerprints).

## Pipeline Overview

Inputs:
- Root path(s)
- Config (depth, ignore, extensions, include_readme, tree_only, output root, etc.)

Phases:
1. Scan
2. Normalize
3. Fingerprint
4. Build Structure
5. Write Snapshot
6. Optional Exports

Outputs:
- `manifest.json`
- `structure.json`
- Optional export files under `exports/`

## Components

### 1) Scanner
Responsibility:
- Walk filesystem roots
- Apply ignore rules and depth limits
- Collect candidate files and directories
- Produce a raw file list (absolute paths allowed internally)

Constraints:
- Must be deterministic (sorted traversal)
- Must not depend on OS-specific ordering

### 2) Normalizer
Responsibility:
- Convert absolute paths into normalized repo-relative paths
- Enforce path normalization rules (see ID_SPEC)
- Derive module paths (directories) deterministically
- Produce canonical, comparable identifiers and paths

### 3) Fingerprinter
Responsibility:
- Compute SHA256 for each included file
- Record file size in bytes
- Record language detection (extension-based in v0.1)

Constraints:
- Hash is over file bytes only (no newline normalization)

### 4) Structure Builder
Responsibility:
- Build hierarchical containment:
  - repo root
  - modules (directories)
  - files (leaf nodes)
- Sort modules and files deterministically

### 5) Snapshot Writer
Responsibility:
- Create append-only snapshot folder
- Write `manifest.json` and `structure.json`
- Optionally write `current.json` pointer

Constraints:
- Snapshot folder is immutable once written

### 6) Exporters (Optional)
Responsibility:
- Produce auxiliary human-readable exports (e.g., flatten.md)
- Exporters must not change canonical snapshot data
- Exporters must read from the same scanned set to remain consistent

Example Exporter:
- FlattenMarkdownExporter
  - Produces a deterministic flattened tree and optional file bodies.
  - Intended for context assembly (e.g., Dennis).
  - Must not influence manifest.json or structure.json.

## Data Flow Rules

- No component may “reach backward” and mutate earlier outputs.
- Only the Snapshot Writer touches disk for canonical artifacts.
- Exports are derived and must be safe to delete/regenerate.

## Non-Goals in v0.1

- Graph edges
- Import/export parsing
- Symbol indexing
- Call graph
- Diagram projection

Those are introduced in v0.2+ with separate specs.


```

### `C:/projects/repo-runner/documents/CONFIG_SPEC.md`

```md
# CONFIG_SPEC.md

# Config Spec (v0.1)

Repo-runner accepts configuration via CLI flags. A config file may be introduced later, but v0.1 defines CLI as canonical.

## Required Config Inputs

- One or more root paths (positional args)
- Output root directory

## Core Options

- depth (integer)
  - Maximum directory depth to traverse from each root
  - depth=0 means treat roots as explicit files/directories only (no recursion)

- ignore_names (list of directory/file names)
  - Name-based ignore (not glob)
  - Applies to directory names during traversal, and to file base names if desired
  - Example: node_modules, .git, dist, build, .next

- include_extensions (list of extensions)
  - Only include files whose extension is in this list
  - Extensions must include the dot (e.g., ".ts")

- include_readme (boolean)
  - If true: include README files even if extension filtering would exclude them
  - README detection: README, README.md, README.txt (case-insensitive)

- tree_only (boolean)
  - v0.1 affects exporters only
  - structure.json + manifest.json are unaffected by tree_only
  - tree_only may skip reading file bodies for exports

## Output Options

- output_root (path)
  - Root directory to place snapshots
  - Example: C:\repo-runner-output

- write_current_pointer (boolean)
  - If true, write/update current.json

## Precedence Rules

In v0.1:
- CLI flags are the only config source.
- Defaults apply when flags are omitted.

## Defaults (Recommended)

- depth: 25
- ignore_names: [".git", "node_modules", "__pycache__", "dist", "build", ".next", ".expo", ".venv"]
- include_extensions: common code + config (user-defined)
- include_readme: true
- tree_only: false
- write_current_pointer: true
```

### `C:/projects/repo-runner/documents/CONTRIBUTING.md`

```md
# CONTRIBUTING.md

# Contributing (Solo Discipline)

This project is primarily for internal use, but it follows strict engineering hygiene to protect determinism and compatibility.

## Rules

1) Specs First
- Any change to snapshot formats, ID rules, or determinism rules must update the relevant spec document first.

2) Breaking Changes Require Version Bumps
- Output schema changes require VERSIONING_POLICY compliance.

3) No “Convenient” Non-Determinism
- No random IDs
- No reliance on unordered maps/sets
- No OS-specific ordering assumptions

4) Append-Only Snapshots
- Never overwrite snapshots
- Only current.json may be updated

## Branching (If Using Git)
- main: stable
- dev: active work
- feature/*: scoped changes

## Commit Hygiene
- One change category per commit where possible:
  - spec update
  - implementation
  - tests

## “Dennis Integration” Boundary
- Repo-runner stays generic and deterministic.
- Dennis-specific logic belongs in Dennis.
```

### `C:/projects/repo-runner/documents/DETERMINISM_RULES.md`

```md
# DETERMINISM_RULES.md

# Determinism Rules (v0.1)

Repo-runner must be deterministic across runs given identical repo content and config.

## Ordering

- Directory traversal must be sorted lexicographically by entry name.
- Included file list must be sorted by normalized repo-relative path.
- Module list must be sorted by module path.
- File lists within modules must be sorted.

## Serialization

- JSON must be emitted deterministically:
  - stable key ordering
  - stable list ordering
  - no non-deterministic map iteration

## Hashing

- SHA256 computed from raw file bytes.
- No newline normalization.
- No trimming.
- If a file cannot be read, fail with explicit error.

## Normalization

- Path normalization must be applied before:
  - sorting
  - ID generation
  - JSON emission

## Allowed Non-Determinism

- snapshot_id
- created_utc timestamp

Everything else must remain stable.

## Failure Is Preferred Over Ambiguity

Repo-runner should fail hard if:
- path collisions occur after normalization
- roots escape repo boundary (if enforced)
- unreadable files in the included set
- output snapshot folder already exists

Exporters must consume the canonical scanned file set.
Exporters must not independently walk the filesystem.
```

### `C:/projects/repo-runner/documents/ID_SPEC.md`

```md
# ID_SPEC.md

# Stable ID Spec (v0.1)

Stable IDs are required for deterministic outputs and future graph layering.

## ID Types (v0.1)

- Repository: repo:root
- Module (directory): module:{path}
- File: file:{path}

Where `{path}` is a normalized repo-relative path.

Examples:
- repo:root
- module:src/modules/catalog
- file:src/modules/catalog/index.ts

## Path Normalization

All paths stored in artifacts must be:

1) Repo-relative
- No drive letters
- No absolute paths
- No leading "./" (use plain relative)

2) Forward slashes
- Always use "/" even on Windows

3) Stable casing
- On Windows: normalize to the actual filesystem casing if available, otherwise lower-case.
- Recommended v0.1 rule: lower-case all paths to avoid case drift.
  (This can be revised later, but must be consistent.)

4) No trailing slashes for modules
- module path: "src/app", not "src/app/"

5) No redundant segments
- Remove "." segments
- Collapse ".." deterministically (or disallow roots that escape repo root)

## Stable ID Generation

Given a normalized path:
- file stable_id: "file:" + path
- module stable_id: "module:" + directory_path
- repo stable_id: "repo:root"

No UUIDs.
No random identifiers.

## Collisions

If two included files normalize to the same path (rare, but possible with case conflicts on Windows):
- Repo-runner must detect the collision and fail the run with an explicit error.
- No silent overwrites.

## Future Types (Reserved)

These are not used in v0.1, but reserved for later:
- symbol:{file_path}#{symbol_name}
- external:{package_name}
- edge IDs derived from endpoint IDs
```

### `C:/projects/repo-runner/documents/LANGUAGE_SUPPORT.md`

```md
# LANGUAGE_SUPPORT.md

# Language Support (v0.1)

In v0.1, language support is limited to extension-based detection for metadata only.

## Detection Rules

- language is derived from file extension.
- mapping is configured internally or via a simple mapping table.

Example mapping (illustrative):
- .ts, .tsx, .js, .jsx -> "typescript" or "javascript" (choose one policy and keep it consistent)
- .py -> "python"
- .rs -> "rust"
- .go -> "go"
- .java -> "java"
- .html -> "html"
- .css -> "css"
- .sql -> "sql"
- .toml -> "toml"
- .ps1 -> "powershell"
- .md -> "markdown"

## Policy

- Unknown extensions should be labeled "unknown" and may still be included if allowed by include_extensions.
- README inclusion is controlled separately by include_readme.

## Future (v0.2+)

Language adapters (AST parsing, imports, symbols) will be added later and specified in separate documents.
```

### `C:/projects/repo-runner/documents/REPO_LAYOUT.md`

```md
# REPO_LAYOUT.md

# Repository Layout (repo-runner)

This document defines the expected folder structure for the repo-runner repository itself. The goal is to keep specs stable, implementation modular, and outputs reproducible.

## Top-Level Layout

/
  README.md
  ARCHITECTURE.md
  SNAPSHOT_SPEC.md
  ID_SPEC.md
  CONFIG_SPEC.md
  DETERMINISM_RULES.md
  LANGUAGE_SUPPORT.md
  ROADMAP.md
  TESTING_STRATEGY.md
  VERSIONING_POLICY.md
  CONTRIBUTING.md
  REPO_LAYOUT.md

  src/
  tests/
  fixtures/
  scripts/
  dist/                (optional; build output if applicable)
  .gitignore
  LICENSE              (optional)

## Directory Purposes

### src/
Implementation code lives here.

Recommended internal modules (names are suggestions, not mandates):
- src/scanner/
- src/normalize/
- src/fingerprint/
- src/structure/
- src/snapshot/
- src/exporters/
- src/cli/

Rules:
- Keep phase boundaries clean.
- Do not mix exporters with canonical snapshot writing.

### tests/
Automated tests.

Suggested structure:
- tests/unit/
- tests/integration/
- tests/golden/

Golden tests should compare normalized outputs with snapshot_id/timestamp removed or ignored.

### fixtures/
Small, version-controlled fixture repos for testing.

Examples:
- fixtures/tiny_ts_repo/
- fixtures/mixed_repo/
- fixtures/windows_path_edgecases/

Rules:
- Fixtures must be small enough to run in CI quickly.
- Fixtures should include “annoying” cases (nested dirs, ignored dirs, mixed extensions).

### scripts/
Developer utilities and runner scripts.

Examples:
- scripts/run_fixture_tests.ps1
- scripts/run_fixture_tests.sh
- scripts/dev_snapshot.ps1

Rules:
- scripts/ must never be required for core functionality; they are convenience only.

### dist/ (optional)
Build artifacts if using a compiled language or bundler.

Rules:
- dist/ is never committed unless explicitly desired.
- dist/ should be ignored by git by default.

## Output Location Policy

Repo-runner should never write snapshots into its own repository by default.

Instead:
- Default output root should be user-specified, or
- A safe default like: {repo_root}/.repo-runner/ (for scanned repos), not the tool repo.

## Spec Discipline

All canonical contracts are the spec documents at repo root:
- SNAPSHOT_SPEC.md
- ID_SPEC.md
- CONFIG_SPEC.md
- DETERMINISM_RULES.md
- VERSIONING_POLICY.md

Implementation must follow specs. If implementation needs to change behavior, update specs first.

## Dennis Integration Boundary

Repo-runner is a standalone tool. Dennis consumes outputs.

Repo-runner must not:
- depend on Dennis code
- embed Dennis paths
- assume Dennis runtime environment beyond “local filesystem + CLI execution”

Dennis-specific orchestration belongs in Dennis.
```

### `C:/projects/repo-runner/documents/ROADMAP.md`

```md
# ROADMAP.md

# Roadmap

This roadmap is intentionally staged to preserve determinism and keep complexity layered.

## v0.1 — Structure + Fingerprints (Current)

- structure.json (repo/module/file containment)
- manifest.json (config + file hashes)
- append-only snapshots
- optional exports (flatten.md)

## v0.2 — Dependency Extraction (Imports Only)

- symbols.json (definitions optional)
- imports.json (file-to-file/module import edges)
- external_deps.json (package usage)
- stable external IDs

## v0.3 — Graph Canonicalization

- graph.json as the canonical structure:
  - nodes: repo/module/file/external
  - edges: contains/imports/depends_on
- cycle handling policy

## v0.4 — Diagram Projection

- draw.io export:
  - diagram.drawio
  - mxgraph.xml
- deterministic layout strategy

## v0.5 — Structural Artifacts

- per-node structural artifacts:
  - file artifact
  - module artifact
  - repo artifact
- still non-semantic, template-based

## v0.6+ — Optional LLM Layer (Dennis-Owned)

- semantic compression as a separate layer
- must not break determinism of structural substrate
```

### `C:/projects/repo-runner/documents/SNAPSHOT_SPEC.md`

```md
# SNAPSHOT_SPEC.md

# Snapshot Spec (v0.1)

This document defines the canonical snapshot format and on-disk layout.

## Output Root

Repo-runner writes into an output root directory (configurable). Within it, each run creates a new snapshot folder.

Example:

/repo-runner-output/
  /{snapshot_id}/
    manifest.json
    structure.json
    exports/
      ...
  current.json

## Snapshot Mode

Append-only snapshots are required.

- Every run creates a new `{snapshot_id}` folder.
- No run may overwrite an existing snapshot folder.
- `current.json` may be overwritten to point to the latest snapshot.

## snapshot_id Format

snapshot_id must be:
- Unique per run
- Safe as a folder name on Windows/macOS/Linux
- Deterministic *enough* to avoid collisions, but may include timestamp

Recommended format:

YYYY-MM-DDTHH-mm-ssZ_{short_hash}

Where `short_hash` is derived from:
- normalized roots
- config (ignore/ext/depth)
- optional git commit
- optional file list hash (if available after scan)

## manifest.json Schema

manifest.json describes:
- When the snapshot was made
- What inputs and config were used
- What files were included
- How to fingerprint and compare runs

Required fields:

{
  "schema_version": "1.0",
  "tool": {
    "name": "repo-runner",
    "version": "0.1.0"
  },
  "snapshot": {
    "snapshot_id": "...",
    "created_utc": "YYYY-MM-DDTHH:MM:SSZ",
    "output_root": "normalized path string"
  },
  "inputs": {
    "repo_root": "normalized path string",
    "roots": ["normalized path string", ...],
    "git": {
      "is_repo": true/false,
      "commit": "string or null"
    }
  },
  "config": {
    "depth": number,
    "ignore_names": ["node_modules", ".git", ...],
    "include_extensions": [".ts", ".tsx", ...],
    "include_readme": true/false,
    "tree_only": true/false
  },
  "stats": {
    "file_count": number,
    "total_bytes": number
  },
  "files": [
    {
      "stable_id": "file:src/app/page.tsx",
      "path": "src/app/page.tsx",
      "sha256": "hex string",
      "size_bytes": number,
      "language": "typescript"
    }
  ]
}

Rules:
- `files` must be sorted by `path` ascending.
- `sha256` must be computed from file bytes.
- `path` must follow normalization rules in ID_SPEC.md.

## structure.json Schema

structure.json is hierarchical containment only.

{
  "schema_version": "1.0",
  "repo": {
    "stable_id": "repo:root",
    "root": "repo-relative root (usually '.')",
    "modules": [
      {
        "stable_id": "module:src/app",
        "path": "src/app",
        "files": [
          "file:src/app/page.tsx",
          "file:src/app/layout.tsx"
        ]
      }
    ]
  }
}

Rules:
- `modules` sorted by `path` ascending.
- `files` entries sorted by their file path ascending.
- module membership is defined by directory containment of the file path.

## exports/ Folder

`exports/` is optional.

Anything in `exports/`:
- Must be derivable from the canonical snapshot
- Must be safe to delete and regenerate
- Must not be used as a source of truth

## current.json

Optional pointer for convenience:

{
  "schema_version": "1.0",
  "current_snapshot_id": "{snapshot_id}",
  "path": "{snapshot_id}"
}

Overwriting current.json is allowed.

## Snapshot Resolution Policy

When invoked without explicit snapshot_id:
- Repo-runner or its consumer may default to current.json pointer.

If snapshot_id is provided:
- The specified snapshot folder must exist.
- If not found, fail explicitly.

Snapshot resolution does not mutate snapshots.
```

### `C:/projects/repo-runner/documents/TESTING_STRATEGY.md`

```md
# TESTING_STRATEGY.md

# Testing Strategy (v0.1)

Repo-runner must prove determinism and correctness under realistic repo conditions.

## Test Categories

### 1) Golden Snapshot Tests
- Run repo-runner on a small fixture repo.
- Store expected `structure.json` and `manifest.json` (excluding snapshot_id and timestamp).
- Compare normalized outputs.

### 2) Determinism Re-run Tests
- Run twice on the same fixture with identical config.
- Assert:
  - file list is identical
  - module grouping identical
  - sha256 hashes identical
  - ordering identical

### 3) Drift Detection Tests
- Modify one file byte.
- Assert only that file’s sha256 changes, and totals adjust accordingly.

### 4) Ignore Rule Tests
- Ensure ignored directories are never traversed.
- Ensure ignore list is name-based and deterministic.

### 5) Path Normalization Tests
- Windows-style input paths normalize to repo-relative forward slash format.
- Case normalization policy is enforced consistently.

### 6) Collision Tests
- Simulate two inputs that normalize to the same path.
- Assert hard failure.

## Performance Smoke Test (Non-Blocking v0.1)
- Run on a medium repo (tens of thousands of files).
- Confirm completion and stable output.
- No optimization requirements yet.

## CI Recommendation
- Run fixture tests on:
  - Windows
  - Linux
to catch path normalization and separator issues early.
```

### `C:/projects/repo-runner/documents/VERSIONING_POLICY.md`

```md
# VERSIONING_POLICY.md

# Versioning Policy

Repo-runner uses semantic versioning: MAJOR.MINOR.PATCH.

Because Dennis will consume repo-runner outputs, output compatibility matters.

## MAJOR Version Bump (Breaking)

Any of the following requires a MAJOR bump:
- Changes to stable ID formats
- Changes to path normalization policy
- Changes to snapshot folder contract
- Changes to manifest.json or structure.json schema that are not backward compatible
- Removal/renaming of required fields

## MINOR Version Bump (Backward-Compatible Additions)

Any of the following requires a MINOR bump:
- Adding new optional fields to manifest/structure
- Adding new exporters
- Adding new CLI flags that do not change defaults
- Adding new language detection mappings (if it doesn’t alter existing labels)

## PATCH Version Bump (Fixes Only)

Any of the following requires a PATCH bump:
- Bug fixes that restore intended determinism
- Documentation corrections
- Performance improvements that do not change outputs

## Schema Versioning

Both manifest.json and structure.json include `schema_version`.
- If schema changes in a backward-compatible way: increment MINOR in schema_version (e.g., 1.1)
- If schema changes incompatibly: increment MAJOR in schema_version (e.g., 2.0)

Tool version and schema_version are related but distinct.
```

### `C:/projects/repo-runner/src/__init__.py`

```py

```

### `C:/projects/repo-runner/src/cli/__init__.py`

```py

```

### `C:/projects/repo-runner/src/cli/main.py`

```py
import argparse
import os
from typing import List, Optional

from src.exporters.flatten_markdown_exporter import (
    FlattenMarkdownExporter,
    FlattenOptions,
)
from src.fingerprint.file_fingerprint import FileFingerprint
from src.normalize.path_normalizer import PathNormalizer
from src.scanner.filesystem_scanner import FileSystemScanner
from src.snapshot.snapshot_loader import SnapshotLoader
from src.snapshot.snapshot_writer import SnapshotWriter
from src.structure.structure_builder import StructureBuilder


def _parse_args():
    parser = argparse.ArgumentParser(prog="repo-runner", description="repo-runner v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    # snapshot
    snap = sub.add_parser("snapshot", help="Create a deterministic structural snapshot")
    snap.add_argument("repo_root", help="Repository root path")
    snap.add_argument("--output-root", required=True, help="Output root directory for snapshots")
    snap.add_argument("--depth", type=int, default=25)
    snap.add_argument(
        "--ignore",
        nargs="*",
        default=[".git", "node_modules", "__pycache__", "dist", "build", ".next", ".expo", ".venv"],
    )
    snap.add_argument("--include-extensions", nargs="*", default=[])
    snap.add_argument("--include-readme", action="store_true", default=True)
    snap.add_argument("--no-include-readme", action="store_false", dest="include_readme")
    snap.add_argument("--write-current-pointer", action="store_true", default=True)
    snap.add_argument("--no-write-current-pointer", action="store_false", dest="write_current_pointer")

    # export
    exp = sub.add_parser("export", help="Export derived artifacts from a snapshot")
    exp_sub = exp.add_subparsers(dest="export_command", required=True)

    flatten = exp_sub.add_parser(
        "flatten",
        help="Generate deterministic flatten markdown (list_tree alternative)",
    )
    flatten.add_argument("--output-root", required=True, help="Output root directory where snapshots live")
    flatten.add_argument(
        "--snapshot-id",
        required=False,
        default=None,
        help="Snapshot id to export from (defaults to current)",
    )
    flatten.add_argument("--repo-root", required=True, help="Repo root path (used to read file contents)")
    flatten.add_argument(
        "--output",
        required=False,
        default=None,
        help="Output path for markdown (defaults to snapshot exports/flatten.md)",
    )
    flatten.add_argument("--tree-only", action="store_true", default=False)
    flatten.add_argument("--include-readme", action="store_true", default=True)
    flatten.add_argument("--no-include-readme", action="store_false", dest="include_readme")
    flatten.add_argument("--scope", required=False, default="full")
    flatten.add_argument("--title", required=False, default=None)

    return parser.parse_args()


def _filter_by_extensions(abs_files: List[str], include_exts: List[str]) -> List[str]:
    if not include_exts:
        return abs_files

    include = set([e.lower() for e in include_exts])
    out = []

    for p in abs_files:
        ext = os.path.splitext(p)[1].lower()
        if ext in include:
            out.append(p)

    return out


def run_snapshot(
    repo_root: str,
    output_root: str,
    depth: int,
    ignore: List[str],
    include_extensions: List[str],
    include_readme: bool,
    write_current_pointer: bool,
) -> str:
    repo_root_abs = os.path.abspath(repo_root)

    scanner = FileSystemScanner(depth=depth, ignore_names=set(ignore))
    absolute_files = scanner.scan([repo_root_abs])
    absolute_files = _filter_by_extensions(absolute_files, include_extensions)

    normalizer = PathNormalizer(repo_root_abs)
    file_entries = []
    total_bytes = 0
    seen_ids = set()

    for abs_path in absolute_files:
        normalized = normalizer.normalize(abs_path)

        if not include_readme and os.path.basename(normalized).lower().startswith("readme"):
            continue

        stable_id = normalizer.file_id(normalized)

        if stable_id in seen_ids:
            raise RuntimeError(f"Path collision after normalization: {stable_id}")

        seen_ids.add(stable_id)

        module_path = normalizer.module_path(normalized)
        fp = FileFingerprint.fingerprint(abs_path)
        total_bytes += fp["size_bytes"]

        file_entries.append(
            {
                "stable_id": stable_id,
                "path": normalized,
                "module_path": module_path,
                **fp,
            }
        )

    file_entries = sorted(file_entries, key=lambda x: x["path"])

    structure = StructureBuilder().build(
        repo_id=PathNormalizer.repo_id(),
        files=file_entries,
    )

    manifest = {
        "schema_version": "1.0",
        "tool": {"name": "repo-runner", "version": "0.1.0"},
        "inputs": {
            "repo_root": repo_root_abs.replace("\\", "/"),
            "roots": [repo_root_abs.replace("\\", "/")],
            "git": {
                "is_repo": os.path.isdir(os.path.join(repo_root_abs, ".git")),
                "commit": None,
            },
        },
        "config": {
            "depth": depth,
            "ignore_names": ignore,
            "include_extensions": include_extensions,
            "include_readme": include_readme,
            "tree_only": False,
        },
        "stats": {
            "file_count": len(file_entries),
            "total_bytes": total_bytes,
        },
        "files": file_entries,
    }

    writer = SnapshotWriter(output_root)
    snapshot_id = writer.write(
        manifest,
        structure,
        write_current_pointer=write_current_pointer,
    )

    return snapshot_id


def run_export_flatten(
    output_root: str,
    repo_root: str,
    snapshot_id: Optional[str],
    output_path: Optional[str],
    tree_only: bool,
    include_readme: bool,
    scope: str,
    title: Optional[str],
) -> str:
    loader = SnapshotLoader(output_root)
    snapshot_dir = loader.resolve_snapshot_dir(snapshot_id)
    manifest = loader.load_manifest(snapshot_dir)

    exporter = FlattenMarkdownExporter()

    options = FlattenOptions(
        tree_only=tree_only,
        include_readme=include_readme,
        scope=scope,
    )

    return exporter.export(
        repo_root=os.path.abspath(repo_root),
        snapshot_dir=snapshot_dir,
        manifest=manifest,
        output_path=output_path,
        options=options,
        title=title,
    )


def main():
    args = _parse_args()

    if args.command == "snapshot":
        snap_id = run_snapshot(
            repo_root=args.repo_root,
            output_root=args.output_root,
            depth=args.depth,
            ignore=args.ignore,
            include_extensions=args.include_extensions,
            include_readme=args.include_readme,
            write_current_pointer=args.write_current_pointer,
        )
        print(f"Snapshot created: {snap_id}")
        return

    if args.command == "export" and args.export_command == "flatten":
        out = run_export_flatten(
            output_root=args.output_root,
            repo_root=args.repo_root,
            snapshot_id=args.snapshot_id,
            output_path=args.output,
            tree_only=args.tree_only,
            include_readme=args.include_readme,
            scope=args.scope,
            title=args.title,
        )
        print(f"Wrote: {out}")
        return

    raise RuntimeError("Unhandled command")


if __name__ == "__main__":
    main()
```

### `C:/projects/repo-runner/src/exporters/flatten_markdown_exporter.py`

```py
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class FlattenOptions:
    tree_only: bool
    include_readme: bool
    scope: str  # full | module:<path> | file:<path> | list:<a,b,c> | prefix:<path>


class FlattenMarkdownExporter:
    TEXT_EXTENSIONS = {
        ".ts", ".tsx", ".js", ".jsx",
        ".py", ".rs", ".go", ".java",
        ".json", ".md", ".txt",
        ".html", ".css", ".sql", ".toml",
        ".ps1", ".ejs", ".yml", ".yaml",
        ".env", ".example", ".gitignore",
        ".d.ts",
    }

    def export(
        self,
        repo_root: str,
        snapshot_dir: str,
        manifest: Dict,
        output_path: Optional[str],
        options: FlattenOptions,
        title: Optional[str] = None,
    ) -> str:

        files = self._canonical_files_from_manifest(manifest, options)
        tree_md = self._render_tree([f["path"] for f in files])
        content_md = "" if options.tree_only else self._render_contents(repo_root, files)

        header = [
            f"# {title or 'repo-runner flatten export'}",
            "",
            f"- repo_root: `{repo_root}`",
            f"- snapshot_dir: `{snapshot_dir}`",
            f"- file_count: `{len(files)}`",
            f"- scope: `{options.scope}`",
            f"- tree_only: `{options.tree_only}`",
            "",
        ]

        final_md = "\n".join(header) + tree_md + ("\n" + content_md if content_md else "")

        if output_path is None:
            exports_dir = os.path.join(snapshot_dir, "exports")
            os.makedirs(exports_dir, exist_ok=True)
            output_path = os.path.join(exports_dir, "flatten.md")

        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(final_md)

        return output_path

    def _canonical_files_from_manifest(self, manifest: Dict, options: FlattenOptions) -> List[Dict]:
        files = manifest.get("files", [])
        entries = []

        for entry in files:
            path = entry["path"]

            if not options.include_readme and path.lower().startswith("readme"):
                continue

            entries.append(entry)

        scoped = self._apply_scope(entries, options.scope)

        scoped.sort(key=lambda x: x["path"])
        return scoped

    def _apply_scope(self, entries: List[Dict], scope: str) -> List[Dict]:
        if scope == "full":
            return list(entries)

        if scope.startswith("module:"):
            prefix = scope.split("module:", 1)[1].rstrip("/")
            return [e for e in entries if e["path"].startswith(prefix + "/")]

        if scope.startswith("prefix:"):
            prefix = scope.split("prefix:", 1)[1]
            return [e for e in entries if e["path"].startswith(prefix)]

        if scope.startswith("file:"):
            target = scope.split("file:", 1)[1]
            return [e for e in entries if e["path"] == target]

        if scope.startswith("list:"):
            raw = scope.split("list:", 1)[1]
            targets = [t.strip() for t in raw.split(",") if t.strip()]
            target_set = set(targets)
            return [e for e in entries if e["path"] in target_set]

        raise ValueError(f"Invalid scope: {scope}")

    def _render_tree(self, paths: List[str]) -> str:
        root = {}
        for p in paths:
            parts = [x for x in p.split("/") if x]
            node = root
            for part in parts:
                node = node.setdefault(part, {})

        lines = ["## Tree", "", "```"]
        lines.extend(self._tree_lines(root, ""))
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def _tree_lines(self, node: Dict, prefix: str) -> List[str]:
        keys = sorted(node.keys())
        lines = []
        for i, key in enumerate(keys):
            is_last = i == len(keys) - 1
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + key)
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(self._tree_lines(node[key], child_prefix))
        return lines

    def _render_contents(self, repo_root: str, files: List[Dict]) -> str:
        blocks = ["## File Contents", ""]
        for entry in files:
            path = entry["path"]
            abs_path = os.path.join(repo_root, path.replace("/", os.sep))

            blocks.append(f"### `{path}`")
            blocks.append("")

            ext = os.path.splitext(path)[1].lower()

            if ext not in self.TEXT_EXTENSIONS or self._sniff_binary(abs_path):
                blocks.append(self._binary_placeholder(entry))
                blocks.append("")
                continue

            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except OSError as e:
                content = f"<<ERROR: {e}>>"

            blocks.append(f"```")
            blocks.append(content.rstrip("\n"))
            blocks.append("```")
            blocks.append("")

        return "\n".join(blocks)

    @staticmethod
    def _sniff_binary(abs_path: str) -> bool:
        try:
            with open(abs_path, "rb") as f:
                chunk = f.read(4096)
        except OSError:
            return False
        return b"\x00" in chunk

    @staticmethod
    def _binary_placeholder(entry: Dict) -> str:
        return "\n".join([
            "```",
            "<<BINARY_OR_SKIPPED_FILE>>",
            f"size_bytes: {entry.get('size_bytes')}",
            f"sha256: {entry.get('sha256')}",
            "```",
        ])
```

### `C:/projects/repo-runner/src/fingerprint/file_fingerprint.py`

```py
import hashlib
import os
from typing import Dict


class FileFingerprint:
    LANGUAGE_MAP = {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".toml": "toml",
        ".ps1": "powershell",
        ".md": "markdown",
        ".json": "json",
    }

    @staticmethod
    def fingerprint(path: str) -> Dict:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)

        size = os.path.getsize(path)
        ext = os.path.splitext(path)[1].lower()
        language = FileFingerprint.LANGUAGE_MAP.get(ext, "unknown")

        return {
            "sha256": sha.hexdigest(),
            "size_bytes": size,
            "language": language,
        }
```

### `C:/projects/repo-runner/src/normalize/path_normalizer.py`

```py
import os


class PathNormalizer:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    def normalize(self, absolute_path: str) -> str:
        relative = os.path.relpath(absolute_path, self.repo_root)

        # Normalize separators first.
        normalized = relative.replace("\\", "/")

        # Only strip a literal "./" prefix (do NOT strip leading dots from names like ".context-docs").
        if normalized.startswith("./"):
            normalized = normalized[2:]

        # Normalize any accidental leading slashes (defensive; relpath shouldn't produce these).
        while normalized.startswith("/"):
            normalized = normalized[1:]

        return normalized.lower()

    def module_path(self, file_path: str) -> str:
        directory = os.path.dirname(file_path)
        return directory.replace("\\", "/")

    @staticmethod
    def file_id(normalized_path: str) -> str:
        return f"file:{normalized_path}"

    @staticmethod
    def module_id(module_path: str) -> str:
        return f"module:{module_path}"

    @staticmethod
    def repo_id() -> str:
        return "repo:root"
```

### `C:/projects/repo-runner/src/scanner/filesystem_scanner.py`

```py
import os
from typing import List, Set


class FileSystemScanner:
    def __init__(self, depth: int, ignore_names: Set[str]):
        self.depth = depth
        self.ignore_names = ignore_names

    def scan(self, root_paths: List[str]) -> List[str]:
        all_files = []

        for root in root_paths:
            if os.path.isfile(root):
                all_files.append(os.path.abspath(root))
                continue

            root = os.path.abspath(root)
            all_files.extend(self._walk(root, current_depth=0))

        return sorted(all_files)

    def _walk(self, directory: str, current_depth: int) -> List[str]:
        if self.depth >= 0 and current_depth > self.depth:
            return []

        results = []

        try:
            entries = sorted(os.listdir(directory))
        except OSError:
            return []

        for entry in entries:
            if entry in self.ignore_names:
                continue

            full_path = os.path.join(directory, entry)

            if os.path.isdir(full_path):
                results.extend(self._walk(full_path, current_depth + 1))
            elif os.path.isfile(full_path):
                results.append(os.path.abspath(full_path))

        return results
```

### `C:/projects/repo-runner/src/snapshot/snapshot_loader.py`

```py
import json
import os
from typing import Optional


class SnapshotLoader:
    def __init__(self, output_root: str):
        self.output_root = output_root

    def resolve_snapshot_dir(self, snapshot_id: Optional[str]) -> str:
        if snapshot_id:
            snapshot_dir = os.path.join(self.output_root, snapshot_id)
            if not os.path.isdir(snapshot_dir):
                raise FileNotFoundError(f"Snapshot not found: {snapshot_dir}")
            return snapshot_dir

        current_path = os.path.join(self.output_root, "current.json")
        if not os.path.isfile(current_path):
            raise FileNotFoundError(
                f"current.json not found at output root: {current_path}. "
                "Run `repo-runner snapshot ...` first or pass --snapshot-id."
            )

        with open(current_path, "r", encoding="utf-8") as f:
            current = json.load(f)

        snapshot_id = current.get("current_snapshot_id")
        if not snapshot_id:
            raise ValueError("current.json missing required field: current_snapshot_id")

        snapshot_dir = os.path.join(self.output_root, snapshot_id)
        if not os.path.isdir(snapshot_dir):
            raise FileNotFoundError(f"Snapshot dir referenced by current.json not found: {snapshot_dir}")

        return snapshot_dir

    @staticmethod
    def load_manifest(snapshot_dir: str) -> dict:
        path = os.path.join(snapshot_dir, "manifest.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_structure(snapshot_dir: str) -> dict:
        path = os.path.join(snapshot_dir, "structure.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
```

### `C:/projects/repo-runner/src/snapshot/snapshot_writer.py`

```py
import json
import os
from datetime import datetime
from typing import Dict, Optional


class SnapshotWriter:
    def __init__(self, output_root: str):
        self.output_root = output_root

    def write(
        self,
        manifest: Dict,
        structure: Dict,
        snapshot_id: Optional[str] = None,
        write_current_pointer: bool = True,
    ) -> str:
        os.makedirs(self.output_root, exist_ok=True)

        if snapshot_id is None:
            # v0.1: timestamp-based id; future: append short_hash as per SNAPSHOT_SPEC
            snapshot_id = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")

        snapshot_dir = os.path.join(self.output_root, snapshot_id)
        if os.path.exists(snapshot_dir):
            raise RuntimeError(f"Snapshot directory already exists: {snapshot_dir}")

        os.makedirs(snapshot_dir, exist_ok=False)
        os.makedirs(os.path.join(snapshot_dir, "exports"), exist_ok=True)

        # Ensure manifest has snapshot metadata (non-breaking additive)
        manifest = dict(manifest)
        manifest.setdefault("snapshot", {})
        manifest["snapshot"] = dict(manifest["snapshot"])
        manifest["snapshot"].setdefault("snapshot_id", snapshot_id)
        manifest["snapshot"].setdefault("created_utc", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        manifest["snapshot"].setdefault("output_root", self.output_root)

        with open(os.path.join(snapshot_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)

        with open(os.path.join(snapshot_dir, "structure.json"), "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=2, sort_keys=True)

        if write_current_pointer:
            current_path = os.path.join(self.output_root, "current.json")
            with open(current_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "schema_version": "1.0",
                        "current_snapshot_id": snapshot_id,
                        "path": snapshot_id,
                    },
                    f,
                    indent=2,
                    sort_keys=True,
                )

        return snapshot_id
```

### `C:/projects/repo-runner/src/structure/structure_builder.py`

```py
from collections import defaultdict
from typing import Dict, List


class StructureBuilder:
    def build(self, repo_id: str, files: List[Dict]) -> Dict:
        modules = defaultdict(list)

        for file_entry in files:
            module_path = file_entry["module_path"]
            modules[module_path].append(file_entry["stable_id"])

        sorted_modules = sorted(modules.keys())

        module_entries = []
        for module in sorted_modules:
            module_entries.append({
                "stable_id": f"module:{module}",
                "path": module,
                "files": sorted(modules[module])
            })

        return {
            "schema_version": "1.0",
            "repo": {
                "stable_id": repo_id,
                "root": ".",
                "modules": module_entries
            }
        }
```

