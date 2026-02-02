-- ===============================
-- CloudStoryAI Core Tables
-- ===============================

CREATE TABLE raw_cost (
    id SERIAL PRIMARY KEY,
    record_date DATE,
    cloud_provider TEXT,
    service_name TEXT,
    resource_id TEXT,
    is_shared BOOLEAN,
    usage_quantity NUMERIC,
    usage_unit TEXT,
    cost_amount NUMERIC,
    customer_id TEXT,
    environment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE allocated_cost (
    id SERIAL PRIMARY KEY,
    record_date DATE,
    cloud_provider TEXT,
    service_name TEXT,
    shared_service_type TEXT,
    customer_id TEXT,
    allocation_method TEXT,
    allocated_cost NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    record_date DATE,
    customer_id TEXT,
    cloud_provider TEXT,
    service_name TEXT,
    observed_cost NUMERIC,
    expected_range TEXT,
    severity TEXT,
    finops_reasoning TEXT,
    detected_at TIMESTAMP
);

CREATE TABLE stories (
    id SERIAL PRIMARY KEY,
    persona TEXT,
    customer_id TEXT,
    cloud_provider TEXT,
    story TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

