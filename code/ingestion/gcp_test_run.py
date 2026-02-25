from google.cloud import bigquery

client = bigquery.Client(project="sigma-nimbus-446013-k2")

query = """
SELECT COUNT(*) as total_rows
FROM `sigma-nimbus-446013-k2.cloudstory_billing_query.gcp_billing_export_resource_v1_014483_5554EB_94329C`
"""

results = client.query(query)

for row in results:
    print("Total rows:", row.total_rows)
