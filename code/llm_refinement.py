# llm_refinement.py
import requests

def refine_with_llm(text: str) -> str:
    payload = {
        "model": "mistral",
        "prompt": f"Rewrite clearly for executives:\n{text}",
        "stream": False
    }

    r = requests.post("http://localhost:11434/api/generate", json=payload)
    return r.json()["response"]

