def analyze_contract(text, law_json):
    return f"""
Analyze the following contract.

Contract:
{text}

Check against these laws:
{law_json}

List:
- Compliant clauses
- Risks
- Invalid clauses with articles
"""
