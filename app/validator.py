def validate_inputs(user_inputs, law_json):
    """
    Validate user inputs against legal requirements.
    Returns a list of validation errors.
    """
    errors = []
    
    # Define required fields for partnership contracts
    required_fields = {
        "partners": "Names of all partners",
        "capital_contribution": "Capital contribution details",
        "profit_sharing": "Profit and loss sharing arrangement",
        "duration": "Duration of partnership"
    }
    
    # Check for missing required fields
    for field, description in required_fields.items():
        if field not in user_inputs or not user_inputs[field]:
            errors.append({
                "field": field,
                "reason": f"Required field: {description} (Article 1767, 1797)"
            })
    
    # Validate capital contribution format
    if "capital_contribution" in user_inputs:
        contrib = user_inputs["capital_contribution"]
        if "/" in contrib:
            parts = contrib.split("/")
            try:
                total = sum(int(p) for p in parts)
                if total != 100:
                    errors.append({
                        "field": "capital_contribution",
                        "reason": f"Contributions must total 100% (currently {total}%)"
                    })
            except ValueError:
                errors.append({
                    "field": "capital_contribution",
                    "reason": "Invalid format. Use format like '60/40' for percentages"
                })
    
    # Validate profit sharing format
    if "profit_sharing" in user_inputs:
        profit = user_inputs["profit_sharing"]
        if "/" in profit:
            parts = profit.split("/")
            try:
                total = sum(int(p) for p in parts)
                if total != 100:
                    errors.append({
                        "field": "profit_sharing",
                        "reason": f"Profit shares must total 100% (currently {total}%) - Article 1797"
                    })
            except ValueError:
                errors.append({
                    "field": "profit_sharing",
                    "reason": "Invalid format. Use format like '60/40' for percentages"
                })
    
    # Validate duration
    if "duration" in user_inputs:
        duration = user_inputs["duration"].lower()
        if "year" in duration:
            try:
                years = int(''.join(filter(str.isdigit, duration)))
                if years > 50:
                    errors.append({
                        "field": "duration",
                        "reason": "Partnership duration seems unusually long. Consider review."
                    })
            except ValueError:
                pass
    
    # Check against void conditions from law
    for article in law_json.get("articles", []):
        if article["article"] == "1799":  # Exclusion from profits is void
            if "profit_sharing" in user_inputs:
                if "0" in user_inputs["profit_sharing"]:
                    errors.append({
                        "field": "profit_sharing",
                        "reason": f"Article 1799: A stipulation which excludes one or more partners from any share in the profits or losses is void"
                    })
    
    return errors