"""
CloudStoryAI – FastAPI Service
Exposes FinOps engine data via REST APIs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psycopg2
import os

from intent_engine import detect_intent
from aggregation_engine import aggregate_signals, rank_signals
from narrative_engine import build_ai_narrative
from llm_refinement import refine_with_llm

# -------------------------------------------------
# App bootstrap (ONLY ONE FastAPI instance)
# -------------------------------------------------
app = FastAPI(title="CloudStoryAI API", version="1.0")

# Static UI mount
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
# Health
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# Cost APIs
# -------------------------------------------------
@app.get("/cost/raw")
def raw_cost(limit: int = 50):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT record_date, cloud_provider, service_name,
               customer_id, cost_amount
        FROM raw_cost
        ORDER BY record_date DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/cost/allocated")
def allocated_cost(limit: int = 50):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT record_date, cloud_provider, service_name,
               customer_id, allocated_cost
        FROM allocated_cost
        ORDER BY record_date DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# -------------------------------------------------
# Anomalies
# -------------------------------------------------
@app.get("/anomalies")
def anomalies():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT record_date, customer_id, cloud_provider,
               service_name, observed_cost, severity
        FROM anomalies
        ORDER BY detected_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# -------------------------------------------------
# Stories
# -------------------------------------------------
@app.get("/stories")
def stories(persona: str = Query(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, customer_id, cloud_provider, story
        FROM stories
        WHERE persona = %s
        ORDER BY created_at DESC
    """, (persona,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# -------------------------------------------------
# Audio endpoint
# -------------------------------------------------
@app.get("/stories/audio/{story_id}")
def get_story_audio(story_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT audio_path
        FROM stories
        WHERE id = %s
    """, (story_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="Audio not available")

    if not os.path.exists(row[0]):
        raise HTTPException(status_code=404, detail="Audio file missing")

    return FileResponse(row[0], media_type="audio/wav")

# -------------------------------------------------
# AI Query (INTENT-AWARE)
# -------------------------------------------------
@app.post("/ai/query")
def ai_query(req: AIQuery):
    print("🔥 AI QUERY ENDPOINT HIT")

    intent = detect_intent(req.query)["intent"]
    print(f"🧠 Detected intent: {intent}")
    print("INTENT RETURNED:", intent)

    conn = get_db()

    signals = aggregate_signals(conn, intent)
    print("SIGNALS RETURNED:", signals)
    conn.close()
    narrative = build_ai_narrative(signals, req.persona, intent)
    #narrative = build_narrative(
        #signals,          # ranked_signals
        #req.persona       # persona
    

    return {
        "question": req.query,
        "persona": req.persona,
        "intent": intent,
        "summary": narrative,
        "signals": signals[:3]
    }

# -------------------------------------------------
# Root → UI
# -------------------------------------------------
@app.get("/")
def root():
    return RedirectResponse(url="/ui")

