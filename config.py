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

# --- SCHEMA FIRST APPROACH ---
INITIAL_SEARCH_TERMS = ["Founding Engineer", "Robotics AI", "Systems Automation"] 
LOCATIONS = ["Boston, MA", "USA", "Remote"]

# --- SMART HEURISTICS (REGEX BASED) ---
# These must match EXACT tokens (\b) to prevent "hr" killing "Northrop" or "mechanic" killing "Mechanical"

# 1. ROLES WE NEVER WANT (Check against Job Title)
TITLE_BLACKLIST = [
    # Seniority / Type
    r"\bintern\b", r"\binternship\b", r"\bco-op\b", r"\bcoop\b", r"\bstudent\b", 
    r"\bundergraduate\b", r"\bvolunteer\b", r"\bunpaid\b", r"\bpart-time\b",
    
    # Medical / Clinical Practice (Not tech at medical companies)
    r"\bphysician\b", r"\bnurse\b", r"\bclinical\b", r"\bpatient\b", r"\btherapist\b", 
    r"\bsurgeon\b", r"\bveterinary\b", r"\bpharmacy\b", r"\bpsychologist\b", r"\bcounselor\b",
    r"\bdentist\b", r"\bmedical assistant\b",
    
    # Sales / Non-Technical
    r"\bsales\b", r"\baccount executive\b", r"\bmarketing\b", r"\brecruiter\b", 
    r"\bhr\b", r"\bhuman resources\b", r"\bsecretary\b", r"\bclerk\b", r"\bdriver\b", 
    r"\bwarehouse\b", r"\bcustomer service\b", r"\bmerchandising\b",
    
    # Trades (Standalone words, not "Engineering Technician" usually, but let's be safe)
    r"\bmechanic\b", r"\belectrician\b", r"\bplumber\b", r"\bhvac\b", r"\bwelder\b"
]

# 2. COMPANIES WE NEVER WANT (Check against Company Name)
COMPANY_BLACKLIST = [
    r"\bcybercoders\b", r"\brevature\b", r"\bcannon search\b", r"\bjobot\b", r"\bbairesdev\b"
]

# 3. ALLOWLIST PARDONS
# If a title contains these, it's highly likely a tech role, even if "support" or "medical" appears.
ALLOWLIST_OVERRIDES = [
    r"\bsoftware\b", r"\bengineer\b", r"\bdeveloper\b", r"\bsystems\b", r"\bdata\b", 
    r"\brobotics\b", r"\bai\b", r"\bmachine learning\b", r"\barchitect\b"
]

# Soft-block terms injected into the LLM prompt.
USER_PREFERENCES = """
NEGATIVE CONSTRAINTS (Reject or Score Low):
- MEDICAL/CLINICAL: Any role involving patient care, medical devices (unless embedded code), or hospital admin.
- IT SUPPORT: Helpdesk, SysAdmin, Network Admin, Manual QA.
- WEB DEV: Generic Wordpress, Shopify, or simple frontend roles.
- SENIORITY: Avoid 'Junior' or 'Entry Level'.
- DOMAIN: Avoid Civil Engineering, Construction, Banking, or Insurance unless high-frequency trading.
"""

# The Absolute Boundaries of the Agent's Universe
CORE_SCHEMA = [
    "AI Systems Engineer", "LLM Infrastructure Engineer", "Agentic AI Architect", "RAG Systems Specialist",
    "Generative AI Platform Engineer", "Vector Database Engineer", "Machine Learning Operations (MLOps)",
    "Natural Language Processing (NLP) Engineer", "AI Observability Engineer", "AI Safety and Validation Engineer",
    "AI Compliance Auditor", "Semantic Search Engineer", "LLM Evaluation Frameworks", "Prompt Engineer",
    "Context Engineering Specialist", "Knowledge Graph Engineer", "Applied AI Scientist", "LLM Orchestration Engineer",
    "AI Integration Engineer", "Verifiable Agentic Workflows",
    
    "Robotics Software Engineer", "Autonomy Engineer", "Perception Engineer", "Motion Planning Engineer",
    "Computer Vision Engineer", "LiDAR Systems Engineer", "Sensor Fusion Engineer", "Embedded Software Engineer",
    "Controls Engineer", "PLC Automation Engineer", "Industrial Automation Engineer", "Mechatronics Engineer",
    "Robotic Systems Integrator", "Spatial Algorithms Engineer", "Navigation Systems Engineer", "SLAM Engineer",
    "Robotic Perception Specialist", "Firmware Engineer", "Real-Time Systems Engineer", "Autonomous Ground Vehicle (AGV) Engineer",
    "Robotics Deployment Engineer", "Geometric Algorithms Developer",
    
    "Founding Systems Engineer", "Backend Systems Engineer", "Full Stack Software Engineer", "Distributed Systems Engineer",
    "Platform Engineer", "Cloud Infrastructure Architect", "API Infrastructure Engineer", "Database Engineer",
    "PostgreSQL Specialist", "DevOps Engineer", "Site Reliability Engineer (SRE)", "Systems Architect",
    "Scalable Infrastructure Engineer", "Microservices Architect", "Docker & Containerization Specialist",
    "CI/CD Pipeline Engineer", "Python Backend Developer", "TypeScript Software Engineer", "Data Engineering Architect",
    "Schema-Driven Systems Designer", "Deterministic System Architect",
    
    "Materials Science Engineer", "Research & Development (R&D) Engineer", "Scientific Computing Engineer",
    "Computational Geometry Researcher", "NASA Systems Engineer", "Aerospace Materials Engineer", "Laboratory Automation Engineer",
    "Thin Film Process Engineer", "SEM/EDS Analysis Specialist", "Experimental Design Engineer (DOE)", "Capillary Systems Designer",
    "Ceramic Engineering Specialist", "Characterization Engineer", "Instrumentation Engineer", "Hardware-Software Integration Engineer",
    "Electrical Systems Engineer", "Battery Systems Engineer", "Energy Storage Engineer", "New Product Introduction (NPI) Engineer",
    "Manufacturing Systems Engineer", "Hardware Validation Engineer", "Test and Measurement Engineer", "Digital Signal Processing (DSP) Engineer",
    
    "Design Technologist", "Product Systems Engineer", "Technical Design Lead", "Workflow Automation Architect",
    "Business Process Automation Engineer", "Solutions Architect (AI/Robotics)", "Technical Program Manager (Systems)",
    "Technical Product Manager", "High-Assurance Systems Engineer", "Digital Twin Engineer", "Simulation Engineer",
    "MATLAB Modeling Specialist", "Climate Tech Engineer", "Energy Infrastructure Engineer", "Space Systems Engineer",
    "Advanced Manufacturing Engineer"
]

MIN_SCORE = 7            
SWEEP_DEPTH = 100        
NUM_ANALYSTS = 3         
MAX_QUEUE_DEPTH = 50