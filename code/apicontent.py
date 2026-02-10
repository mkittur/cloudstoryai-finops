from intent_engine import detect_intent
from aggregation_engine import aggregate_signals, rank_signals
from narrative_engine import build_narrative
from llm_refinement import refine_with_llm

@app.post("/ai/query")
def ai_query(req: AIQuery):
    intent = detect_intent(req.query)["intent"]

    conn = get_db()
    signals = aggregate_signals(conn, intent)
    ranked = rank_signals(signals, req.persona)
    conn.close()

    narrative = build_narrative(ranked, req.persona)

    refined = refine_with_llm(narrative)

    return {
        "intent": intent,
        "persona": req.persona,
        "summary": refined,
        "top_signals": ranked[:3]
    }

