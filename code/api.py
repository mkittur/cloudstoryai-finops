"""
CloudStoryAI – FastAPI Service
Exposes FinOps engine data via REST APIs
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os

from fastapi import FastAPI, Query
import psycopg2

app = FastAPI(title="CloudStoryAI API", version="1.0")

def get_db():
    return psycopg2.connect(
        dbname="cloudstoryai",
        user="cloudstory",
        password="cloudstory_pwd",
        host="/var/run/postgresql"
    )

@app.get("/health")
def health():
    return {"status": "ok"}

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

@app.get("/stories")
def stories(persona: str = Query(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT customer_id, cloud_provider, story
        FROM stories
        WHERE persona = %s
        ORDER BY created_at DESC
    """, (persona,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
def get_db():
    return psycopg2.connect(
        dbname="cloudstoryai",
        user="cloudstory",
        password="cloudstory_pwd",
        host="/var/run/postgresql"
    )
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
        raise HTTPException(
            status_code=404,
            detail="Audio not available for this story"
        )

    audio_path = row[0]

    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=404,
            detail="Audio file not found on disk"
        )

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=os.path.basename(audio_path)
    )

