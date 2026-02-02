import psycopg2
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def call_llm(prompt):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )
    r.raise_for_status()
    return r.json()["response"].strip()

conn = psycopg2.connect(
    dbname="cloudstoryai",
    user="cloudstory",
    password="cloudstory_pwd",
    host="/var/run/postgresql"
)
cur = conn.cursor()

cur.execute("""
    SELECT
        record_date,
        customer_id,
        cloud_provider,
        service_name,
        observed_cost,
        expected_range,
        finops_reasoning
    FROM anomalies
""")

rows = cur.fetchall()

for date, customer, cloud, service, cost, expected, reasoning in rows:
    prompt = f"""
You are a FinOps executive advisor.

Explain this anomaly in business language:

Customer: {customer}
Cloud: {cloud}
Service: {service}
Observed Cost: {cost}
Expected Range: {expected}

Explain:
1. What happened
2. Why it matters financially
3. What action should be taken

Keep it concise and executive-friendly.
"""

    story = call_llm(prompt)

    cur.execute("""
        INSERT INTO stories (
            persona,
            customer_id,
            cloud_provider,
            story
        )
        VALUES (%s,%s,%s,%s)
    """, (
        "executive_summary",
        customer,
        cloud,
        story
    ))

conn.commit()
cur.close()
conn.close()

print("✅ Local LLM refinement completed and stored")

