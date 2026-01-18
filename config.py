"""
Configuration for the Patient Allocator application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get the directory where this config file is located (for absolute paths)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Password protection - set via environment variable or use default
APP_PASSWORD = os.environ.get('APP_PASSWORD', 'CRMCPATIENTS')

# File paths for persistent storage (using absolute paths)
DATA_FILE = os.path.join(BASE_DIR, "physician_data.csv")
YESTERDAY_FILE = os.path.join(BASE_DIR, "yesterday_physicians.csv")
SELECTED_FILE = os.path.join(BASE_DIR, "selected_physicians.csv")
MASTER_LIST_FILE = os.path.join(BASE_DIR, "master_physician_list.csv")
DEFAULT_PARAMS_FILE = os.path.join(BASE_DIR, "default_parameters.csv")
DEFAULT_PHYSICIANS_FILE = os.path.join(BASE_DIR, "default_physicians.csv")
TEAM_ASSIGNMENTS_FILE = os.path.join(BASE_DIR, "team_assignments.csv")

# Default master physician list
DEFAULT_MASTER_LIST = [
    "Adhiakha", "Wang", "Jaini", "JemJem", "Batth",
    "Rajarathinam", "Shehata", "Yousef", "Aung", "Bhogireddy",
    "Souliman", "Zaidi", "Attrapisi", "Ali", "Batlawala",
    "Sakkalaek", "Shirani", "Oladipo", "Abadi", "Kaur",
    "Narra", "Suman", "Win", "Das", "Alchi", "Reddy",
    "Hung", "Nwadei", "Lamba", "Ahir", "Mahajan", "Abukraa",
    "Keralos", "Nibber"
]

# Default allocation parameters
DEFAULT_PARAMETERS = {
    "n_total_new_patients": 20,
    "n_A_new_patients": 10,
    "n_B_new_patients": 8,
    "n_N_new_patients": 2,
    "n_step_down_patients": 0,
    "minimum_patients": 10,
    "maximum_patients": 20,
    "new_start_number": 5
}

# Team options
TEAMS = ["A", "B", "N"]
