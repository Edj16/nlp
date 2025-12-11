import json
import glob 

CLAUSE_DIR = "dataset/clauses"
OUTPUT_FILE = "dataset/clause_library.json"

library = {}

for fpath in glob.glob(f"{CLAUSE_DIR}/*.json"):
    with open(fpath, "r", encoding="utf-8") as f:
        clauses = json.load(f)

    ctype = clauses[0]["contract_type"]
    library[ctype] = []

    for c in clauses:
        library[ctype].append({
            "template": c["clause_text"],
            "entities": c["entities"]
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(library, f, indent=4)

print("Clause library created!")
