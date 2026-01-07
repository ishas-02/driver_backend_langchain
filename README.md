# 🚗 **Driver Safety Intelligence Backend**

### *Reasoning About Driver Risk, Context, and Safety with RAG & LLMs*

---

# 🧩 **1. The Problem: Safety Systems Detect — But Don’t Explain**

Modern driver safety systems generate large volumes of signals:

* Driver behavior classifications  
* Risk scores and alerts  
* Temporal driving logs  
* Historical driving context  

Yet the most important questions are often unanswered:

* Why was this driving session marked risky?
* Which behaviors contributed the most?
* How does this drive compare to past sessions?
* What patterns should be addressed proactively?

Most systems **detect anomalies**.
Very few **reason about them**.

Drivers, researchers, and safety analysts deserve systems that explain *why*, not just *what*.

---

# ⭐ **2. The Solution: A Reasoning Backend for Driver Safety**

**driver_backend_langchain** is a **LangChain-powered backend** that transforms driver-safety data into **explainable, queryable intelligence** using **Retrieval-Augmented Generation (RAG)**.

Instead of returning isolated predictions, the system:

* Retrieves relevant historical and contextual data
* Grounds responses in evidence
* Generates natural-language explanations
* Produces structured safety reports
* Logs outputs for evaluation and analysis

It is not just an inference engine.  
It is a **reasoning layer** behind driver-safety systems.

---

# 🧠 **3. What the Backend Understands**

The system builds semantic relationships across driver data such as:
```
[Sudden Braking] -> CONTRIBUTES_TO -> [High Risk]
[Distracted Driving] -> INCREASES -> [Accident Probability]
[Historical Pattern] -> EXPLAINS -> [Current Risk Score]
[Environmental Context] -> AMPLIFIES -> [Driver Error]
```



These relationships allow the backend to **justify decisions**, not just compute them.

---

# 🎨 **4. What the System Produces**

### 🤖 Natural-Language Reasoning

Ask questions like:

* “Why was this driving session high risk?”
* “Which behaviors contributed the most?”
* “Compare today’s drive with last week”

The backend responds with **context-grounded explanations**, not hallucinations.

---

### 📊 Risk Scores with Context

Risk values are returned alongside semantic reasoning — not as black-box numbers.

---

### 🧾 Structured Safety Reports

Automatically generated reports that can be shared with:

* Drivers  
* Fleet managers  
* Safety researchers  
* Analytics dashboards  

---

### 📈 Evaluation Logs

All batch-query outputs and metadata are saved to:


This enables offline analysis, benchmarking, and visualization.

---


## 🛠️ Installation & Setup

### Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
````

###  Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Running the System

### Step 1: Prepare the Knowledge Base

```bash
python prepare_kb.py
```

Preprocesses and cleans the data used for retrieval.

---

### Step 2: Build the Vector Index

```bash
python build_index.py
```

Creates embeddings and stores them in a vector index for fast retrieval.

---

### Step 3: Start the Backend Server

Choose your preferred LLM backend.

####  Using FLAN-T5

```bash
./run_server_flant5.sh
```

####  Using Ollama

```bash
./run_server_ollama.sh
```

Ensure Ollama is running locally before launching.

#### Direct Python execution

```bash
python server.py
```

---

## 🌐 API Capabilities (Representative)

| Endpoint  | Method | Description                           |
| --------- | ------ | ------------------------------------- |
| `/query`  | POST   | Context-aware driver safety reasoning |
| `/risk`   | POST   | Driver risk score computation         |
| `/report` | GET    | Generate structured safety report     |


---
## 📦 Project Structure
```
driver_backend_langchain/
│
├── data/                     # Knowledge base data
├── prepare_kb.py             # KB preprocessing
├── build_index.py            # Vector index creation
├── rag_chain.py              # LangChain RAG pipeline
├── server.py                 # API server
├── risk.py                   # Risk computation logic
├── report.py                 # Report generation
├── run_15_queries.sh         # Batch evaluation
├── run_server_flant5.sh      # FLAN-T5 runner
├── run_server_ollama.sh      # Ollama runner
├── requirements.txt
└── results.csv
```
---
## 🔥 Why This Matters

Because safety systems should not be black boxes.
Because drivers deserve explanations, not just warnings.
Because trust comes from understanding.

This backend transforms driver-safety data into interpretable, explainable intelligence.

---
## 🎉 Final Thought

Driver safety should be about more than alerts.

It should be about understanding behavior, context, and risk —
and acting with clarity.

This backend helps systems not only warn — but explain why.
---
### 📄 License
MIT License © 2026 Isha Shetye
