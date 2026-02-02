"""
CloudStoryAI – Anomaly Detection (Simulated)
Author: Mahantesh Kittur

Purpose:
- Simulate shared cloud resource costs across customers
- Detect abnormal spikes using simple statistical logic
- Emit anomaly_event.json for downstream AI storytelling

FinOps Context:
- Shared services (K8s / RDS) are hardest to charge back
- Anomalies often signal:
  - noisy neighbors
  - misconfigured workloads
  - runaway batch jobs
"""

import json
import random
from datetime import datetime, timedelta
import statistics

# -----------------------------
# Configuration
# -----------------------------
CUSTOMERS = ["Customer_A", "Customer_B", "Customer_C"]
CLOUDS = ["AWS", "GCP", "Azure"]
DAYS = 30

BASELINE_COST = {
    "Customer_A": 120,
    "Customer_B": 100,
    "Customer_C": 80,
}

ANOMALY_PROBABILITY = 0.1  # 10% chance of spike


# -----------------------------
# Generate simulated cost data
# -----------------------------
def generate_cost_data():
    data = []
    start_date = datetime.now() - timedelta(days=DAYS)

    for day in range(DAYS):
        date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")

        for customer in CUSTOMERS:
            for cloud in CLOUDS:
                cost = random.gauss(BASELINE_COST[customer], 10)

                # Inject anomaly
                if random.random() < ANOMALY_PROBABILITY:
                    cost *= random.uniform(2.5, 4.0)

                data.append({
                    "date": date,
                    "customer": customer,
                    "cloud": cloud,
                    "cost": round(cost, 2)
                })

    return data


# -----------------------------
# Detect anomalies
# -----------------------------
def detect_anomalies(data):
    anomalies = []

    grouped = {}
    for entry in data:
        key = (entry["customer"], entry["cloud"])
        grouped.setdefault(key, []).append(entry["cost"])

    for (customer, cloud), costs in grouped.items():
        mean = statistics.mean(costs)
        stdev = statistics.stdev(costs)

        for cost in costs:
            if cost > mean + 3 * stdev:
                anomalies.append({
                    "customer": customer,
                    "cloud": cloud,
                    "observed_cost": round(cost, 2),
                    "expected_range": f"{round(mean - stdev,2)}–{round(mean + stdev,2)}",
                    "severity": "HIGH",
                    "detected_at": datetime.utcnow().isoformat() + "Z",
                    "finops_reasoning": (
                        "Cost significantly exceeded historical baseline. "
                        "Likely causes include noisy neighbor effect, "
                        "misconfigured autoscaling, or unexpected workload spike."
                    )
                })

    return anomalies


# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    cost_data = generate_cost_data()
    anomalies = detect_anomalies(cost_data)

    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_records": len(cost_data),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies
    }

    with open("anomaly_event.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(cost_data)} cost records")
    print(f"Detected {len(anomalies)} anomalies")
    print("Output written to anomaly_event.json")

