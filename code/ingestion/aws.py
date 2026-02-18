import boto3
import psycopg2
import gzip
import csv
import io
from psycopg2.extras import execute_batch
from code.config import DB_CONFIG

# -----------------------------
# Configuration
# -----------------------------


BUCKET_NAME = "cloudstoryai-cur-bucket"
CUR_PREFIX = "cloudstoryai-cur/"   # IMPORTANT


# -----------------------------
# Ingestion Function
# -----------------------------
def ingest_aws_cur():
    print("Starting AWS CUR ingestion...")

    session = boto3.Session(profile_name="cloudstoryai")
    s3 = session.client("s3", region_name="ap-south-1")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT current_database();")
    print("Connected to DB:", cur.fetchone()[0])

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=BUCKET_NAME,
        Prefix=CUR_PREFIX
    )

    total_rows = 0
    total_files = 0

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]

            # Process only CUR CSV files
            if not key.endswith(".csv.gz"):
                continue

            print(f"Processing file: {key}")
            total_files += 1

            try:
                file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                gz = gzip.GzipFile(fileobj=file_obj["Body"])
                reader = csv.DictReader(io.TextIOWrapper(gz))

                batch_rows = []

                for row in reader:
                    batch_rows.append((
                        row["lineItem/UsageStartDate"],
                        "aws",
                        row["product/ProductName"],
                        row["lineItem/UsageAccountId"],
                        row["lineItem/UnblendedCost"]
                    ))

                if batch_rows:
                    execute_batch(cur, """
                        INSERT INTO raw_cost (
                            record_date,
                            cloud_provider,
                            service_name,
                            customer_id,
                            cost_amount
                        )
                        VALUES (%s::date,%s,%s,%s,%s)
                        ON CONFLICT ON CONSTRAINT raw_cost_unique
                        DO UPDATE SET cost_amount = EXCLUDED.cost_amount
                    """, batch_rows)

                    total_rows += len(batch_rows)

            except Exception as e:
                print(f"Error processing {key}: {e}")

    conn.commit()
    cur.close()
    conn.close()

    print(f"Ingestion completed. Files processed: {total_files}, Rows inserted/updated: {total_rows}")
# -----------------------------
# Run Script
# -----------------------------
if __name__ == "__main__":
    ingest_aws_cur()

