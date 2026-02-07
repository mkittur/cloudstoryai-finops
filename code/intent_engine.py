def detect_intent(question: str) -> dict:
    q = question.lower()

    if any(k in q for k in ["anomaly", "unusual", "unexpected"]):
        return {"intent": "ANOMALY"}

    if any(k in q for k in ["increase", "spike", "jump", "anomaly"]):
        return {"intent": "COST_SPIKE"}

    if any(k in q for k in ["trend", "over time", "history"]):
        return {"intent": "TREND"}

    if any(k in q for k in ["allocate", "allocation", "shared"]):
        return {"intent": "ALLOCATION"}

    if any(k in q for k in ["save", "reduce", "optimize", "cut cost"]):
        return {"intent": "SAVINGS"}

    if any(k in q for k in ["forecast", "future", "next month"]):
        return {"intent": "FORECAST"}

    return {"intent": "GENERAL"}

