# utils/query_builder.py

def build_query_from_logic(logic: dict):

    terms = []

    for rule in logic.get("rules", []):
        t = rule.get("type")

        if t == "coverage":
            terms.append("coverage condition")

        elif t == "state":
            terms.append("state OR logic")

        elif t == "effective_date":
            terms.append("effective date")

        elif t == "transaction":
            terms.append("transaction type")

    return " ".join(terms)