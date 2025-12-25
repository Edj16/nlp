def build_contract_prompt(contract_type, user_data, law_json):
    """
    Build a detailed prompt for contract generation based on legal requirements.
    """
    
    # Extract relevant legal rules
    mandatory_rules = []
    for article in law_json.get("articles", []):
        if article.get("mandatory_clause"):
            mandatory_rules.append(f"Article {article['article']}: {article['rule']}")
    
    rules_text = "\n".join([f"  {i+1}. {rule}" for i, rule in enumerate(mandatory_rules)])
    
    # Format user data nicely
    user_data_text = "\n".join([f"  - {key}: {value}" for key, value in user_data.items()])
    
    prompt = f"""You are a Philippine legal contract drafting assistant specialized in business contracts compliant with the Philippine Civil Code.

TASK: Generate a complete and legally compliant {contract_type} Agreement.

USER PROVIDED DETAILS:
{user_data_text}

MANDATORY LEGAL REQUIREMENTS (Philippine Civil Code):
{rules_text}

INSTRUCTIONS:
1. Draft a complete {contract_type} Agreement with proper legal structure
2. Include all required clauses based on the mandatory legal requirements
3. Use formal legal language appropriate for Philippine contracts
4. Structure the contract with:
   - Title
   - Parties section
   - Recitals (WHEREAS clauses)
   - Terms and Conditions (numbered articles)
   - Signatures section
5. After the contract, provide a "LEGAL PROTECTIONS EXPLAINED" section that explains:
   - How each major clause is protected by specific Civil Code articles
   - Scenarios showing what happens if either party breaches
   - Rights and remedies available to each party

CONTRACT FORMAT:
---
[Generate the complete contract here]
---

LEGAL PROTECTIONS EXPLAINED:
[Explain the legal protections with article references]

Now generate the complete {contract_type} Agreement:"""
    
    return prompt


def build_analysis_prompt(contract_text, law_json):
    """
    Build a prompt for analyzing an existing contract.
    """
    
    # Extract all relevant rules
    all_rules = []
    for article in law_json.get("articles", []):
        all_rules.append(f"Article {article['article']} ({article['topic']}): {article['rule']}")
    
    rules_text = "\n".join([f"  {i+1}. {rule}" for i, rule in enumerate(all_rules)])
    
    prompt = f"""You are a Philippine legal contract analyst. Analyze the following contract for compliance with Philippine Civil Code.

CONTRACT TO ANALYZE:
---
{contract_text}
---

APPLICABLE LAWS (Philippine Civil Code):
{rules_text}

ANALYSIS INSTRUCTIONS:
Provide a comprehensive analysis with the following sections:

1. COMPLIANCE CHECK
   - List all clauses that comply with Philippine Civil Code
   - Reference specific articles for each compliant clause

2. VIOLATIONS & RISKS
   - Identify any clauses that violate Philippine law
   - Explain why they violate and which articles
   - Rate risk level: HIGH, MEDIUM, or LOW

3. MISSING PROVISIONS
   - List mandatory clauses that should be included but are missing
   - Reference the articles requiring these provisions

4. DANGEROUS OR UNFAIR TERMS
   - Highlight any terms that heavily favor one party
   - Identify potential loopholes
   - Explain the risks to each party

5. RECOMMENDATIONS
   - Provide specific suggestions to make the contract legally compliant
   - Suggest additional protective clauses

6. OVERALL ASSESSMENT
   - Summary: Is this contract safe to sign? (YES/NO/WITH MODIFICATIONS)
   - Overall risk rating
   - Key actions needed before signing

Now provide your detailed analysis:"""
    
    return prompt