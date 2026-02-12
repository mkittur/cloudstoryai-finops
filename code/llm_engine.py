import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def refine_with_llm(prompt: str):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:
            return response.json()["response"]

        return None

    except Exception as e:
        print("LLM error:", e)
        return None

