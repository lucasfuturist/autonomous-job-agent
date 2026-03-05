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