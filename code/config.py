import os

DB_CONFIG = {
    "dbname": "cloudstoryai",
    "user": "cloudstory",
    "password": os.getenv("DB_PASSWORD", "cloudstory_pwd"),
    "host": "127.0.0.1",
    "port": 5432
}

LLM_CONFIG = {
    "endpoint": "http://localhost:11434/api/generate",
    "model": "mistral"
}

API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000
}

