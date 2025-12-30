# # # from flask import Flask, request, jsonify, send_file
# # # from flask_cors import CORS
# # # import time, json, os, csv

# # # from rag_chain import RagChain
# # # from risk import risk_to_message
# # # from report import save_report

# # # app = Flask(__name__)
# # # CORS(app)

# # # rag = RagChain()
# # # event_log = []

# # # # reload JSON logs (optional)
# # # if os.path.exists("event_log.json"):
# # #     try:
# # #         with open("event_log.json", "r") as f:
# # #             event_log = json.load(f)
# # #     except Exception:
# # #         event_log = []

# # # def _save_events():
# # #     try:
# # #         with open("event_log.json", "w") as f:
# # #             json.dump(event_log[-500:], f, indent=2)
# # #     except Exception as e:
# # #         print("⚠️ Could not persist events:", e)

# # # @app.route("/health", methods=["GET"])
# # # def health():
# # #     return jsonify({"ok": True})

# # # @app.route("/risk_alert", methods=["POST"])
# # # def risk_alert():
# # #     data = request.get_json(force=True) or {}
# # #     lvl = int(data.get("risk_level", 0))
# # #     msg = risk_to_message(lvl)
# # #     ts_ms = int(time.time() * 1000)

# # #     event_log.append({
# # #         "type": "risk_alert",
# # #         "timestamp_query": ts_ms / 1000.0,
# # #         "timestamp_resp": ts_ms / 1000.0,
# # #         "level": lvl,
# # #         "message": msg,
# # #         "success": True
# # #     })
# # #     _save_events()
# # #     return jsonify({"message": msg, "timestamp_ms": ts_ms})

# # # @app.route("/ask", methods=["POST"])
# # # def ask():
# # #     data = request.get_json(force=True) or {}
# # #     q = (data.get("query") or "").strip()
# # #     ctx = data.get("context") or {}

# # #     t_q = time.time()
# # #     if not q:
# # #         return jsonify({
# # #             "answer": "",
# # #             "chunks": [],
# # #             "latency_sec": 0.0,
# # #             "success": False,
# # #             "timestamp_query": int(t_q * 1000),
# # #             "timestamp_resp": int(t_q * 1000),
# # #             "used_llm": False
# # #         })

# # #     try:
# # #         out = rag.ask(q, context=ctx)
# # #         answer = out["answer"]
# # #         chunks = out["chunks"]
# # #         used_llm = out["used_llm"]
# # #         latency = out["latency_sec"]
# # #         success = True
# # #     except Exception as e:
# # #         answer = f"Temporary issue: {e}"
# # #         chunks = []
# # #         used_llm = False
# # #         latency = 0.0
# # #         success = False

# # #     t_r = time.time()

# # #     event_log.append({
# # #         "type": "ask",
# # #         "timestamp_query": t_q,
# # #         "timestamp_resp": t_r,
# # #         "query": q,
# # #         "answer": answer,
# # #         "chunks": chunks,
# # #         "success": success,
# # #         "used_llm": used_llm,
# # #         "latency_sec": latency,
# # #         "context": ctx
# # #     })
# # #     _save_events()

# # #     return jsonify({
# # #         "answer": answer,
# # #         "chunks": chunks,
# # #         "latency_sec": latency,
# # #         "success": success,
# # #         "timestamp_query": int(t_q * 1000),
# # #         "timestamp_resp": int(t_r * 1000),
# # #         "used_llm": used_llm
# # #     })

# # # @app.route("/events", methods=["GET"])
# # # def events():
# # #     lines = []
# # #     for e in event_log[-50:]:
# # #         if isinstance(e, dict):
# # #             ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(e.get("timestamp_query", 0))))
# # #             if e.get("type") == "ask":
# # #                 q = (e.get("query") or "")[:48]
# # #                 a = (e.get("answer") or "")[:64]
# # #                 lines.append(f"{ts} | Q: {q} | A: {a}")
# # #             elif e.get("type") == "risk_alert":
# # #                 lines.append(f"{ts} | L{e.get('level', '?')} | {e.get('message', '')}")
# # #         else:
# # #             lines.append(str(e))
# # #     return jsonify(lines)

