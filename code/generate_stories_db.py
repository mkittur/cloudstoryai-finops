"""
CloudStoryAI – Persona-Based Storytelling (DB-backed)
Reads anomalies from PostgreSQL
Writes narratives into stories table
"""

import psycopg2

# -----------------------------
# Persona Templates
# -----------------------------
PERSONA_TEMPLATES = {
    "finops_analyst": (
        "An anomaly was detected for customer {customer} on {cloud} "
        "for service {service}. The allocated cost reached {cost}, "
        "exceeding the expected threshold {threshold}. "
        "Recommended action: review workload usage patterns and "
        "validate allocation assumptions."
    ),

    "engineering_manager": (
        "A cost spike occurred for customer {customer} on {cloud} "
        "within service {service}. The observed cost of {cost} "
        "is higher than normal expectations. "
        "This may indicate autoscaling misconfiguration or "
        "unexpected workload behavior."
    ),

    "cfo": (
        "We identified an unusual increase in infrastructure spend "
        "for customer {customer} on {cloud}. Costs for {service} "
        "exceeded expected levels, which could impact budget forecasts "
        "if not addressed."
    )
}

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
# Fetch anomalies
# -----------------------------
cur.execute("""
    SELECT
        record_date,
        customer_id,
        cloud_provider,
        service_name,
        observed_cost,
        expected_range
    FROM anomalies
""")

anomalies = cur.fetchall()

# -----------------------------
# Generate stories
# -----------------------------
for record_date, customer, cloud, service, cost, threshold in anomalies:
    for persona, template in PERSONA_TEMPLATES.items():
        story = template.format(
            customer=customer,
            cloud=cloud,
            service=service,
            cost=round(cost, 2),
            threshold=threshold
        )

        cur.execute("""
            INSERT INTO stories (
                persona,
                customer_id,
                cloud_provider,
                story
            )
            VALUES (%s,%s,%s,%s)
        """, (
            persona,
            customer,
            cloud,
            story
        ))

conn.commit()
cur.close()
conn.close()

print("✅ Persona-based stories generated and stored in stories table")

