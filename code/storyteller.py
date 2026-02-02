"""
CloudStoryAI – Persona-Based Storytelling Engine
Author: Mahantesh Kittur

Purpose:
Convert FinOps anomaly events into role-specific narratives.
Designed for dashboards, reports, and future audio output.
"""

import json

# -----------------------------
# Persona Templates
# -----------------------------
PERSONA_TEMPLATES = {
    "finops_analyst": (
        "An anomaly was detected for {customer} on {cloud}. "
        "Observed cost was {observed_cost}, exceeding the normal range of {expected_range}. "
        "This suggests inefficient resource utilization or misconfigured scaling. "
        "Recommended action: investigate workload patterns and adjust allocation."
    ),

    "engineering_manager": (
        "A significant cost spike occurred for {customer} on {cloud}. "
        "The usage exceeded historical norms, likely due to autoscaling behavior "
        "or unexpected workload bursts. "
        "Action required: review deployment scaling rules and recent code changes."
    ),

    "cfo": (
        "We identified an unusual increase in infrastructure spend for {customer} "
        "on {cloud}. Costs exceeded expected levels, indicating potential waste "
        "or unplanned demand. "
        "This may impact monthly budget forecasts if not addressed promptly."
    )
}

# -----------------------------
# Story Generator
# -----------------------------
def generate_story(anomaly, persona):
    template = PERSONA_TEMPLATES.get(persona)

    if not template:
        raise ValueError(f"Unsupported persona: {persona}")

    return template.format(
        customer=anomaly["customer"],
        cloud=anomaly["cloud"],
        observed_cost=anomaly["observed_cost"],
        expected_range=anomaly["expected_range"]
    )


# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    with open("anomaly_event.json") as f:
        event = json.load(f)

    stories = []

    for anomaly in event["anomalies"]:
        for persona in PERSONA_TEMPLATES.keys():
            stories.append({
                "persona": persona,
                "customer": anomaly["customer"],
                "cloud": anomaly["cloud"],
                "story": generate_story(anomaly, persona)
            })

    with open("story_output.json", "w") as f:
        json.dump(stories, f, indent=2)

    print(f"Generated {len(stories)} persona-based stories")
    print("Output written to story_output.json")

