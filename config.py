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
    "System Test Engineer", "Applied Hardware Engineer", "Technical Systems Analyst", "Product Systems Engineer",

    # --- EXPANSION 1: CLOUD, BACKEND, SAAS & EMBEDDED ---
    "Cloud Systems Engineer", "Backend Developer", "Full Stack Developer", "SaaS Platform Engineer", "Application Architect",
    "AI Research Engineer", "Machine Learning Scientist", "Data Infrastructure Engineer", "Cloud Solutions Architect",
    "Software Development Engineer", "API Integration Engineer", "Application Engineer", "Enterprise Architect",
    "Machine Learning Developer", "SaaS Architect", "Platform Services Engineer", "Analytics Systems Engineer",
    "Web Systems Engineer", "Full Stack Architect", "Cloud AI Engineer", "Distributed Systems Architect",
    "AI Software Engineer", "Software Validation Engineer", "Algorithm Engineer", "Technical Lead Engineer",
    "Backend Systems Developer", "Cloud Operations Engineer", "Core Services Engineer", "AI Product Engineer",
    "Data Architecture Engineer", "Platform Automation Engineer", "Search Systems Engineer", "Cloud Security Engineer",
    "Software QA Engineer", "Firmware Developer", "IoT Systems Engineer", "Autonomous Navigation Engineer",
    "Robotics Prototyping Engineer", "Embedded Linux Engineer", "Embedded Software Developer", "Motion Control Engineer",
    "Hardware Automation Engineer", "Connected Systems Engineer", "Mechatronics Architect", "Autonomous Driving Engineer",
    "Lidar Systems Engineer", "Calibration Engineer", "Robotic Process Engineer", "Fleet Autonomy Engineer",
    "UAV Systems Engineer", "Hardware Architecture Engineer", "Edge Devices Engineer", "Robotic Navigation Engineer",
    "Drone Systems Engineer", "Microcontroller Engineer", "Embedded Controls Engineer", "Automation Controls Engineer",
    "Machine Vision Engineer", "Teleoperation Systems Engineer", "Avionics Software Engineer", "Real Time Engineer",
    "Simulation Systems Engineer", "Field Automation Engineer", "Systems Architecture Engineer", "Hardware Bringup Engineer",
    "Autonomy Software Engineer", "Robotics Test Engineer", "Semiconductor Process Engineer", "Device Research Engineer",
    "Physical Sciences Engineer", "Fabrication Engineer", "Inorganic Materials Engineer", "Applied Physicist",
    "Electrochemical Scientist", "Battery Systems Engineer", "Hardware Reliability Engineer", "Microfabrication Engineer",
    "Thermal Systems Engineer", "Substrate Process Engineer", "Cleanroom Process Engineer", "Coating Process Engineer",
    "Ceramics Researcher", "Sintering Engineer", "Applied Mechanics Engineer", "R&D Hardware Engineer",
    "Hardware R&D Scientist", "Physics Simulation Engineer", "Deposition Process Engineer", "Etch Process Engineer",
    "Structural Test Engineer", "Product Design Engineer", "Quality Systems Engineer", "Chemical Sensor Engineer",
    "Electromechanical Scientist", "Nanotechnology Engineer", "Formulation Scientist", "Surface Engineer",
    "Reliability Test Engineer", "Destructive Testing Engineer", "Component Engineer",

    # --- EXPANSION 2: COMPUTATIONAL MATERIALS, SIMULATION & ADVANCED MANUFACTURING ---
    "Materials Informatics Engineer", "Computational Materials Scientist", "Materials Data Scientist", "Simulation Engineer",
    "Computational Physicist", "Predictive Modeling Engineer", "Statistical Modeling Engineer", "Multiphysics Simulation Engineer",
    "Computational Modeling Engineer", "Algorithm Development Engineer", "Materials Modeler", "Imaging Scientist",
    "Image Processing Engineer", "Sensor Data Scientist", "Automated Metrology Engineer", "Ceramic Process Engineer",
    "Thermodynamics Engineer", "Powder Processing Engineer", "Extrusion Process Engineer", "Additive Manufacturing Engineer",
    "Porous Materials Scientist", "Inorganic Materials Scientist", "Slurry Process Engineer", "Refractory Engineer",
    "Analytical Scientist", "Surface Characterization Scientist", "Defect Analysis Engineer", "Materials Reliability Engineer",
    "Microstructural Engineer", "Characterization Scientist", "Physical Property Analyst", "Reliability Systems Engineer",
    "PVD Process Engineer", "Thin Film Scientist", "Vacuum Systems Engineer", "MEMS Process Engineer",
    "Battery Materials Engineer", "Fuel Cell Engineer", "Sensor Materials Engineer", "Electrochemistry Engineer",
    "Coating Development Engineer", "Deposition Engineer", "Plasma Process Engineer", "Materials Integration Engineer",
    "Hardware Materials Engineer", "Advanced Manufacturing Engineer", "Process Characterization Engineer", "Applied Materials Scientist",
    "R&D Simulation Engineer", "Applied Physics Engineer", "Finite Element Analyst", "Mathematical Modeling Engineer",
    "Scientific Computing Engineer", "Computational Research Scientist", "Materials Research Engineer", "Structural Analysis Engineer",
    "Sensor Fabrication Engineer", "Hardware Simulation Engineer", "Aerospace Materials Engineer", "FEA Simulation Engineer"
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
SWEEP_DEPTH = 30        
NUM_ANALYSTS = 3         
MAX_QUEUE_DEPTH = 50     

MAX_COMMUTE_MILES = 50.0  # Max distance from Home Coords. -1.0 means remote is allowed.