# # # @app.route("/report", methods=["GET"])
# # # def report():
# # #     entries = []
# # #     for e in event_log:
# # #         if isinstance(e, dict) and e.get("type") in ("risk_alert", "ask"):
# # #             ts_ms = int(float(e.get("timestamp_query", 0)) * 1000)
# # #             lvl = e.get("level", -1)
# # #             msg = e.get("message", e.get("answer", "")) or ""
# # #             entries.append((ts_ms, lvl, msg))

# # #     path = save_report(entries, out_path="trip_report.pdf")
# # #     return send_file(path, as_attachment=True)

# # # @app.route("/export_csv", methods=["GET"])
# # # def export_csv():
# # #     try:
# # #         out_path = "results.csv"
# # #         fieldnames = ["timestamp_query", "timestamp_resp", "latency_sec", "success", "query", "answer", "used_llm"]

# # #         rows = []
# # #         for e in event_log:
# # #             if isinstance(e, dict) and e.get("type") == "ask":
# # #                 rows.append({
# # #                     "timestamp_query": e.get("timestamp_query", 0),
# # #                     "timestamp_resp": e.get("timestamp_resp", 0),
# # #                     "latency_sec": e.get("latency_sec", 0),
# # #                     "success": e.get("success", False),
# # #                     "query": (e.get("query") or "").replace("\n", " ").strip(),
# # #                     "answer": (e.get("answer") or "").replace("\n", " ").strip(),
# # #                     "used_llm": e.get("used_llm", False)
# # #                 })

# # #         with open(out_path, "w", newline="", encoding="utf-8") as f:
# # #             w = csv.DictWriter(f, fieldnames=fieldnames)
# # #             w.writeheader()
# # #             for r in rows:
# # #                 w.writerow(r)

# # #         return jsonify({"ok": True, "rows": len(rows), "path": os.path.abspath(out_path)})

# # #     except Exception as e:
# # #         return jsonify({"ok": False, "error": str(e)}), 500

# # # if __name__ == "__main__":
# # #     app.run(host="0.0.0.0", port=8000)

# # # server.py
# # from flask import Flask, request, jsonify, send_file
# # from flask_cors import CORS
# # import time, json, os, csv

# # from rag_chain import RagChain
# # from risk import risk_to_message
# # from report import save_report

# # app = Flask(__name__)
# # CORS(app)

# # rag = RagChain(index_dir="data/faiss_index")
# # event_log = []

# # # reload JSON logs (optional)
# # if os.path.exists("event_log.json"):
# #     try:
# #         with open("event_log.json", "r", encoding="utf-8") as f:
# #             event_log = json.load(f)
# #     except Exception:
# #         event_log = []

# # def _save_events():
# #     try:
# #         with open("event_log.json", "w", encoding="utf-8") as f:
# #             json.dump(event_log[-500:], f, indent=2)
# #     except Exception as e:
# #         print("⚠️ Could not persist events:", e)

# # @app.route("/health", methods=["GET"])
# # def health():
# #     return jsonify({"ok": True})

# # @app.route("/risk_alert", methods=["POST"])
# # def risk_alert():
# #     data = request.get_json(force=True) or {}
# #     lvl = int(data.get("risk_level", 0))
# #     msg = risk_to_message(lvl)
# #     ts_ms = int(time.time() * 1000)

# #     event_log.append({
# #         "type": "risk_alert",
# #         "timestamp_query": ts_ms / 1000.0,
# #         "timestamp_resp": ts_ms / 1000.0,
# #         "level": lvl,
# #         "message": msg,
# #         "success": True
# #     })
# #     _save_events()
# #     return jsonify({"message": msg, "timestamp_ms": ts_ms})

# # @app.route("/ask", methods=["POST"])
# # def ask():
# #     data = request.get_json(force=True) or {}
# #     q = (data.get("query") or "").strip()
# #     ctx = data.get("context") or {}

# #     t_q = time.time()
# #     if not q:
# #         return jsonify({
# #             "answer": "",
# #             "chunks": [],
# #             "latency_sec": 0.0,
# #             "success": False,
# #             "timestamp_query": int(t_q * 1000),
# #             "timestamp_resp": int(t_q * 1000),
# #             "used_llm": False
# #         })

