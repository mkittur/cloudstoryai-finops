"""
CloudStoryAI – FastAPI Service
Exposes FinOps engine data via REST APIs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psycopg2
import os
from intent_engine import detect_intent
from fastapi.responses import RedirectResponse


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
# AI Query
# -------------------------------------------------

@app.post("/ai/query")

def ai_query(req: AIQuery):
    print("🔥 AI QUERY ENDPOINT HIT")

    intent_data = detect_intent(req.query)
    intent = intent_data["intent"]

    print(f"🧠 Detected intent: {intent}")

    conn = get_db()
    cur = conn.cursor()
    story = row[0]
    audio = row[1] if len(row) > 1 else None

    if intent == "SAVINGS":
        cur.execute("""
            SELECT story, COALESCE(audio_path, '')
            FROM stories
            WHERE persona = %s
              AND story ILIKE '%save%'
            ORDER BY created_at DESC
            LIMIT 1
        """, (req.persona,))
        row = cur.fetchone()

    elif intent == "COST_SPIKE":
        cur.execute("""
            SELECT story, audio_path
            FROM stories
            WHERE persona = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (req.persona,))

    else:
        cur.execute("""
            SELECT story, audio_path
            FROM stories
            WHERE persona = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (req.persona,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {
            "summary": "No relevant insight found",
            "intent": intent
        }

    return {
        "question": req.query,
        "persona": req.persona,
        "intent": intent,
        "summary": story,
        "confidence": 0.82,
        "audio_url": audio
    }


@app.get("/")
def root():
    return RedirectResponse(url="/ui")

