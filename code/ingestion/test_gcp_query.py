from google.cloud import bigquery

PROJECT_ID = "sigma-nimbus-446013-k2"

client = bigquery.Client(project=PROJECT_ID)

query = """
SELECT
    DATE(usage_start_time) AS usage_date,
    service.description AS service_name,
    SUM(cost) AS total_cost
FROM `sigma-nimbus-446013-k2.cloudstory_billing_query.gcp_billing_export_resource_v1_014483_5554EB_94329C`
GROUP BY usage_date, service_name
ORDER BY usage_date DESC
LIMIT 10
"""

results = client.query(query)

for row in results:
    print(row)
