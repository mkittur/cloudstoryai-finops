import requests

resp = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": "Summarize why Kubernetes shared services cause cost spikes.",
        "stream": False
    },
    timeout=180
)

print(resp.json()["response"])

