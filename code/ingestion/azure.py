import requests
import psycopg2
from datetime import datetime

from code.config import DB_CONFIG


# Import secure credentials from keys folder
from keys.azure_credentials import (
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET,
    AZURE_SUBSCRIPTION_ID,
)


def get_token():
    url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "resource": "https://management.azure.com/"
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()

    return response.json()["access_token"]


def ingest_azure_cost():

    print("Starting Azure ingestion...")

    token = get_token()

    url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/providers/Microsoft.CostManagement/query?api-version=2023-03-01"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {
                    "name": "Cost",
                    "function": "Sum"
                }
            },
            "grouping": [
                {"type": "Dimension", "name": "ServiceName"}
            ]
        }
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    data = response.json()

    print("Status:", response.status_code)
    print("Rows returned:", len(data["properties"].get("rows", [])))

    rows = data["properties"].get("rows", [])

    if not rows:
        print("No Azure billing rows found.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    inserted = 0

    for row in rows:
        cost = float(row[0] or 0)
        usage_date_raw = str(row[1])  # Format: 20260223
        service = row[2]

        # Convert 20260223 → 2026-02-23
        usage_date = datetime.strptime(usage_date_raw, "%Y%m%d").date()

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
            usage_date,
            "azure",
            service,
            "default_customer",
            cost
        ))

        inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Azure ingestion completed. Rows processed: {inserted}")


if __name__ == "__main__":
    ingest_azure_cost()
