import csv, json, os

CSV_PATH = "lstm_data.csv"
OUT_PATH = "data/rag_meta.json"

BASE_DOCS = [
    {"id": "lvl4", "text": "Risk level 4 (Critical): Immediate danger. Slow down at once.", "type": "risk"},
    {"id": "lvl3", "text": "Risk level 3 (High): Increase following distance and reduce speed.", "type": "risk"},
    {"id": "lvl2", "text": "Risk level 2 (Moderate): Be vigilant, maintain lane discipline.", "type": "risk"},
    {"id": "lvl1", "text": "Risk level 1 (Low): Normal driving but stay cautious.", "type": "risk"},
    {"id": "lvl0", "text": "Risk level 0 (Very Low): Safe conditions.", "type": "risk"},
    {"id": "faq1", "text": "Stereo depth uses SGBM disparity; closer objects have higher disparity.", "type": "faq"},
    {"id": "faq2", "text": "Speed is estimated from object track displacement across frames after calibration.", "type": "faq"},
    {"id": "faq3", "text": "Driver distraction increases risk even at low speeds.", "type": "behavior"},
]

docs = BASE_DOCS.copy()

# --- Optional: ingest LSTM CSV ---
if os.path.exists(CSV_PATH):
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            docs.append({
                "id": f"lstm_{i}",
                "text": f"At speed {row['speed']} km/h and distance {row['distance']} m, risk level was {row['risk_level']}.",
                "type": "lstm",
                "risk_level": int(row["risk_level"])
            })

os.makedirs("data", exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(docs, f, indent=2)

print(f"✅ Knowledge base written to {OUT_PATH} ({len(docs)} docs)")
