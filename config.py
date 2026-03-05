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
# Expanded for volume and specificity based on resume analysis
INITIAL_SEARCH_TERMS = ["Founding Engineer", "Robotics AI", "Systems Automation"] 
LOCATIONS = ["Boston, MA", "USA", "Remote"]

# --- FILTERING & HEURISTICS ---
# Hard-block terms. If these appear in Title or Company, the job is instantly rejected.
BLACKLIST_KEYWORDS = [
    "intern", "internship", "co-op", "coop", "student", 
    "undergraduate", "volunteer", "unpaid", "part-time",
    "cybercoders", "revature", "cannon search"
]

# Strategic preferences injected into the LLM for semantic scoring
USER_PREFERENCES = """
NEGATIVE CONSTRAINTS (Reject or Score Low):
- Internships, Co-ops, or Student positions.
- Roles requiring Security Clearance (Secret/TS) unless explicitly high-tech.
- Staffing/Recruiting agency posts (low quality signal).
- Roles focusing purely on IT Support, Helpdesk, or Manual QA.
- Seniority: Avoid 'Junior' or 'Entry Level' if not Founding/Startup context.
"""

# The Absolute Boundaries of the Agent's Universe
CORE_SCHEMA = [
    # --- AI, LLM & AGENTIC SYSTEMS ---
    "AI Systems Engineer",
    "LLM Infrastructure Engineer",
    "Agentic AI Architect",
    "RAG Systems Specialist",
    "Generative AI Platform Engineer",
    "Vector Database Engineer",
    "Machine Learning Operations (MLOps)",
    "Natural Language Processing (NLP) Engineer",
    "AI Observability Engineer",
    "AI Safety and Validation Engineer",
    "AI Compliance Auditor",
    "Semantic Search Engineer",
    "LLM Evaluation Frameworks",
    "Prompt Engineer",
    "Context Engineering Specialist",
    "Knowledge Graph Engineer",
    "Applied AI Scientist",
    "LLM Orchestration Engineer",
    "AI Integration Engineer",
    "Verifiable Agentic Workflows",
    
    # --- ROBOTICS, AUTONOMY & PERCEPTION ---
    "Robotics Software Engineer",
    "Autonomy Engineer",
    "Perception Engineer",
    "Motion Planning Engineer",
    "Computer Vision Engineer",
    "LiDAR Systems Engineer",
    "Sensor Fusion Engineer",
    "Embedded Software Engineer",
    "Controls Engineer",
    "PLC Automation Engineer",
    "Industrial Automation Engineer",
    "Mechatronics Engineer",
    "Robotic Systems Integrator",
    "Spatial Algorithms Engineer",
    "Navigation Systems Engineer",
    "SLAM Engineer",
    "Robotic Perception Specialist",
    "Firmware Engineer",
    "Real-Time Systems Engineer",
    "Autonomous Ground Vehicle (AGV) Engineer",
    "Robotics Deployment Engineer",
    "Geometric Algorithms Developer",
    
    # --- BACKEND, PLATFORM & DISTRIBUTED SYSTEMS ---
    "Founding Systems Engineer",
    "Backend Systems Engineer",
    "Full Stack Software Engineer",
    "Distributed Systems Engineer",
    "Platform Engineer",
    "Cloud Infrastructure Architect",
    "API Infrastructure Engineer",
    "Database Engineer",
    "PostgreSQL Specialist",
    "DevOps Engineer",
    "Site Reliability Engineer (SRE)",
    "Systems Architect",
    "Scalable Infrastructure Engineer",
    "Microservices Architect",
    "Docker & Containerization Specialist",
    "CI/CD Pipeline Engineer",
    "Python Backend Developer",
    "TypeScript Software Engineer",
    "Data Engineering Architect",
    "Schema-Driven Systems Designer",
    "Deterministic System Architect",
    
    # --- MATERIALS SCIENCE, RESEARCH & HARDWARE ---
    "Materials Science Engineer",
    "Research & Development (R&D) Engineer",
    "Scientific Computing Engineer",
    "Computational Geometry Researcher",
    "NASA Systems Engineer",
    "Aerospace Materials Engineer",
    "Laboratory Automation Engineer",
    "Thin Film Process Engineer",
    "SEM/EDS Analysis Specialist",
    "Experimental Design Engineer (DOE)",
    "Capillary Systems Designer",
    "Ceramic Engineering Specialist",
    "Characterization Engineer",
    "Instrumentation Engineer",
    "Hardware-Software Integration Engineer",
    "Electrical Systems Engineer",
    "Battery Systems Engineer",
    "Energy Storage Engineer",
    "New Product Introduction (NPI) Engineer",
    "Manufacturing Systems Engineer",
    "Hardware Validation Engineer",
    "Test and Measurement Engineer",
    "Digital Signal Processing (DSP) Engineer",
    
    # --- SPECIALIZED PRODUCT & STRATEGY ROLES ---
    "Design Technologist",
    "Product Systems Engineer",
    "Technical Design Lead",
    "Workflow Automation Architect",
    "Business Process Automation Engineer",
    "Solutions Architect (AI/Robotics)",
    "Technical Program Manager (Systems)",
    "Technical Product Manager",
    "High-Assurance Systems Engineer",
    "Digital Twin Engineer",
    "Simulation Engineer",
    "MATLAB Modeling Specialist",
    "Climate Tech Engineer",
    "Energy Infrastructure Engineer",
    "Space Systems Engineer",
    "Advanced Manufacturing Engineer"
]

# --- PERFORMANCE & MODES ---
MIN_SCORE = 7            # The minimum LLM score required to deploy a resume
SWEEP_DEPTH = 100        # Exhaustive search: Pull up to 100 jobs per term per location
NUM_ANALYSTS = 2         # Dual-thread LLM evaluation
MAX_QUEUE_DEPTH = 50     # If queue > 50, Hunter sleeps (Matching Mode)