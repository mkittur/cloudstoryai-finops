"""
CloudStoryAI – Shared Service Allocation (DB-backed)
Reads raw_cost from PostgreSQL
Writes allocated cost into allocated_cost
"""

import psycopg2

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
# Fetch shared service cost
# -----------------------------
cur.execute("""
    SELECT
        record_date,
        cloud_provider,
        service_name,
        customer_id,
        SUM(cost_amount) AS cost,
        SUM(usage_quantity) AS usage
    FROM raw_cost
    WHERE is_shared = TRUE
    GROUP BY record_date, cloud_provider, service_name, customer_id
""")

rows = cur.fetchall()

# -----------------------------
# Organize data
# -----------------------------
grouped = {}

for record_date, cloud, service, customer, cost, usage in rows:
    key = (record_date, cloud, service)
    grouped.setdefault(key, []).append({
        "customer": customer,
        "cost": float(cost),
        "usage": float(usage)
    })

# -----------------------------
# Allocation logic
# -----------------------------
for (record_date, cloud, service), entries in grouped.items():
    total_cost = sum(e["cost"] for e in entries)
    total_usage = sum(e["usage"] for e in entries)

    for e in entries:
        allocated = (e["usage"] / total_usage) * total_cost if total_usage > 0 else 0

        cur.execute("""
            INSERT INTO allocated_cost (
                record_date,
                cloud_provider,
                service_name,
                shared_service_type,
                customer_id,
                allocation_method,
                allocated_cost
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            record_date,
            cloud,
            service,
            service,
            e["customer"],
            "usage",
            round(allocated, 2)
        ))

conn.commit()
cur.close()
conn.close()

print("✅ Allocation completed and written to allocated_cost table")

