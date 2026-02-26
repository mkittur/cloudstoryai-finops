from constants import PERSONA_WEIGHTS

def aggregate_signals(conn, intent):
    cur = conn.cursor()
    signals = []

    # -------------------------------------------------
    # COST SPIKE → anomalies table
    # -------------------------------------------------
    if intent == "COST_SPIKE":
        cur.execute("""
            SELECT service_name,
                   SUM(observed_cost) AS cost
            FROM anomalies
            GROUP BY service_name
            ORDER BY cost DESC
            LIMIT 5
        """)
        for r in cur.fetchall():
            signals.append({
                "service": r[0],
                "cost": float(r[1]),
                "risk": 1.0,
                "complexity": 0.4
            })

    # -------------------------------------------------
    # SAVINGS → highest allocated services
    # -------------------------------------------------
    elif intent == "SAVINGS":
        cur.execute("""
            SELECT service_name,
                   SUM(allocated_cost) AS cost
            FROM allocated_cost
            GROUP BY service_name
            ORDER BY cost DESC
            LIMIT 5
        """)
        for r in cur.fetchall():
            signals.append({
                "service": r[0],
                "cost": float(r[1]),
                "risk": 0.6,
                "complexity": 0.5
            })

    # -------------------------------------------------
    # ALLOCATION → shared services breakdown
    # -------------------------------------------------
    elif intent == "ALLOCATION":
        cur.execute("""
            SELECT shared_service_type,
                   SUM(allocated_cost) AS cost
            FROM allocated_cost
            WHERE shared_service_type IS NOT NULL
            GROUP BY shared_service_type
            ORDER BY cost DESC
            LIMIT 5
        """)
        for r in cur.fetchall():
            signals.append({
                "service": r[0],
                "cost": float(r[1]),
                "risk": 0.4,
                "complexity": 0.7
            })

    # -------------------------------------------------
    # TREND → top services by recent spend
    # -------------------------------------------------
    elif intent == "TREND":
        cur.execute("""
            SELECT service_name,
                   SUM(allocated_cost) AS cost
            FROM allocated_cost
            WHERE record_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY service_name
            ORDER BY cost DESC
            LIMIT 5
        """)
        for r in cur.fetchall():
            signals.append({
                "service": r[0],
                "cost": float(r[1]),
                "risk": 0.5,
                "complexity": 0.5
            })

    # -------------------------------------------------
    # GENERAL → overall top cost drivers
    # -------------------------------------------------
    else:
        cur.execute("""
            SELECT service_name,
                   SUM(allocated_cost) AS cost
            FROM allocated_cost
            GROUP BY service_name
            ORDER BY cost DESC
            LIMIT 5
        """)
        for r in cur.fetchall():
            signals.append({
                "service": r[0],
                "cost": float(r[1]),
                "risk": 0.5,
                "complexity": 0.5
            })

    cur.close()
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