# #     try:
# #         out = rag.ask(q, context=ctx, k=3)
# #         answer = out["answer"]
# #         chunks = out["chunks"]
# #         used_llm = out["used_llm"]
# #         latency = out["latency_sec"]
# #         success = True
# #     except Exception as e:
# #         answer = f"Temporary issue: {e}"
# #         chunks = []
# #         used_llm = False
# #         latency = 0.0
# #         success = False

# #     t_r = time.time()

# #     event_log.append({
# #         "type": "ask",
# #         "timestamp_query": t_q,
# #         "timestamp_resp": t_r,
# #         "query": q,
# #         "answer": answer,
# #         "chunks": chunks,
# #         "success": success,
# #         "used_llm": used_llm,
# #         "latency_sec": latency,
# #         "context": ctx
# #     })
# #     _save_events()

# #     return jsonify({
# #         "answer": answer,
# #         "chunks": chunks,
# #         "latency_sec": latency,
# #         "success": success,
# #         "timestamp_query": int(t_q * 1000),
# #         "timestamp_resp": int(t_r * 1000),
# #         "used_llm": used_llm
# #     })

# # @app.route("/events", methods=["GET"])
# # def events():
# #     lines = []
# #     for e in event_log[-50:]:
# #         if isinstance(e, dict):
# #             ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(e.get("timestamp_query", 0))))
# #             if e.get("type") == "ask":
# #                 q = (e.get("query") or "")[:48]
# #                 a = (e.get("answer") or "")[:64]
# #                 lines.append(f"{ts} | Q: {q} | A: {a}")
# #             elif e.get("type") == "risk_alert":
# #                 lines.append(f"{ts} | L{e.get('level', '?')} | {e.get('message', '')}")
# #         else:
# #             lines.append(str(e))
# #     return jsonify(lines)

# # @app.route("/report", methods=["GET"])
# # def report():
# #     entries = []
# #     for e in event_log:
# #         if isinstance(e, dict) and e.get("type") in ("risk_alert", "ask"):
# #             ts_ms = int(float(e.get("timestamp_query", 0)) * 1000)
# #             lvl = e.get("level", -1)
# #             msg = e.get("message", e.get("answer", "")) or ""
# #             entries.append((ts_ms, lvl, msg))

# #     path = save_report(entries, out_path="trip_report.pdf")
# #     return send_file(path, as_attachment=True)

# # @app.route("/export_csv", methods=["GET"])
# # def export_csv():
# #     try:
# #         out_path = "results.csv"
# #         fieldnames = ["timestamp_query", "timestamp_resp", "latency_sec", "success", "query", "answer", "used_llm"]

# #         rows = []
# #         for e in event_log:
# #             if isinstance(e, dict) and e.get("type") == "ask":
# #                 rows.append({
# #                     "timestamp_query": e.get("timestamp_query", 0),
# #                     "timestamp_resp": e.get("timestamp_resp", 0),
# #                     "latency_sec": e.get("latency_sec", 0),
# #                     "success": e.get("success", False),
# #                     "query": (e.get("query") or "").replace("\n", " ").strip(),
# #                     "answer": (e.get("answer") or "").replace("\n", " ").strip(),
# #                     "used_llm": e.get("used_llm", False)
# #                 })

# #         with open(out_path, "w", newline="", encoding="utf-8") as f:
# #             w = csv.DictWriter(f, fieldnames=fieldnames)
# #             w.writeheader()
# #             for r in rows:
# #                 w.writerow(r)

# #         return jsonify({"ok": True, "rows": len(rows), "path": os.path.abspath(out_path)})

# #     except Exception as e:
# #         return jsonify({"ok": False, "error": str(e)}), 500

# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=8000)

# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import time, json, os, csv

# from rag_chain import RagChain
# from risk import risk_to_message
# from report import save_report

# app = Flask(__name__)
# CORS(app)

# rag = RagChain()

# # -------------------------------
# # Event log (in-memory + persisted)
# # -------------------------------
# event_log = []

