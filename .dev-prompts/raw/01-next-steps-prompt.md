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