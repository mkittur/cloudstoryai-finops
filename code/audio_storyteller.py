"""
CloudStoryAI – Audio Storytelling Engine (Local TTS)
Renders governed AI stories into voice narratives
"""

import os
import psycopg2
import pyttsx3

AUDIO_DIR = "/data/cloudstoryai/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

engine = pyttsx3.init()
engine.setProperty('rate', 165)   # speech speed
engine.setProperty('volume', 1.0)

conn = psycopg2.connect(
    dbname="cloudstoryai",
    user="cloudstory",
    password="cloudstory_pwd",
    host="/var/run/postgresql"
)
cur = conn.cursor()

cur.execute("""
    SELECT id, persona, customer_id, story
    FROM stories
    WHERE persona = 'executive_summary'
      AND audio_path IS NULL
    LIMIT 3
""")

rows = cur.fetchall()

for story_id, persona, customer, text in rows:
    output_path = f"{AUDIO_DIR}/story_{story_id}_{persona}.wav"

    print(f"🎧 Generating audio for story {story_id}")

    engine.save_to_file(text, output_path)
    engine.runAndWait()

    cur.execute("""
        UPDATE stories
        SET audio_path = %s
        WHERE id = %s
    """, (output_path, story_id))

conn.commit()
cur.close()
conn.close()

print("✅ Audio stories generated and linked")

