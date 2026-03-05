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