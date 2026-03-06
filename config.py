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
    # --- ZONE 1: AI, LLMs & DATA INFRASTRUCTURE ---
    "AI Systems Engineer", "LLM Infrastructure Engineer", "RAG Engineer", "Generative AI Engineer",
    "AI Platform Engineer", "MLOps Engineer", "Applied AI Scientist", "AI Architect",
    "Prompt Engineer", "AI Orchestration Engineer", "Vector Search Engineer", "Semantic Search Engineer",
    "AI Compliance Engineer", "AI Safety Engineer", "Machine Learning Systems Engineer", "Agentic AI Engineer",
    "NLP Systems Engineer", "AI Validation Engineer", "Cognitive Systems Engineer", "Data Pipeline Engineer",

    # --- ZONE 2: BACKEND, SYSTEMS & PLATFORM ARCHITECTURE ---
    "Founding Systems Engineer", "Backend Infrastructure Engineer", "Distributed Systems Engineer",
    "Data Ingestion Engineer", "Platform Infrastructure Engineer", "Database Systems Engineer",
    "Backend Architecture Engineer", "Systems Integration Engineer", "CI/CD Pipeline Engineer",
    "Infrastructure Automation Engineer", "Site Reliability Engineer", "Cloud Infrastructure Engineer",
    "DevOps Automation Engineer", "Backend Python Engineer", "Deterministic Systems Engineer",
    "Enterprise Systems Architect", "Scalability Engineer", "High Performance Computing Engineer",
    "Backend Software Architect", "Software Systems Engineer",

    # --- ZONE 3: ROBOTICS, AUTONOMY & EDGE COMPUTING ---
    "Robotics Autonomy Engineer", "Motion Planning Engineer", "Computer Vision Engineer", "Robotic Systems Engineer",
    "SLAM Engineer", "Perception Engineer", "Sensor Fusion Engineer", "Edge Computing Engineer",
    "Edge AI Engineer", "Autonomous Vehicles Engineer", "Mechatronics Software Engineer", "Robotics Integration Engineer",
    "Field Robotics Engineer", "Robotics Deployment Engineer", "C++ Robotics Engineer", "Embedded Vision Engineer",
    "Navigation Systems Engineer", "Mobile Robotics Engineer", "Industrial Robotics Engineer", "Robotics Infrastructure Engineer",

    # --- ZONE 4: MATERIALS CHARACTERIZATION & R&D ---
    "Materials Characterization Engineer", "Thin Film Engineer", "Process Development Engineer", "R&D Materials Scientist",
    "Failure Analysis Engineer", "Ceramic Engineer", "Metallurgy Engineer", "Microscopy Engineer",
    "SEM Specialist", "Materials Testing Engineer", "Thermal Process Engineer", "Materials Formulation Engineer",
    "Process Integration Engineer", "Sputtering Process Engineer", "Yield Enhancement Engineer",
    "Manufacturing Process Engineer", "Advanced Materials Engineer", "Metrology Engineer", "Device Fabrication Engineer", "R&D Process Engineer",

    # --- ZONE 5: HARDWARE/SOFTWARE, SENSORS & ELECTROCHEMISTRY ---
    "Sensor Development Engineer", "Electrochemical Engineer", "Hardware Software Integration Engineer",
    "Firmware Integration Engineer", "Embedded Systems Engineer", "PLC Automation Engineer",
    "Industrial Automation Engineer", "Controls Systems Engineer", "Hardware Validation Engineer",
    "Test and Measurement Engineer", "Prototype Engineer", "Solid State Sensor Engineer",
    "Physical Data Engineer", "Electro-Mechanical Engineer", "Hardware Test Engineer", "Sensor Systems Engineer",
    "System Test Engineer", "Applied Hardware Engineer", "Technical Systems Analyst", "Product Systems Engineer"
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
- MEDICAL/CLINICAL: Any role involving patient care, medical devices (unless embedded code), or hospital admin.
- IT SUPPORT: Helpdesk, SysAdmin, Network Admin, Manual QA.
- WEB DEV: Generic Wordpress, Shopify, or simple frontend roles.
- SENIORITY: Avoid 'Junior' or 'Entry Level'.
- DOMAIN: Avoid Civil Engineering, Construction, Banking, or Insurance unless high-frequency trading.
"""

# --- PERFORMANCE & GEOFENCING ---
MIN_SCORE = 7            
SWEEP_DEPTH = 100        
NUM_ANALYSTS = 3         
MAX_QUEUE_DEPTH = 50     

MAX_COMMUTE_MILES = 50.0  # Max distance from Home Coords. -1.0 means remote is allowed.