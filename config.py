# config.py
OLLAMA_MODEL = "qwen:14b"
PORT = 8050

# --- PATHS ---
MD_FOLDER = "data/output_mds"
PDF_FOLDER = "data/input_pdfs"
DB_FILE = "data/targets.db"
JSON_FEED = "data/dashboard.json"
MISSIONS_FEED = "data/missions.json"
STATUS_FEED = "data/status.json"
HTML_FILE = "mission_control.html"

# --- SCHEMA FIRST APPROACH ---
INITIAL_SEARCH_TERMS = [] 
LOCATIONS = ["Boston, MA", "USA", "Remote"]

# The Absolute Boundaries of the Agent's Universe
CORE_SCHEMA = [
    "Artificial Intelligence", 
    "Robotics", 
    "Machine Learning", 
    "Edge Computing", 
    "Hardware Engineering", 
    "New Product Introduction (NPI)",
    "Autonomous Systems"
]

# --- PERFORMANCE & MODES ---
MIN_SCORE = 7            # The minimum LLM score required to deploy a resume
SWEEP_DEPTH = 100        # Exhaustive search: Pull up to 100 jobs per term per location
NUM_ANALYSTS = 2         # Dual-thread LLM evaluation
MAX_QUEUE_DEPTH = 50     # If queue > 50, Hunter sleeps (Matching Mode)