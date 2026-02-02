"""
CloudStoryAI – Raw Cost Ingestion (Simulated)
Purpose:
Insert simulated multi-cloud cost records into PostgreSQL.
"""

import psycopg2
import random
from datetime import datetime, timedelta

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
# Simulation Parameters
# -----------------------------
CUSTOMERS = ["Customer_A", "Customer_B", "Customer_C"]
CLOUDS = ["aws", "gcp", "azure"]
SERVICES = ["k8s", "rds"]
DAYS = 10

start_date = datetime.now() - timedelta(days=DAYS)

# -----------------------------
# Insert Data
# -----------------------------
for day in range(DAYS):
    record_date = (start_date + timedelta(days=day)).date()

    for cloud in CLOUDS:
        for service in SERVICES:
            is_shared = True
            base_cost = random.uniform(80, 150)

            for customer in CUSTOMERS:
                usage = random.uniform(10, 60)
                cost = base_cost * (usage / 100)

                cur.execute(
                    """
                    INSERT INTO raw_cost (
                        record_date,
                        cloud_provider,
                        service_name,
                        resource_id,
                        is_shared,
                        usage_quantity,
                        usage_unit,
                        cost_amount,
                        customer_id,
                        environment
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        record_date,
                        cloud,
                        service,
                        f"{service}-{cloud}",
                        is_shared,
                        round(usage, 2),
                        "vCPU-hours",
                        round(cost, 2),
                        customer,
                        "prod"
                    )
                )

conn.commit()
cur.close()
conn.close()

print("✅ Raw cost data inserted into PostgreSQL")

