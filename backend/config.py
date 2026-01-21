"""
Updated Configuration - Labor merged into Employment
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LAWS_DIR = DATA_DIR / "laws"
TEMPLATES_DIR = DATA_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
for directory in [DATA_DIR, LAWS_DIR, TEMPLATES_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Flask configuration
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

# Logging
LOG_FILE = BASE_DIR / "logs" / "kontrata.log"
LOG_FILE.parent.mkdir(exist_ok=True)
LOG_LEVEL = "INFO"

# Ollama Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Contract Types - LABOR REMOVED, merged into EMPLOYMENT
CONTRACT_TYPES = [
    "EMPLOYMENT",  # Now includes labor contracts
    "PARTNERSHIP",
    "LEASE",
    "BUY_SELL"
]

# Required Fields - Will be dynamically loaded from law JSONs
# This is just a fallback
REQUIRED_FIELDS = {
    "EMPLOYMENT": [
        "employer_name",
        "employee_name",
        "position",
        "salary",
        "employment_type",
        "start_date",
        "working_hours",
        "work_schedule",
        "place_of_work"
    ],
    "PARTNERSHIP": [
        "partner1_name",
        "partner2_name",
        "business_name",
        "business_purpose",
        "capital_contribution1",
        "capital_contribution2",
        "profit_sharing",
        "start_date"
    ],
    "LEASE": [
        "lessor_name",
        "lessee_name",
        "property_description",
        "rental_amount",
        "lease_duration",
        "start_date",
        "payment_schedule",
        "security_deposit",
        "utilities",
        "repairs"
    ],
    "BUY_SELL": [
        "seller_name",
        "buyer_name",
        "item_description",
        "sale_price",
        "payment_terms",
        "delivery_date",
        "warranty_period"
    ]
}

# File upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Out of scope message
OUT_OF_SCOPE_MESSAGE = """I'm KontrataPH, your contract assistant. I can help with:

• Generating contracts (Employment, Partnership, Lease, Buy & Sell)
• Analyzing contracts
• Answering questions about Philippine contract law

What would you like help with?"""