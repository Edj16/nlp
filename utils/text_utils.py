def get_mandatory_fields(law_json):
    return [
        a for a in law_json["articles"]
        if a.get("mandatory_clause")
    ]