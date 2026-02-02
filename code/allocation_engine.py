"""
CloudStoryAI – Shared Service Allocation Engine
Author: Mahantesh Kittur

Purpose:
Allocate shared service costs across customers using multiple strategies.

FinOps Context:
Shared services (Kubernetes, RDS) are the hardest to charge back.
This module provides transparent, explainable allocation logic.
"""

import json
from collections import defaultdict
from datetime import datetime


# -----------------------------
# Allocation Strategies
# -----------------------------

def equal_split(total_cost, customers):
    share = total_cost / len(customers)
    return {c: round(share, 2) for c in customers}


def weighted_split(total_cost, weights):
    total_weight = sum(weights.values())
    return {
        c: round((w / total_weight) * total_cost, 2)
        for c, w in weights.items()
    }


def usage_based_split(total_cost, usage):
    total_usage = sum(usage.values())
    return {
        c: round((u / total_usage) * total_cost, 2)
        for c, u in usage.items()
    }


# -----------------------------
# Sample Shared Service Input
# -----------------------------
shared_service_event = {
    "record_date": "2026-01-30",
    "cloud_provider": "aws",
    "service_name": "EKS",
    "is_shared": True,
    "shared_service_type": "k8s",
    "total_cost": 300.00,
    "customers": ["Customer_A", "Customer_B", "Customer_C"],

    # Simulated usage metrics (e.g., vCPU-hours)
    "usage": {
        "Customer_A": 120,
        "Customer_B": 80,
        "Customer_C": 40
    },

    # Optional weighting (business priority / SLA)
    "weights": {
        "Customer_A": 0.5,
        "Customer_B": 0.3,
        "Customer_C": 0.2
    }
}


# -----------------------------
# Allocation Execution
# -----------------------------
def allocate(event, method):
    customers = event["customers"]
    total_cost = event["total_cost"]

    if method == "equal":
        allocation = equal_split(total_cost, customers)

    elif method == "weighted":
        allocation = weighted_split(total_cost, event["weights"])

    elif method == "usage":
        allocation = usage_based_split(total_cost, event["usage"])

    else:
        raise ValueError(f"Unsupported allocation method: {method}")

    results = []
    for customer, cost in allocation.items():
        results.append({
            "record_date": event["record_date"],
            "cloud_provider": event["cloud_provider"],
            "service_name": event["service_name"],
            "shared_service_type": event["shared_service_type"],
            "customer_id": customer,
            "allocation_method": method,
            "allocated_cost": cost,
            "processed_at": datetime.utcnow().isoformat() + "Z"
        })

    return results


# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    output = {
        "equal_split": allocate(shared_service_event, "equal"),
        "weighted_split": allocate(shared_service_event, "weighted"),
        "usage_based_split": allocate(shared_service_event, "usage")
    }

    with open("allocation_output.json", "w") as f:
        json.dump(output, f, indent=2)

    print("Shared service allocation completed")
    print("Output written to allocation_output.json")

