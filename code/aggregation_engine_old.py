# aggregation_engine.py
from constants import PERSONA_WEIGHTS

def aggregate_signals(conn, intent):
    cur = conn.cursor()
    signals = []

    if intent == "COST_SPIKE":
        cur.execute("""
            SELECT cloud_provider, service_name,
                   SUM(observed_cost) AS cost,
                   COUNT(*) AS events
            FROM anomalies
            GROUP BY cloud_provider, service_name
        """)
        for r in cur.fetchall():
            signals.append({
                "service": r[1],
                "cost": float(r[2]),
                "risk": 1.0,
                "complexity": 0.4
            })

    return signals


def rank_signals(signals, persona):
    weights = PERSONA_WEIGHTS.get(persona, PERSONA_WEIGHTS["cfo"])
    ranked = []

    for s in signals:
        score = (
            s["cost"] * weights["cost"] +
            s["risk"] * weights["risk"] +
            s["complexity"] * weights["complexity"]
        )
        ranked.append({**s, "score": round(score, 2)})

    return sorted(ranked, key=lambda x: x["score"], reverse=True)

