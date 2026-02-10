# narrative_engine.py

# narrative_engine.py

def build_narrative(ranked_signals, persona):
    if not ranked_signals:
        return "No significant insights detected."

    top = ranked_signals[0]

    if persona == "cfo":
        return (
            f"Primary cost risk identified in {top['service']} "
            f"with estimated exposure of ${top['cost']:.2f}. "
            f"Immediate review recommended."
        )

    if persona == "engineering":
        return (
            f"Cost spike observed in {top['service']}. "
            f"Likely related to workload behavior or shared service usage."
        )

    return f"Key insight detected in {top['service']}."