# if os.path.exists("event_log.json"):
#     try:
#         with open("event_log.json", "r") as f:
#             event_log = json.load(f)
#     except Exception:
#         event_log = []


# # -------------------------------
# # Health
# # -------------------------------
# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"ok": True})


# # -------------------------------
# # Risk alert endpoint (from LSTM)
# # -------------------------------
# @app.route("/risk_alert", methods=["POST"])
# def risk_alert():
#     data = request.get_json(force=True)
#     lvl = int(data.get("risk_level", 0))
#     msg = risk_to_message(lvl)

#     ts = time.time()

#     event_log.append({
#         "type": "risk_alert",
#         "timestamp_query": ts,
#         "timestamp_resp": ts,
#         "level": lvl,
#         "message": msg,
#         "success": True
#     })
#     _save_events()

#     return jsonify({"message": msg, "timestamp_ms": int(ts * 1000)})


# # -------------------------------
# # ASK (LangChain RAG)
# # -------------------------------
# @app.route("/ask", methods=["POST"])
# def ask():
#     data = request.get_json(force=True)
#     q = (data.get("query") or "").strip()
#     ctx = data.get("context") or {}

#     t_q = time.time()

#     if not q:
#         return jsonify({
#             "answer": "",
#             "chunks": [],
#             "success": False,
#             "timestamp_query": int(t_q * 1000),
#             "timestamp_resp": int(t_q * 1000),
#             "used_llm": False
#         })

#     try:
#         out = rag.ask(q, context=ctx, k=3)

#         answer = out["answer"]
#         chunks = out["chunks"]
#         used_llm = out["used_llm"]
#         latency = out["latency_sec"]
#         success = True

#     except Exception as e:
#         answer = f"Temporary issue: {e}"
#         chunks = []
#         used_llm = False
#         latency = 0.0
#         success = False

#     t_r = time.time()

#     event_log.append({
#         "type": "ask",
#         "timestamp_query": t_q,
#         "timestamp_resp": t_r,
#         "query": q,
#         "answer": answer,
#         "chunks": chunks,
#         "used_llm": used_llm,
#         "latency_sec": latency,
#         "success": success,
#         "context": ctx
#     })
#     _save_events()

#     return jsonify({
#         "answer": answer,
#         "chunks": chunks,
#         "latency_sec": latency,
#         "success": success,
#         "timestamp_query": int(t_q * 1000),
#         "timestamp_resp": int(t_r * 1000),
#         "used_llm": used_llm
#     })


# # -------------------------------
# # EVENTS (Android feed)
# # -------------------------------
# @app.route("/events", methods=["GET"])
# def events():
#     lines = []

#     for e in event_log[-50:]:
#         try:
#             ts = time.strftime(
#                 "%Y-%m-%d %H:%M:%S",
#                 time.localtime(float(e.get("timestamp_query", 0)))
#             )
#         except Exception:
#             ts = "NA"

#         if e.get("type") == "ask":
#             q = (e.get("query") or "")[:50]
#             a = (e.get("answer") or "")[:70]
#             lines.append(f"{ts} | Q: {q} | A: {a}")

#         elif e.get("type") == "risk_alert":
#             lvl = e.get("level", "?")
#             msg = e.get("message", "")
#             lines.append(f"{ts} | L{lvl} | {msg}")

#     return jsonify(lines)


# # -------------------------------
# # REPORT (PDF)
# # -------------------------------
# @app.route("/report", methods=["GET"])
# def report():
#     entries = []
#     for e in event_log:
#         if e.get("type") in ("ask", "risk_alert"):
#             ts_ms = int(float(e.get("timestamp_query", 0)) * 1000)
#             lvl = e.get("level", -1)
#             msg = e.get("message", e.get("answer", ""))
#             entries.append((ts_ms, lvl, msg))

#     path = save_report(entries, out_path="trip_report.pdf")
#     return send_file(path, as_attachment=True)


# # -------------------------------
# # CSV EXPORT (for paper tables)
# # -------------------------------
# @app.route("/export_csv", methods=["GET"])
# def export_csv():
#     rows = []

