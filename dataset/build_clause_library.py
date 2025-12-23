import json
import glob
import re
import os

CLAUSE_DIR = "dataset/clauses"
OUTPUT_FILE = "dataset/clause_library.json"

# Clause Function Classifier

def classify_clause(text):
    text_l = text.lower()

    RULES = {
        "parties": ["party", "parties", "represented", "henceforth", "address"],
        "term": ["term", "duration", "effectivity", "commencement", "effectivity"],
        "payment": ["pay", "payment", "amount", "compensation", "rent", "consideration"],
        "termination": ["termination", "terminate", "cancel", "rescission"],
        "obligations": ["obligations", "duties", "responsibilities", "shall"],
        "confidentiality": ["confidential", "non-disclosure", "nda"],
        "dispute_resolution": ["arbitration", "dispute", "jurisdiction", "venue"],
        "capital": ["capital", "contribution", "investment"],   # for partnership
    }

    for function, keywords in RULES.items():
        if any(k in text_l for k in keywords):
            return function

    return "miscellaneous"

# Template Placeholder Inserter

def convert_to_template(text):
    text = text.replace("_________", "{placeholder}")
    text = re.sub(r'₱\s?\d+(?:,\d{3})*', "{amount}", text)
    text = re.sub(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+', "{name}", text)
    text = re.sub(r'\d{4}-\d{2}-\d{2}', "{date}", text)
    return text

# Mandatory Clause Mapping

MANDATORY_CLAUSES = {
    "rental": ["parties", "payment", "term"],
    "buy_and_sell": ["parties", "payment"],
    "partnership": ["parties", "capital", "obligations"],
    "employment": ["parties", "obligations", "payment", "term"]
}

# Process Clause Files

library = {}

for fpath in glob.glob(f"{CLAUSE_DIR}/*.json"):
    with open(fpath, "r", encoding="utf-8") as f:
        clauses = json.load(f)

    # Skip empty files or wrong formats
    if not clauses or not isinstance(clauses, list):
        print(f"⚠ Skipped empty or invalid file: {os.path.basename(fpath)}")
        continue

    # ALSO skip if first clause has no contract_type
    if "contract_type" not in clauses[0]:
        print(f"⚠ Skipped file with missing contract_type: {os.path.basename(fpath)}")
        continue

    contract_type = clauses[0]["contract_type"]

# Save Final Clause Library

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(library, f, indent=4)

print("Enhanced clause library created!")
