"""
CloudStoryAI – AI Governance & ROI Scoring Engine
Evaluates AI-driven cost decisions with FinOps governance
"""

import psycopg2
from datetime import date
import random

# -----------------------------
# DB Connection
# -----------------------------
conn = psycopg2.connect(
    dbname="cloudstoryai",
    user="cloudstory",
    password="cloudstory_pwd",
    host="/var/run/postgresql"
)

cur = conn.cursor()

# -----------------------------
# Fetch anomalies (AI trigger)
# -----------------------------
cur.execute("""
    SELECT
        record_date,
        customer_id,
        cloud_provider,
        service_name,
        observed_cost
    FROM anomalies
""")

rows = cur.fetchall()

# -----------------------------
# Governance evaluation logic
# -----------------------------
for record_date, customer, cloud, service, cost in rows:
    cost = float(cost)
    ai_action = "Recommend workload rightsizing and scaling policy adjustment"

    # Confidence score (simulated but realistic)
    confidence = round(random.uniform(0.6, 0.9), 2)

    # Estimated FinOps impact
    estimated_savings = round(cost * random.uniform(0.15, 0.35), 2)
    estimated_cost = round(cost * 0.05, 2)

    net_roi = round(estimated_savings - estimated_cost, 2)

    if net_roi > 0 and confidence >= 0.7:
        status = "approved"
    elif net_roi > 0:
        status = "monitored"
    else:
        status = "rejected"

    justification = (
        f"AI confidence={confidence}. "
        f"Estimated savings {estimated_savings} outweigh execution cost "
        f"{estimated_cost}."
        if net_roi > 0 else
        "Projected savings do not justify execution cost."
    )

    cur.execute("""
        INSERT INTO ai_governance (
            decision_date,
            decision_type,
            customer_id,
            cloud_provider,
            service_name,
            ai_action,
            ai_confidence_score,
            estimated_savings,
            estimated_cost,
            net_roi,
            governance_status,
            justification
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        date.today(),
        "anomaly_response",
        customer,
        cloud,
        service,
        ai_action,
        confidence,
        estimated_savings,
        estimated_cost,
        net_roi,
        status,
        justification
    ))

conn.commit()
cur.close()
conn.close()

print("✅ AI governance decisions evaluated and stored")

