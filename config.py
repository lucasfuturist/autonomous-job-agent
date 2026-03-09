# config.py
import re

# --- MULTI-AGENT INTELLIGENCE CORE ---
OLLAMA_MODEL = "qwen:14b"             
HEAVY_MODEL = "qwen2.5:32b"          
PORT = 8050

# --- PATHS ---
MD_FOLDER = "data/output_mds"
PDF_FOLDER = "data/input_pdfs"
DB_FILE = "data/targets.db"
JSON_FEED = "data/dashboard.json"
MISSIONS_FEED = "data/missions.json"
STATUS_FEED = "data/status.json"
HTML_FILE = "mission_control.html"

# --- SWEEP VECTORS ---
INITIAL_SEARCH_TERMS = [
    # CORE MATERIALS & R&D
    "Materials Scientist", "Materials Engineer", "R&D Materials Scientist", 
    "Failure Analysis Engineer", "Ceramic Engineer", "Metallurgy Engineer",
    "Materials Characterization", "Process Development Engineer", 
    "Thin Film Engineer", "Composite Materials Engineer", 
    "Semiconductor Materials Engineer", "Battery Materials Engineer",
    
    # COMPUTATIONAL & INFORMATICS
    "Computational Materials Scientist", "Materials Informatics Engineer", 
    "Materials Data Scientist", "Multiphysics Simulation Engineer",
    
    # ADVANCED MANUFACTURING & HARDWARE
    "Surface Engineer", "Nanotechnology Engineer", "Device Fabrication Engineer",
    "Metrology Engineer", "Thermal Process Engineer", "Hardware Materials Engineer"
]
LOCATIONS = ["Boston, MA", "Massachusetts", "Remote"]

# --- SMART HEURISTICS (REGEX BASED) ---
TITLE_BLACKLIST = [
    r"\bintern\b", r"\binternship\b", r"\bco-op\b", r"\bcoop\b", r"\bstudent\b", 
    r"\bundergraduate\b", r"\bvolunteer\b", r"\bunpaid\b", r"\bpart-time\b",
    
    r"\bphysician\b", r"\bnurse\b", r"\bclinical\b", r"\bpatient\b", r"\btherapist\b", 
    r"\bsurgeon\b", r"\bveterinary\b", r"\bpharmacy\b", r"\bpsychologist\b", r"\bcounselor\b",
    r"\bdentist\b", r"\bmedical assistant\b",
    
    r"\bsales\b", r"\baccount executive\b", r"\bmarketing\b", r"\brecruiter\b", 
    r"\bhr\b", r"\bhuman resources\b", r"\bsecretary\b", r"\bclerk\b", r"\bdriver\b", 
    r"\bwarehouse\b", r"\bcustomer service\b", r"\bmerchandising\b",
    
    r"\bmechanic\b", r"\belectrician\b", r"\bplumber\b", r"\bhvac\b", r"\bwelder\b"
]

COMPANY_BLACKLIST = [
    r"\bcybercoders\b", r"\brevature\b", r"\bcannon search\b", r"\bjobot\b", r"\bbairesdev\b"
]

ALLOWLIST_OVERRIDES = [
    r"\bsoftware\b", r"\bengineer\b", r"\bdeveloper\b", r"\bsystems\b", r"\bdata\b", 
    r"\brobotics\b", r"\bai\b", r"\bmachine learning\b", r"\barchitect\b"
]

USER_PREFERENCES = """
NEGATIVE CONSTRAINTS (Reject or Score Low):
- PURE SOFTWARE/IT: Web dev, Helpdesk, SysAdmin, generic frontend.
- MEDICAL/CLINICAL: Any role involving patient care or hospital admin.
POSITIVE CONSTRAINTS (Score High):
- Physical hardware, R&D, materials characterization, failure analysis, ceramics, thermodynamics, or computational materials.
"""

# --- PERFORMANCE & DYNAMIC PAGINATION ---
MIN_SCORE = 5            
SWEEP_BATCH_SIZE = 100        
MIN_YIELD_THRESHOLD = 0.05   # Hunter will keep paginating until novel job yield drops below 10%
NUM_ANALYSTS = 3         
MAX_QUEUE_DEPTH = 50     

MAX_COMMUTE_MILES = 50.0  # Max distance from Home Coords. -1.0 means remote is allowed.