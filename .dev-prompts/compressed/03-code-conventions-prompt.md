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

4. Please provide a concise, single-line git commit -m message summarizing all changes in this response, utilizing the feat/fix nomenclature and formatted as a single command for easy copy-pasting."
---

## Tone & Assumptions

- Write as a senior engineer implementing changes in a production system.
- Assume another senior engineer will review and run the code.
- Be exact, boring, and correct.
- No motivational language. No speculation. No hand-waving.

NOTE: ensure that the file titles are right above the implemented code. not in the actual codeblock, though. just a title before the codeblock.

> **Codebase Context: Testing Regiment**
>
> We use a strict **Pytest** setup.
> 1.  **Structure:** Tests live in `tests/unit` and `tests/integration`.
> 2.  **Config:** Configuration is in `pytest.ini`. Do not modify `sys.path` manually.
> 3.  **Fixtures:** Use `tests/conftest.py` for all file ops. **Never** write to the real disk; use the `temp_repo_root` fixture.
> 4.  **Performance:** The suite currently runs in **1.6s**. Do not introduce slow tests or sleeps.
> 5.  **Validation:** Run `scripts/verify.ps1` to prove your code works.
>
> **Current State:** v0.2, All 63 tests passing.

