# import os
# import pandas as pd
# from langchain.schema import Document
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings

# # ---- Optional: extend KB with CSV-derived "context cards"
# CSV_PATH = "/Users/ishashetye/Desktop/Projects/BeSafeOnTheRoad/driver_backend/lstm data.csv"  # if your CSV is in backend root

# BASE_DOCS = [
#     {"id": "lvl4", "text": "Risk level 4 (Critical): Immediate danger. Slow down at once."},
#     {"id": "lvl3", "text": "Risk level 3 (High): Increase following distance and reduce speed."},
#     {"id": "lvl2", "text": "Risk level 2 (Moderate): Be vigilant, maintain lane discipline."},
#     {"id": "lvl1", "text": "Risk level 1 (Low): Normal driving but stay cautious."},
#     {"id": "lvl0", "text": "Risk level 0 (Very Low): Safe conditions."},
#     {"id": "faq1", "text": "Stereo depth uses SGBM disparity; closer objects have higher disparity."},
#     {"id": "faq2", "text": "Speed is estimated from object track displacement across frames after calibration."},
#     {"id": "faq3", "text": "Driver distraction (e.g., texting) increases risk even at low speeds."},
#     {"id": "beh0", "text": "Safe driving: keep eyes on the road, hands on the wheel, maintain steady speed and lane position."},
#     {"id": "beh1", "text": "Texting while driving: immediately stop texting, place phone away, and refocus on the road."},
#     {"id": "beh2", "text": "Phone call while driving: switch to hands-free or pull over if attention is reduced."},
#     {"id": "dist1", "text": "Safe following distance: use at least a 3-second gap; increase to 4–6 seconds in rain or low visibility."},
#     {"id": "rain1", "text": "Driving in rain: reduce speed, increase following distance, avoid sudden braking, and keep headlights on."},
# ]

# def load_csv_context_cards():
#     if not os.path.exists(CSV_PATH):
#         return []

#     df = pd.read_csv(CSV_PATH)
#     cards = []

#     # These column names may differ in your CSV; adjust once if needed.
#     # We'll try common ones safely:
#     col_risk = next((c for c in df.columns if "risk" in c.lower()), None)
#     col_depth = next((c for c in df.columns if "depth" in c.lower()), None)
#     col_speed = next((c for c in df.columns if "speed" in c.lower()), None)
#     col_beh = next((c for c in df.columns if "behav" in c.lower() or "driver" in c.lower()), None)

#     # Sample a few rows to avoid huge KB
#     sample = df.sample(min(200, len(df)), random_state=42)

#     for i, row in sample.iterrows():
#         risk = row[col_risk] if col_risk else "NA"
#         depth = row[col_depth] if col_depth else "NA"
#         speed = row[col_speed] if col_speed else "NA"
#         beh = row[col_beh] if col_beh else "NA"

#         text = (
#             f"Observed driving context: risk_level={risk}, depth={depth}, speed={speed}, behavior={beh}. "
#             f"Recommendation: if risk is elevated, reduce speed, increase distance, and avoid distractions."
#         )
#         cards.append({"id": f"csv_{i}", "text": text})

#     return cards

# def main():
#     os.makedirs("data", exist_ok=True)

#     docs = BASE_DOCS + load_csv_context_cards()
#     langchain_docs = []

#     for d in docs:
#         langchain_docs.append(
#             Document(
#                 page_content=d["text"],
#                 metadata={"id": d["id"]}
#             )
#         )

#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#     db = FAISS.from_documents(langchain_docs, embeddings)
#     db.save_local("data/faiss_index")

#     print("✅ Built LangChain FAISS index at data/faiss_index")
#     print(f"✅ Total docs indexed: {len(langchain_docs)}")

# if __name__ == "__main__":
#     main()

import os, json
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

class STEmbeddings(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text):
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()


def main():
    os.makedirs("data", exist_ok=True)

    # Load your KB
    with open("data/rag_meta.json", "r") as f:
        docs_json = json.load(f)

    docs = []
    for d in docs_json:
        docs.append(Document(page_content=d["text"], metadata={k: v for k, v in d.items() if k != "text"}))

    embeddings = STEmbeddings("all-MiniLM-L6-v2")

    db = FAISS.from_documents(docs, embeddings)
    db.save_local("data/faiss_index")

    print("✅ Built LangChain FAISS index at data/faiss_index")
    print("✅ Total docs indexed:", len(docs))


if __name__ == "__main__":
    main()
