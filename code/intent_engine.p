# intent_engine.py

def detect_intent(question: str) -> dict:
    q = question.lower()

    if any(k in q for k in ["save", "reduce", "optimize"]):
        return {"intent": "SAVINGS"}

    if any(k in q for k in ["increase", "spike", "anomaly"]):
        return {"intent": "COST_SPIKE"}

    if any(k in q for k in ["allocation", "shared"]):
        return {"intent": "ALLOCATION"}

    if any(k in q for k in ["trend", "growth"]):
        return {"intent": "TREND"}

    return {"intent": "GENERAL"}

