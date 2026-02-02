"""
CloudStoryAI – Anomaly Detection on Allocated Cost (DB-backed)
Detects customer-level spend anomalies and stores them in PostgreSQL.
"""

import psycopg2
import statistics
from datetime import datetime

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
# Fetch allocated cost history
# -----------------------------
cur.execute("""
    SELECT
        record_date,
        customer_id,
        cloud_provider,
        service_name,
        allocated_cost
    FROM allocated_cost
""")

rows = cur.fetchall()

# -----------------------------
# Group data for analysis
# -----------------------------
grouped = {}

for record_date, customer, cloud, service, cost in rows:
    key = (customer, cloud, service)
    grouped.setdefault(key, []).append((record_date, float(cost)))

# -----------------------------
# Detect anomalies
# -----------------------------
for (customer, cloud, service), records in grouped.items():
    costs = [c for _, c in records]

    if len(costs) < 3:
        continue  # not enough data

    mean = statistics.mean(costs)
    stddev = statistics.stdev(costs)

    threshold = mean + (2 * stddev)

    for record_date, cost in records:
        if cost > threshold:
            cur.execute("""
                INSERT INTO anomalies (
                    record_date,
                    customer_id,
                    cloud_provider,
                    service_name,
                    observed_cost,
                    expected_range,
                    severity,
                    finops_reasoning,
                    detected_at
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                record_date,
                customer,
                cloud,
                service,
                cost,
                f"<= {round(threshold, 2)}",
                "HIGH",
                "Allocated cost significantly exceeded historical baseline. "
                "Likely causes include workload spike, scaling misconfiguration, "
                "or inefficient resource utilization.",
                datetime.utcnow()
            ))

conn.commit()
cur.close()
conn.close()

print("✅ Anomaly detection completed and stored in anomalies table")

