def detect_intent(question: str) -> dict:
    q = question.lower()

    # ------------------------
    # Vendor Detection
    # ------------------------
    vendors = []

    if "aws" in q or "amazon" in q:
        vendors.append("aws")

    if "azure" in q or "microsoft" in q:
        vendors.append("azure")

    if "gcp" in q or "google cloud" in q:
        vendors.append("gcp")

    if not vendors:
        vendors = ["all"]  # default scope

    # ------------------------
    # Intent Classification
    # ------------------------

    if any(k in q for k in ["compare", "vs", "versus", "difference between"]):
        return {"intent": "VENDOR_COMPARISON", "vendors": vendors}

    if any(k in q for k in ["cost by vendor", "cloud cost", "vendor cost"]):
        return {"intent": "COST_BY_VENDOR", "vendors": vendors}

    if any(k in q for k in ["anomaly", "unusual", "unexpected"]):
        return {"intent": "ANOMALY", "vendors": vendors}

    if any(k in q for k in ["increase", "spike", "jump"]):
        return {"intent": "COST_SPIKE", "vendors": vendors}

    if any(k in q for k in ["trend", "over time", "history"]):
        return {"intent": "TREND", "vendors": vendors}

    if any(k in q for k in ["allocate", "allocation", "shared"]):
        return {"intent": "ALLOCATION", "vendors": vendors}

    if any(k in q for k in ["save", "reduce", "optimize", "cut cost"]):
        return {"intent": "SAVINGS", "vendors": vendors}

    if any(k in q for k in ["forecast", "future", "next month"]):
        return {"intent": "FORECAST", "vendors": vendors}

    if any(k in q for k in ["total cost", "overall cost", "spend"]):
        return {"intent": "TOTAL_COST", "vendors": vendors}

    return {"intent": "GENERAL", "vendors": vendors}
