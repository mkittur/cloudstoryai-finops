# Architecture Overview

CloudStoryAI is designed as a layered platform:

## Data Foundation
- PostgreSQL as single source of truth
- Raw cost, allocated cost, anomalies, stories, governance tables

## Financial Core
- Deterministic shared-service allocation engine
- Transparent allocation methods

## Signal Layer
- Statistical anomaly detection
- FinOps reasoning persisted with anomalies

## Intelligence Layer
- Persona-based narratives
- Local LLM refinement (no external APIs)

## Governance Layer
- AI confidence scoring
- ROI estimation
- Approval / Monitor / Reject decisions

## Presentation Layer
- FastAPI (Swagger UI)
- PowerBI dashboards via SQL views

