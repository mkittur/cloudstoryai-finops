# CloudStoryAI – Canonical Multi-Cloud Cost & Usage Schema (v1)

## Purpose
A cloud-agnostic schema to normalize cost and usage data across AWS, GCP, and Azure,
with explicit support for shared services and FinOps chargeback use cases.

---

## Core Dimensions

| Field | Type | Description |
|-----|----|------------|
| record_date | date | Usage / billing date |
| cloud_provider | string | aws / gcp / azure |
| account_id | string | Cloud account / subscription |
| region | string | Cloud region |
| service_name | string | e.g. EKS, GKE, RDS, VM |
| resource_id | string | Logical resource identifier |

---

## Cost & Usage Metrics

| Field | Type | Description |
|-----|----|------------|
| usage_quantity | float | Normalized usage units |
| usage_unit | string | vCPU-hours, GB-hours, requests |
| cost_amount | float | Cost in billing currency |
| currency | string | USD |
| pricing_model | string | on-demand / reserved / spot |

---

## Shared Service Attribution

| Field | Type | Description |
|-----|----|------------|
| is_shared | boolean | True if shared service |
| shared_service_type | string | k8s / rds / cache |
| allocation_method | string | equal / weighted / usage |
| allocated_cost | float | Cost after allocation |

---

## Business Context

| Field | Type | Description |
|-----|----|------------|
| customer_id | string | Internal / external customer |
| workload_id | string | App / microservice |
| environment | string | prod / staging / dev |
| owner_team | string | Engineering owner |

---

## Governance & AI Metadata

| Field | Type | Description |
|-----|----|------------|
| anomaly_flag | boolean | Detected anomaly |
| anomaly_score | float | Severity score |
| finops_notes | string | Human/AI reasoning |
| processed_at | timestamp | Pipeline timestamp |

---

## Design Principles
- All cloud-native fields must map into this schema
- Shared services must be explicitly marked
- Allocation must be transparent and explainable
- Schema must support AI narrative generation

---

## Future Extensions
- Kubernetes namespace / pod labels
- SaaS tenant ID
- Carbon emissions
- AI-generated optimization actions

