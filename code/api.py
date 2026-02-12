
# -------------------------------------------------
# AI Query (INTENT-AWARE + SIGNAL + LLM)
# -------------------------------------------------

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psycopg2
import os

from intent_engine import detect_intent
from aggregation_engine import aggregate_signals, rank_signals
from narrative_engine import build_deterministic_narrative
app = FastAPI(title="CloudStoryAI API", version="1.0")

app.mount(
    "/ui",
    StaticFiles(directory="/data/cloudstoryai/ui", html=True),
    name="ui"
)

class AIQuery(BaseModel):
    query: str
    persona: str = "cfo"


def get_db():
    return psycopg2.connect(
        dbname="cloudstoryai",
        user="cloudstory",
        password="cloudstory_pwd",
        host="127.0.0.1",
        port=5432
    )

@app.post("/ai/query")
def ai_query(req: AIQuery):
    print("🔥 AI QUERY ENDPOINT HIT")

    # 1️⃣ Detect intent
    intent = detect_intent(req.query)["intent"]
    print(f"🧠 Detected intent: {intent}")

    # 2️⃣ Get DB connection
    conn = get_db()

    # 3️⃣ Aggregate signals from DB
    signals = aggregate_signals(conn, intent)

    # 4️⃣ Rank signals (if ranking logic exists)
    ranked_signals = rank_signals(signals) if signals else []

    conn.close()

    print("📊 SIGNALS RETURNED:", ranked_signals)

    # 5️⃣ Build deterministic narrative
    deterministic_story = build_narrative(ranked_signals, req.persona)

    # 6️⃣ LLM refinement (only if we have signals)
    final_story = deterministic_story

    if ranked_signals:
        llm_prompt = f"""
You are a FinOps AI assistant.

Persona: {req.persona}
Intent: {intent}

Top Insight:
Service: {ranked_signals[0]['service']}
Cost Impact: ${ranked_signals[0]['cost']}

Explain:
1. What happened
2. Business impact
3. Technical reasoning
4. Recommended action
5. ROI perspective

Be concise and executive-ready.
"""

        refined = refine_with_llm(llm_prompt)

        if refined:
            final_story = refined

    return {
        "question": req.query,
        "persona": req.persona,
        "intent": intent,
        "summary": final_story,
        "signals": ranked_signals[:3]
    }


@app.get("/")
def root():
    return RedirectResponse(url="/ui")
