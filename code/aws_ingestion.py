import boto3
import psycopg2
import gzip
import csv
import io

def ingest_aws_cur():
    s3 = boto3.client(
        "s3",
        aws_access_key_id="YOUR_KEY",
        aws_secret_access_key="YOUR_SECRET",
        region_name="ap-south-1"
    )

    bucket = "cloudstoryai-cur-bucket"
    response = s3.list_objects_v2(Bucket=bucket)

    for obj in response.get("Contents", []):
        key = obj["Key"]

        if key.endswith(".csv.gz"):
            file_obj = s3.get_object(Bucket=bucket, Key=key)
            gz = gzip.GzipFile(fileobj=file_obj["Body"])
            reader = csv.DictReader(io.TextIOWrapper(gz))

            conn = psycopg2.connect(...)
            cur = conn.cursor()

            for row in reader:
                cur.execute("""
                    INSERT INTO raw_cost (
                        record_date,
                        cloud_provider,
                        service_name,
                        customer_id,
                        cost_amount
                    )
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    row["lineItem/UsageStartDate"],
                    "aws",
                    row["product/ProductName"],
                    row["lineItem/UsageAccountId"],
                    row["lineItem/UnblendedCost"]
                ))

            conn.commit()
            cur.close()
            conn.close()

