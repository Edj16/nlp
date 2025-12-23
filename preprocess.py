import os
import re
import json
from unidecode import unidecode
import nltk
import spacy

nlp = spacy.load("en_core_web_sm")

RAW_DIR = "dataset/raw_contracts"
CLEAN_DIR = "dataset/cleaned_text"
CLAUSE_DIR = "dataset/clauses"

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(CLAUSE_DIR, exist_ok=True)

# Cleaning functions
def clean_text(text):
    text = unidecode(text)                         # normalize unicode
    text = re.sub(r'\s+', ' ', text).strip()       # remove excessive whitespace
    text = re.sub(r'[“”]', '"', text)              # normalize quotes
    text = re.sub(r'[’]', "'", text)               # normalize apostrophes
    text = text.replace("\t", " ")
    return text

def normalize_for_nlp(text):
    text = text.lower()
    return text


def tokenize_sentence(text):
    return nltk.sent_tokenize(text)


# Rule-based entity extraction
def extract_entities(text):
    entities = {}

    # Money
    money_pattern = r'(₱\s?\d+(?:,\d{3})*|\d+(?:,\d{3})* pesos)'
    entities["amount"] = True if re.search(money_pattern, text, re.IGNORECASE) else False

    # Dates
    date_pattern = r'\b(\d{1,2}\/\d{1,2}\/\d{2,4})|\b(\d{4}-\d{2}-\d{2})'
    entities["date"] = True if re.search(date_pattern, text) else False

    # Names (capitalized sequences)
    name_pattern = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+'
    entities["party_name"] = True if re.search(name_pattern, text) else False

    return entities


# Clause segmentation
def segment_into_clauses(text):
    # Break into paragraphs or numbered clauses
    clauses = re.split(r'\n\d+\.\s|\n\n+', text)
    clauses = [c.strip() for c in clauses if len(c.strip()) > 20]  # keep meaningful clauses
    return clauses



# Main processing loop
def process_contract_type(contract_type):
    type_path = os.path.join(RAW_DIR, contract_type)
    all_clauses = []

    for filename in os.listdir(type_path):
        if not filename.endswith(".txt"):
            continue

        with open(os.path.join(type_path, filename), "r", encoding="utf-8") as f:
            raw = f.read()

        cleaned = clean_text(raw)
        normalized = normalize_for_nlp(cleaned)
        clauses = segment_into_clauses(cleaned)

        # save cleaned file
        out_clean_path = os.path.join(CLEAN_DIR, f"{contract_type}_{filename}")
        with open(out_clean_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        # process each clause
        for i, clause in enumerate(clauses):
            entry = {
                "id": f"{contract_type}_{filename}_{i}",
                "contract_type": contract_type,
                "clause_text": clause,
                "clause_text_normalized": normalized,
                "entities": extract_entities(clause)
            }
            all_clauses.append(entry)

    # Save to JSON
    out_json = os.path.join(CLAUSE_DIR, f"{contract_type}_clauses.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_clauses, f, indent=4)

# Run preprocessing
CONTRACT_TYPES = ["rental", "buy_and_sell", "partnerships", "employment"]

for ctype in CONTRACT_TYPES:
    process_contract_type(ctype)

print("Preprocessing complete!")
