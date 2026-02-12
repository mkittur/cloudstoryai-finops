# narrative_engine.py

def build_deterministic_narrative(ranked_signals, persona):
    if not ranked_signals:
        return "No significant insights detected."

    top = ranked_signals[0]

    base = (
        f"Primary cost risk identified in {top['service']} "
        f"with estimated exposure of ${top['cost']:.2f}."
    )

    if persona == "cfo":
        return base + " Immediate financial review recommended."

    if persona == "engineering":
        return base + " Likely workload or shared-service related."

    return base

from llm_engine import refine_with_llm

def build_ai_narrative(signals, persona, intent):
    if not signals:
        return "No significant insights detected."

    top = signals[0]

    prompt = f"""
You are an enterprise FinOps AI assistant.

Persona: {persona}
Intent: {intent}

Top Signal:
Service: {top['service']}
Cost Impact: ${top['cost']}

Provide:
1. Clear explanation
2. Business impact
3. Technical reasoning
4. Action recommendation
5. ROI perspective
Be concise but executive-ready.
"""

    llm_output = refine_with_llm(prompt)

    if llm_output:
        return llm_output

    # fallback
    return build_deterministic_narrative(signals, persona)

