# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import time, json, os, csv

# from rag_chain import RagChain
# from risk import risk_to_message
# from report import save_report

# app = Flask(__name__)
# CORS(app)

# rag = RagChain()
# event_log = []

# # reload JSON logs (optional)
# if os.path.exists("event_log.json"):
#     try:
#         with open("event_log.json", "r") as f:
#             event_log = json.load(f)
#     except Exception:
#         event_log = []

# def _save_events():
#     try:
#         with open("event_log.json", "w") as f:
#             json.dump(event_log[-500:], f, indent=2)
#     except Exception as e:
#         print("⚠️ Could not persist events:", e)

# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"ok": True})

# @app.route("/risk_alert", methods=["POST"])
# def risk_alert():
#     data = request.get_json(force=True) or {}
#     lvl = int(data.get("risk_level", 0))
#     msg = risk_to_message(lvl)
#     ts_ms = int(time.time() * 1000)

#     event_log.append({
#         "type": "risk_alert",
#         "timestamp_query": ts_ms / 1000.0,
#         "timestamp_resp": ts_ms / 1000.0,
#         "level": lvl,
#         "message": msg,
#         "success": True
#     })
#     _save_events()
#     return jsonify({"message": msg, "timestamp_ms": ts_ms})

# @app.route("/ask", methods=["POST"])
# def ask():
#     data = request.get_json(force=True) or {}
#     q = (data.get("query") or "").strip()
#     ctx = data.get("context") or {}

#     t_q = time.time()
#     if not q:
#         return jsonify({
#             "answer": "",
#             "chunks": [],
#             "latency_sec": 0.0,
#             "success": False,
#             "timestamp_query": int(t_q * 1000),
#             "timestamp_resp": int(t_q * 1000),
#             "used_llm": False
#         })

#     try:
#         out = rag.ask(q, context=ctx)
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
#         "success": success,
#         "used_llm": used_llm,
#         "latency_sec": latency,
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

# @app.route("/events", methods=["GET"])
# def events():
#     lines = []
#     for e in event_log[-50:]:
#         if isinstance(e, dict):
#             ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(e.get("timestamp_query", 0))))
#             if e.get("type") == "ask":
#                 q = (e.get("query") or "")[:48]
#                 a = (e.get("answer") or "")[:64]
#                 lines.append(f"{ts} | Q: {q} | A: {a}")
#             elif e.get("type") == "risk_alert":
#                 lines.append(f"{ts} | L{e.get('level', '?')} | {e.get('message', '')}")
#         else:
#             lines.append(str(e))
#     return jsonify(lines)

# @app.route("/report", methods=["GET"])
# def report():
#     entries = []
#     for e in event_log:
#         if isinstance(e, dict) and e.get("type") in ("risk_alert", "ask"):
#             ts_ms = int(float(e.get("timestamp_query", 0)) * 1000)
#             lvl = e.get("level", -1)
#             msg = e.get("message", e.get("answer", "")) or ""
#             entries.append((ts_ms, lvl, msg))

#     path = save_report(entries, out_path="trip_report.pdf")
#     return send_file(path, as_attachment=True)

# @app.route("/export_csv", methods=["GET"])
# def export_csv():
#     try:
#         out_path = "results.csv"
#         fieldnames = ["timestamp_query", "timestamp_resp", "latency_sec", "success", "query", "answer", "used_llm"]

#         rows = []
#         for e in event_log:
#             if isinstance(e, dict) and e.get("type") == "ask":
#                 rows.append({
#                     "timestamp_query": e.get("timestamp_query", 0),
#                     "timestamp_resp": e.get("timestamp_resp", 0),
#                     "latency_sec": e.get("latency_sec", 0),
#                     "success": e.get("success", False),
#                     "query": (e.get("query") or "").replace("\n", " ").strip(),
#                     "answer": (e.get("answer") or "").replace("\n", " ").strip(),
#                     "used_llm": e.get("used_llm", False)
#                 })

#         with open(out_path, "w", newline="", encoding="utf-8") as f:
#             w = csv.DictWriter(f, fieldnames=fieldnames)
#             w.writeheader()
#             for r in rows:
#                 w.writerow(r)

