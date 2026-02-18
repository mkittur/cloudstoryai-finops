from google.cloud import bigquery

def ingest_gcp():
    client = bigquery.Client.from_service_account_json("gcp_key.json")

    query = """
        SELECT
            usage_start_time,
            service.description,
            project.id,
            cost
        FROM `billing_export.dataset.table`
    """

    rows = client.query(query)

    for row in rows:
        # insert into raw_cost