#     for e in event_log:
#         if isinstance(e, dict) and e.get("type") == "ask":
#             rows.append({
#                 "timestamp_query": e.get("timestamp_query", 0),
#                 "timestamp_resp": e.get("timestamp_resp", 0),
#                 "latency_sec": e.get("latency_sec", 0),
#                 "success": e.get("success", False),
#                 "query": (e.get("query") or "").replace("\n", " "),
#                 "answer": (e.get("answer") or "").replace("\n", " "),
#                 "used_llm": e.get("used_llm", False)
#             })

#     out_path = "results.csv"
#     with open(out_path, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(
#             f,
#             fieldnames=[
#                 "timestamp_query", "timestamp_resp", "latency_sec",
#                 "success", "query", "answer", "used_llm"
#             ]
#         )
#         writer.writeheader()
#         for r in rows:
#             writer.writerow(r)

#     return jsonify({"ok": True, "rows": len(rows), "path": os.path.abspath(out_path)})


# # -------------------------------
# # RAG EVALUATION METRICS
# # Precision@k, Recall@k, F1@k
# # -------------------------------
# @app.route("/evaluate_metrics", methods=["GET"])
# def evaluate_metrics():
#     k = int(request.args.get("k", 3))
#     return jsonify(_compute_metrics(k))


# def _compute_metrics(k: int = 3):
#     logs = [e for e in event_log if isinstance(e, dict) and e.get("type") == "ask"]
#     if not logs:
#         return {
#             "Precision@k": 0.0,
#             "Recall@k": 0.0,
#             "F1@k": 0.0,
#             "AvgLatency": 0.0,
#             "SuccessRate": 0.0,
#             "N": 0
#         }

#     def relevant(query: str, chunk: str) -> bool:
#         q_words = set(query.lower().split())
#         c_words = set(chunk.lower().split())
#         return len(q_words & c_words) > 0

#     precisions, recalls, latencies = [], [], []
#     success_count = 0

#     for e in logs:
#         query = e.get("query", "")
#         chunks = (e.get("chunks") or [])[:k]

#         if not chunks:
#             precisions.append(0.0)
#             recalls.append(0.0)
#             continue

#         rel = [relevant(query, c) for c in chunks]
#         tp = sum(rel)

#         precisions.append(tp / k)
#         recalls.append(1.0 if tp > 0 else 0.0)

#         if e.get("success"):
#             success_count += 1
#         latencies.append(float(e.get("latency_sec", 0.0)))

#     P = sum(precisions) / len(precisions)
#     R = sum(recalls) / len(recalls)
#     F1 = (2 * P * R / (P + R)) if (P + R) > 0 else 0.0

#     return {
#         "Precision@k": round(P, 3),
#         "Recall@k": round(R, 3),
#         "F1@k": round(F1, 3),
#         "AvgLatency": round(sum(latencies) / len(latencies), 3),
#         "SuccessRate": round(success_count / len(logs), 3),
#         "N": len(logs)
#     }


# # -------------------------------
# # Helpers
# # -------------------------------
# def _save_events():
#     try:
#         with open("event_log.json", "w") as f:
#             json.dump(event_log[-500:], f, indent=2)
#     except Exception as e:
#         print("⚠️ Could not persist events:", e)


# # -------------------------------
# # MAIN
# # -------------------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time, json, os, csv

from rag_chain import RagChain
from risk import risk_to_message
from report import save_report

app = Flask(__name__)
CORS(app)

rag = RagChain()

# -----------------------------
# In-memory event log
# -----------------------------
event_log = []

# Reload persisted events if present
if os.path.exists("event_log.json"):
    try:
        with open("event_log.json", "r") as f:
            event_log = json.load(f)
    except Exception:
        event_log = []

# -----------------------------
# Health check
# -----------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


# -----------------------------
# Risk alert endpoint
# -----------------------------
@app.route("/risk_alert", methods=["POST"])
def risk_alert():
    data = request.get_json(force=True)
    lvl = int(data.get("risk_level", 0))
    msg = risk_to_message(lvl)

    ts = time.time()

    event_log.append({
        "type": "risk_alert",
        "timestamp_query": ts,
        "timestamp_resp": ts,
        "level": lvl,
        "message": msg,
        "success": True
    })
    _save_events()

    return jsonify({"message": msg, "timestamp_ms": int(ts * 1000)})


