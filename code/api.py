"""
CloudStoryAI – FastAPI Service
Exposes FinOps engine data via REST APIs
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psycopg2

from intent_engine import detect_intent
from aggregation_engine import aggregate_signals, rank_signals
from narrative_engine import build_deterministic_narrative
from llm_engine import refine_with_llm


# -------------------------------------------------
# App bootstrap
# -------------------------------------------------
app = FastAPI(title="CloudStoryAI API", version="1.0")

app.mount(
    "/ui",
    StaticFiles(directory="/data/cloudstoryai/ui", html=True),
    name="ui"
)


# -------------------------------------------------
# Models
# -------------------------------------------------
class AIQuery(BaseModel):
    query: str
    persona: str = "cfo"


# -------------------------------------------------
# Database helper
# -------------------------------------------------
def get_db():
    return psycopg2.connect(
        dbname="cloudstoryai",
        user="cloudstory",
        password="cloudstory_pwd",
        host="127.0.0.1",
        port=5432
    )


# -------------------------------------------------
# 🆕 FinOps Daily Cost Endpoint
# -------------------------------------------------
@app.get("/finops/daily-cost")
def daily_cost():

    try:
        conn = get_db()
        cur = conn.cursor()

        # If you created materialized view mv_daily_cost
        cur.execute("""
            SELECT record_date,
                   SUM(cost_amount) AS total_cost,
                   COUNT(DISTINCT service_name) AS services
            FROM raw_cost
            GROUP BY record_date
            ORDER BY record_date;
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [
            {
                "date": str(r[0]),
                "total_cost": float(r[1]) if r[1] else 0.0,
                "services": r[2]
            }
            for r in rows
        ]

    except Exception as e:
        print("❌ DAILY COST ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# AI Query Endpoint
# -------------------------------------------------
@app.post("/ai/query")
def ai_query(req: AIQuery):

    print("🔥 AI QUERY ENDPOINT HIT")

    try:
        intent = detect_intent(req.query)["intent"]
        print(f"🧠 Detected intent: {intent}")

        conn = get_db()
        signals = aggregate_signals(conn, intent)

        ranked_signals = (
            rank_signals(signals, req.persona)
            if signals else []
        )

        conn.close()

        print("📊 SIGNALS RETURNED:", ranked_signals)

        deterministic_story = build_deterministic_narrative(
            ranked_signals,
            req.persona
        )

        final_story = deterministic_story

        if ranked_signals:
            top = ranked_signals[0]

            llm_prompt = f"""
You are an enterprise FinOps AI assistant.

Persona: {req.persona}
Intent: {intent}

Top Signal:
Service: {top['service']}
Cost Impact: ${top['cost']}

Provide:
1. Clear explanation
2. Business impact
3. Technical reasoning
4. Action recommendation
5. ROI perspective

Be concise but executive-ready.
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

    except Exception as e:
        print("❌ ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/finops/cloud-summary")
def cloud_summary():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT cloud_provider, SUM(cost_amount)
            FROM raw_cost
            GROUP BY cloud_provider;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        summary = {
            "aws": 0.0,
            "azure": 0.0,
            "gcp": 0.0
        }

        for provider, cost in rows:
            key = provider.lower()
            if key in summary:
                summary[key] = float(cost)

        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# Root → UI
# -------------------------------------------------
@app.get("/")
def root():
    return RedirectResponse(url="/ui")

