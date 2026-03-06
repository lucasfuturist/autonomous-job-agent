# Autonomous Job Agent (SYSTEM CNS)

A fully local, multi-agent AI system designed to autonomously scout, score, and prepare highly-tailored application assets for deep tech, robotics, and systems engineering roles. 

Built entirely on local LLMs (Ollama) and an embedded SQLite architecture, this agent operates 24/7 without cloud API costs or data privacy risks.

---

## 🧠 System Architecture

The Central Nervous System (`cns.py`) utilizes a Producer-Consumer threading model with distinct agent personas:

*   **The Hunter (Ingestion):** Continuously paginates through LinkedIn and Indeed using dynamic yield logic. It sweeps through a configurable master list of 200+ technical search vectors, automatically stopping when the yield of novel jobs drops below 10%.
*   **The Geofencer (Navigation):** Calculates exact Haversine distances for every scraped job against a home coordinate (Boston, MA). Utilizes a rate-limited, locally-cached Nominatim integration to filter out jobs beyond a strict 50-mile radius (unless fully remote).
*   **The Scout (Triage):** Powered by `qwen:14b`. Reads job descriptions at high speed, applying strict heuristic constraints to ruthlessly reject irrelevant roles (e.g., medical, IT support, pure frontend) and scores valid targets from 1-10.
*   **The Sniper (Asset Generation):** Powered by `qwen2.5:32b`. Triggered only for high-scoring jobs (Score 8+). It cross-references the job description against a master JSON vault of your career history (`master_career_data.json`). It dynamically selects relevant bullet points, rewrites the summary in narrative prose, and prunes your skills list to match the exact role—guaranteeing zero LLM hallucination.

## 🚀 Key Features

*   **Just-In-Time (JIT) PDF Resumes:** Automatically compiles bespoke Markdown resumes into professionally styled, clickable PDFs for every single high-value target.
*   **Anti-Gap Guarantee:** Programmatically ensures your current employment is always injected into generated resumes to prevent ATS red flags.
*   **React War Room (UI):** A local dashboard (`localhost:5173` -> `localhost:8050` API) to monitor the agent's live feed, review AI tactical analysis, edit resumes on the fly, and manage a Kanban board of applications.
*   **Total Privacy:** No OpenAI, no Anthropic. Your data and the agent's logic never leave your machine.

---

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **Node.js 18+** (For the React Frontend)
3.  **Ollama** installed and running locally.

### Required Models
You must pull the following Ollama models before booting the agent:
```bash
ollama pull qwen:14b
ollama pull qwen2.5:32b
```

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/autonomous-job-agent.git
   cd autonomous-job-agent
   ```

2. **Install Python Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   # Ensure you have the PDF generation libs:
   pip install markdown2 xhtml2pdf pandas jobspy
   ```

3. **Install React Frontend Dependencies:**
   ```bash
   cd web
   npm install
   ```

4. **Configure the Vault:**
   * Open `data/master_career_data.json`.
   * Populate your skills, past roles, bullet points, and education. This is the absolute ground truth the LLM uses to generate assets.

---

## 🕹️ Usage

**1. Boot the Agent & API Server**
Open a terminal in the root directory and run:
```bash
python cns.py
```
*This starts the threaded API server on port 8050, boots the Hunter to start scraping, and spins up 3 Analyst threads to begin scoring.*

**2. Boot the Dashboard UI**
Open a second terminal, navigate to the `web/` folder, and start Vite:
```bash
cd web
npm run dev
```
*Open `http://localhost:5173` in your browser to view the Command Profile.*

---

## 🧰 Utility Scripts Index

As the system processes thousands of jobs, schema upgrades or prompt tweaks may require backfilling old data. Use these standalone scripts to modify history without burning LLM tokens or scraping again:

*   **`clean_data.py`**: Wipes the SQLite database, clears the agenda queue, and resets the agent to factory zero.
*   **`export_logs.py`**: Dumps the complete history of every search term, timestamp, and yield count to a CSV (`data/mission_history.csv`).
*   **`rebuild_pdfs.py`**: Iterates over all generated Markdown resumes and recompiles them into PDFs (Useful if you change the CSS styling in `server.py`).
*   **`rebuild_summaries.py`**: Re-runs the LLM *only* on the Professional Summary section of existing resumes to fix tense or grammar issues, preserving the rest of the document.
*   **`rebuild_skill_titles.py`**: A fast string-replacement script to fix capitalization typos in the Markdown skills section.
*   **`rebuild_missing_stealth.py`**: Scans old resumes and forcefully injects your current/latest job if the LLM accidentally pruned it.
*   **`migrate_db_filenames.py`**: Syncs the SQLite database pointers if you batch-renamed files on your hard drive.
*   **`reweigh_queue.py`**: Re-evaluates all "Pending" and "Target" jobs against updated dynamic rules (Triggered via the UI "Rescore" button).

---

## 📂 Directory Structure

```text
autonomous-job-agent/
├── cns.py                      # Main entry point (Agent Threads)
├── config.py                   # Master settings, search terms, heuristics
├── tools/
│   ├── brain.py                # Ollama LLM integration & prompt logic
│   ├── memory.py               # SQLite database & Geocoding logic
│   ├── senses.py               # JobSpy scraping & pagination loop
│   └── server.py               # Native Python HTTP API & PDF compiler
├── data/
│   ├── master_career_data.json # The Candidate "Vault"
│   ├── targets.db              # Auto-generated SQLite DB
│   ├── output_mds/             # Auto-generated Markdown resumes
│   └── deployments/            # Auto-generated PDF resumes
├── web/                        # React Frontend
│   ├── src/
│   │   ├── pages/              # Dashboard, War Room, Profile
│   │   └── components/         # Job Cards, Modals
│   └── package.json
└── [utility_scripts].py        # Maintenance scripts
```
```

### 3. Verification Steps

1.  **View the File:**
    *   Open `README.md` in your editor or IDE (VS Code has a built-in Markdown preview).
    *   Verify the formatting, commands, and architecture descriptions are accurate to what we just built.

### 4. Git Commit Command

```bash
git commit -m "docs: generate comprehensive README detailing system architecture, setup instructions, and utility script index"
```