# =========================================================
# STEP 1 — Per-query Precision@k / Recall@k / F1@k
# =========================================================
def _compute_prf_for_query(query: str, chunks: list, k: int = 3):
    """
    Computes Precision@k, Recall@k, F1@k for a single query
    using lexical overlap heuristic (standard RAG baseline).
    """
    if not chunks:
        return 0.0, 0.0, 0.0

    q_words = set(query.lower().split())
    retrieved = chunks[:k]

    relevant = []
    for c in retrieved:
        c_words = set(c.lower().split())
        relevant.append(len(q_words & c_words) > 0)

    tp = sum(relevant)
    precision = tp / k
    recall = 1.0 if tp > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return round(precision, 3), round(recall, 3), round(f1, 3)


# -----------------------------
# ASK endpoint (RAG + metrics)
# -----------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    q = (data.get("query") or "").strip()
    ctx = data.get("context") or {}

    t_q = time.time()

    if not q:
        return jsonify({
            "answer": "",
            "chunks": [],
            "success": False,
            "timestamp_query": int(t_q * 1000),
            "timestamp_resp": int(t_q * 1000)
        })

    try:
        out = rag.ask(q, context=ctx, k=3)
        answer = out["answer"]
        chunks = out["chunks"]
        used_llm = out["used_llm"]
        latency = out["latency_sec"]
        success = True
    except Exception as e:
        answer = f"Temporary issue: {e}"
        chunks = []
        used_llm = False
        latency = 0.0
        success = False

    t_r = time.time()

    # =====================================================
    # STEP 2 — Compute per-query retrieval metrics
    # =====================================================
    p_k, r_k, f1_k = _compute_prf_for_query(q, chunks, k=3)

    # Log interaction
    event_log.append({
        "type": "ask",
        "timestamp_query": t_q,
        "timestamp_resp": t_r,
        "query": q,
        "answer": answer,
        "chunks": chunks,
        "used_llm": used_llm,
        "latency_sec": latency,
        "success": success,

        # 🔹 Retrieval metrics
        "precision_at_k": p_k,
        "recall_at_k": r_k,
        "f1_at_k": f1_k,

        "context": ctx
    })
    _save_events()

    return jsonify({
        "answer": answer,
        "chunks": chunks,
        "latency_sec": latency,
        "success": success,
        "timestamp_query": int(t_q * 1000),
        "timestamp_resp": int(t_r * 1000),
        "used_llm": used_llm
    })


# -----------------------------
# Export CSV (STEP 3)
# -----------------------------
@app.route("/export_csv", methods=["GET"])
def export_csv():
    rows = []

    for e in event_log:
        if isinstance(e, dict) and e.get("type") == "ask":
            rows.append({
                "timestamp_query": e.get("timestamp_query", 0),
                "timestamp_resp": e.get("timestamp_resp", 0),
                "latency_sec": e.get("latency_sec", 0.0),
                "success": e.get("success", False),
                "query": (e.get("query") or "").replace("\n", " "),
                "answer": (e.get("answer") or "").replace("\n", " "),
                "used_llm": e.get("used_llm", False),

                # 🔹 Metrics columns
                "precision_at_k": e.get("precision_at_k", 0.0),
                "recall_at_k": e.get("recall_at_k", 0.0),
                "f1_at_k": e.get("f1_at_k", 0.0),
            })

    out_path = "results.csv"
    fieldnames = list(rows[0].keys()) if rows else [
        "timestamp_query", "timestamp_resp", "latency_sec",
        "success", "query", "answer", "used_llm",
        "precision_at_k", "recall_at_k", "f1_at_k"
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return jsonify({
        "ok": True,
        "rows": len(rows),
        "path": os.path.abspath(out_path)
    })


# -----------------------------
# Helpers
# -----------------------------
def _save_events():
    try:
        with open("event_log.json", "w") as f:
            json.dump(event_log[-500:], f, indent=2)
    except Exception as e:
        print("Warning: could not persist events:", e)


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