#         return jsonify({"ok": True, "rows": len(rows), "path": os.path.abspath(out_path)})

#     except Exception as e:
#         return jsonify({"ok": False, "error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)

# server.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import time, json, os, csv

from rag_chain import RagChain
from risk import risk_to_message
from report import save_report

app = Flask(__name__)
CORS(app)

rag = RagChain(index_dir="data/faiss_index")
event_log = []

# reload JSON logs (optional)
if os.path.exists("event_log.json"):
    try:
        with open("event_log.json", "r", encoding="utf-8") as f:
            event_log = json.load(f)
    except Exception:
        event_log = []

def _save_events():
    try:
        with open("event_log.json", "w", encoding="utf-8") as f:
            json.dump(event_log[-500:], f, indent=2)
    except Exception as e:
        print("⚠️ Could not persist events:", e)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/risk_alert", methods=["POST"])
def risk_alert():
    data = request.get_json(force=True) or {}
    lvl = int(data.get("risk_level", 0))
    msg = risk_to_message(lvl)
    ts_ms = int(time.time() * 1000)

    event_log.append({
        "type": "risk_alert",
        "timestamp_query": ts_ms / 1000.0,
        "timestamp_resp": ts_ms / 1000.0,
        "level": lvl,
        "message": msg,
        "success": True
    })
    _save_events()
    return jsonify({"message": msg, "timestamp_ms": ts_ms})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True) or {}
    q = (data.get("query") or "").strip()
    ctx = data.get("context") or {}

    t_q = time.time()
    if not q:
        return jsonify({
            "answer": "",
            "chunks": [],
            "latency_sec": 0.0,
            "success": False,
            "timestamp_query": int(t_q * 1000),
            "timestamp_resp": int(t_q * 1000),
            "used_llm": False
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

    event_log.append({
        "type": "ask",
        "timestamp_query": t_q,
        "timestamp_resp": t_r,
        "query": q,
        "answer": answer,
        "chunks": chunks,
        "success": success,
        "used_llm": used_llm,
        "latency_sec": latency,
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

@app.route("/events", methods=["GET"])
def events():
    lines = []
    for e in event_log[-50:]:
        if isinstance(e, dict):
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(e.get("timestamp_query", 0))))
            if e.get("type") == "ask":
                q = (e.get("query") or "")[:48]
                a = (e.get("answer") or "")[:64]
                lines.append(f"{ts} | Q: {q} | A: {a}")
            elif e.get("type") == "risk_alert":
                lines.append(f"{ts} | L{e.get('level', '?')} | {e.get('message', '')}")
        else:
            lines.append(str(e))
    return jsonify(lines)

@app.route("/report", methods=["GET"])
def report():
    entries = []
    for e in event_log:
        if isinstance(e, dict) and e.get("type") in ("risk_alert", "ask"):
            ts_ms = int(float(e.get("timestamp_query", 0)) * 1000)
            lvl = e.get("level", -1)
            msg = e.get("message", e.get("answer", "")) or ""
            entries.append((ts_ms, lvl, msg))

    path = save_report(entries, out_path="trip_report.pdf")
    return send_file(path, as_attachment=True)

@app.route("/export_csv", methods=["GET"])
def export_csv():
    try:
        out_path = "results.csv"
        fieldnames = ["timestamp_query", "timestamp_resp", "latency_sec", "success", "query", "answer", "used_llm"]

        rows = []
        for e in event_log:
            if isinstance(e, dict) and e.get("type") == "ask":
                rows.append({
                    "timestamp_query": e.get("timestamp_query", 0),
                    "timestamp_resp": e.get("timestamp_resp", 0),
                    "latency_sec": e.get("latency_sec", 0),
                    "success": e.get("success", False),
                    "query": (e.get("query") or "").replace("\n", " ").strip(),
                    "answer": (e.get("answer") or "").replace("\n", " ").strip(),
                    "used_llm": e.get("used_llm", False)
                })

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)

        return jsonify({"ok": True, "rows": len(rows), "path": os.path.abspath(out_path)})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
