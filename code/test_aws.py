import boto3

session = boto3.Session(profile_name="cloudstoryai")
ce = session.client("ce", region_name="us-east-1")

response = ce.get_cost_and_usage(
    TimePeriod={
        'Start': '2025-02-01',
        'End': '2025-02-10'
    },
    Granularity='DAILY',
    Metrics=['UnblendedCost']
)

print(response)

