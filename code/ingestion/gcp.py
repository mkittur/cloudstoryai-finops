import psycopg2
from google.cloud import bigquery
from code.config import DB_CONFIG

PROJECT_ID = "sigma-nimbus-446013-k2"
DATASET_ID = "cloudstory_billing_query"
TABLE_ID = "gcp_billing_export_resource_v1_014483_5554EB_94329C"


def ingest_gcp_cost():

    print("Starting GCP ingestion...")

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            DATE(usage_start_time) AS usage_date,
            service.description AS service_name,
            SUM(cost) AS total_cost
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        GROUP BY usage_date, service_name
        ORDER BY usage_date
    """

    results = client.query(query)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    inserted = 0

    for row in results:
        cur.execute("""
            INSERT INTO raw_cost (
                record_date,
                cloud_provider,
                service_name,
                customer_id,
                cost_amount
            )
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT ON CONSTRAINT raw_cost_unique
            DO UPDATE SET cost_amount = EXCLUDED.cost_amount
        """, (
            row.usage_date,
            "gcp",
            row.service_name,
            "default_customer",
            float(row.total_cost or 0)
        ))

        inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"GCP ingestion completed. Rows processed: {inserted}")


if __name__ == "__main__":
    ingest_gcp_cost()

