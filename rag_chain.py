# # import os
# # import time
# # from typing import Dict, Any, List

# # from langchain_community.vectorstores import FAISS
# # from langchain_community.embeddings import HuggingFaceEmbeddings
# # from langchain.prompts import PromptTemplate

# # def load_llm():
# #     mode = os.getenv("LLM_MODE", "transformers").lower().strip()

# #     if mode == "ollama":
# #         from langchain_community.chat_models import ChatOpenAI

# #         return ChatOpenAI(
# #             base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
# #             api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
# #             model=os.getenv("OLLAMA_MODEL", "llama3.1"),
# #             temperature=0.2
# #         )

# #     # default: transformers (FLAN-T5)
# #     from langchain_community.llms import HuggingFacePipeline
# #     from transformers import pipeline

# #     model_name = os.getenv("LLM_MODEL", "google/flan-t5-base")
# #     pipe = pipeline(
# #         "text2text-generation",
# #         model=model_name,
# #         max_new_tokens=128,
# #         do_sample=False
# #     )
# #     return HuggingFacePipeline(pipeline=pipe)


# # class RagChain:
# #     """
# #     LangChain-based RAG:
# #       - FAISS retrieval
# #       - Prompted LLM synthesis
# #       - Keeps Android-compatible output format
# #     """
# #     def __init__(self):
# #         embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# #         self.db = FAISS.load_local(
# #             "data/faiss_index",
# #             embeddings,
# #             allow_dangerous_deserialization=True
# #         )

# #         self.retriever = self.db.as_retriever(search_kwargs={"k": 3})
# #         self.llm = load_llm()

# #         self.prompt = PromptTemplate(
# #             input_variables=["context", "question", "risk_level", "depth_m", "speed_kmh", "behavior"],
# #             template=(
# #                 "You are an in-car driving safety assistant. Be calm, concise, and actionable.\n\n"
# #                 "Known driving context (may be NA):\n"
# #                 "- risk_level: {risk_level}\n"
# #                 "- depth_m (distance to closest object): {depth_m}\n"
# #                 "- speed_kmh: {speed_kmh}\n"
# #                 "- driver_behavior: {behavior}\n\n"
# #                 "Retrieved knowledge:\n{context}\n\n"
# #                 "User question: {question}\n\n"
# #                 "Rules:\n"
# #                 "- Give 1–2 short sentences.\n"
# #                 "- If risk_level is 3 or 4: prioritize slow down + increase distance + focus attention.\n"
# #                 "- If distraction behavior detected: explicitly advise to stop and refocus.\n"
# #                 "Answer:"
# #             )
# #         )

# #     def ask(self, question: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
# #         t0 = time.time()
# #         ctx = context or {}

# #         risk_level = str(ctx.get("risk_level", "NA"))
# #         depth_m = str(ctx.get("depth_m", "NA"))
# #         speed_kmh = str(ctx.get("speed_kmh", "NA"))
# #         behavior = str(ctx.get("behavior", "NA"))

# #         docs = self.retriever.get_relevant_documents(question)
# #         chunks = [d.page_content for d in docs]

# #         # If retrieval is empty, still answer safely (no "No info" response)
# #         if not chunks:
# #             answer = "I recommend slowing down, increasing following distance, and staying fully attentive. Ask a specific safety question and I’ll explain."
# #             used_llm = False
# #             latency = round(time.time() - t0, 4)
# #             return {
# #                 "answer": answer,
# #                 "chunks": [],
# #                 "used_llm": used_llm,
# #                 "latency_sec": latency
# #             }

# #         prompt_text = self.prompt.format(
# #             context="\n".join([f"- {c}" for c in chunks]),
# #             question=question,
# #             risk_level=risk_level,
# #             depth_m=depth_m,
# #             speed_kmh=speed_kmh,
# #             behavior=behavior
# #         )

# #         # LLM generate
# #         answer = self.llm.invoke(prompt_text)
# #         # Some LLMs return object-like outputs; normalize:
# #         if not isinstance(answer, str):
# #             answer = str(answer)

# #         latency = round(time.time() - t0, 4)
# #         return {
# #             "answer": answer.strip(),
# #             "chunks": chunks,
# #             "used_llm": True,
# #             "latency_sec": latency
# #         }

# import os, time
# from typing import Dict, Any

# from langchain.schema import Document
# from langchain_community.vectorstores import FAISS
# from langchain_core.embeddings import Embeddings

# import requests


# # --- Embeddings wrapper using SentenceTransformer (no langchain-huggingface) ---
# class STEmbeddings(Embeddings):
#     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
#         from sentence_transformers import SentenceTransformer
#         self.model = SentenceTransformer(model_name)

#     def embed_documents(self, texts):
#         return self.model.encode(texts, normalize_embeddings=True).tolist()

#     def embed_query(self, text):
#         return self.model.encode([text], normalize_embeddings=True)[0].tolist()


# class RagChain:
#     def __init__(self, index_dir: str = "data/faiss_index"):
#         self.emb = STEmbeddings("all-MiniLM-L6-v2")
#         self.db = FAISS.load_local(index_dir, self.emb, allow_dangerous_deserialization=True)

#         self.llm_mode = os.getenv("LLM_MODE", "none").lower().strip()
#         self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
#         self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
#         self.ollama_key = os.getenv("OLLAMA_API_KEY", "ollama")

#     def retrieve(self, query: str, k: int = 3):
#         docs = self.db.similarity_search_with_score(query, k=k)
#         # docs: List[Tuple[Document, score]] where score is distance-ish; just keep text
#         retrieved = []
#         for d, score in docs:
#             retrieved.append({"text": d.page_content, "score": float(score), "meta": d.metadata})
#         return retrieved

#     def generate(self, question: str, retrieved_texts: list[str]) -> str:
#         # If no LLM, return best chunk
#         if self.llm_mode != "ollama":
#             return " ".join(retrieved_texts) if retrieved_texts else "Please drive safely and ask a more specific question."

#         context = "\n".join([f"- {t}" for t in retrieved_texts])
#         prompt = (
#             "You are an in-car safety assistant. Be calm, concise, and actionable.\n\n"
#             f"Context:\n{context}\n\n"
#             f"Question: {question}\n\n"
#             "Answer in 1–2 sentences with a clear driving recommendation."
#         )

#         try:
#             r = requests.post(
#                 f"{self.ollama_base}/chat/completions",
#                 headers={"Authorization": f"Bearer {self.ollama_key}"},
#                 json={"model": self.ollama_model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
#                 timeout=60,
#             )
#             j = r.json()
#             return j["choices"][0]["message"]["content"].strip()
#         except Exception as e:
#             # fallback to retrieval-only
#             return " ".join(retrieved_texts) + f" (LLM fallback: {e})"

#     def ask(self, query: str, k: int = 3) -> Dict[str, Any]:
#         t0 = time.time()
#         retrieved = self.retrieve(query, k=k)
#         texts = [r["text"] for r in retrieved]
#         ans = self.generate(query, texts)
#         return {
#             "answer": ans,
#             "retrieved": retrieved,
#             "used_llm": (self.llm_mode == "ollama"),
#             "latency_sec": round(time.time() - t0, 4),
#         }

# rag_chain.py
import os, time
from typing import Dict, Any, List, Optional

import requests
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings


class STEmbeddings(Embeddings):
    """SentenceTransformers embeddings wrapper (no langchain-huggingface dependency)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()


class RagChain:
    """
    LangChain FAISS Retriever + optional Ollama generator.

    Returns:
      {
        "answer": str,
        "chunks": [str, ...],
        "used_llm": bool,
        "latency_sec": float
      }
    """

    def __init__(self, index_dir: str = "data/faiss_index"):
        self.emb = STEmbeddings("all-MiniLM-L6-v2")
        self.db = FAISS.load_local(index_dir, self.emb, allow_dangerous_deserialization=True)

        self.llm_mode = os.getenv("LLM_MODE", "none").lower().strip()  # "ollama" or "none"
        self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.ollama_key = os.getenv("OLLAMA_API_KEY", "ollama")

    def ask(self, query: str, context: Optional[Dict[str, Any]] = None, k: int = 3) -> Dict[str, Any]:
        t0 = time.time()

        # 1) Retrieve
        docs = self.db.similarity_search(query, k=k)
        chunks = [d.page_content for d in docs]

        # 2) Answer
        used_llm = (self.llm_mode == "ollama")
        if used_llm:
            answer = self._ollama_answer(query, chunks, context or {})
        else:
            # retrieval-only fallback
            answer = " ".join(chunks) if chunks else (
                "I recommend slowing down, increasing following distance, and refocusing attention."
            )

        return {
            "answer": answer.strip(),
            "chunks": chunks,
            "used_llm": used_llm,
            "latency_sec": round(time.time() - t0, 4)
        }

    def _ollama_answer(self, question: str, chunks: List[str], context: Dict[str, Any]) -> str:
        # Keep prompt short and driver-safe
        ctx_lines = "\n".join([f"- {c}" for c in chunks[:3]])
        ctx_meta = ""
        if context:
            # include only safe compact metadata
            meta_parts = []
            for k in ["risk_level", "speed_kmh", "depth_m", "behavior"]:
                if k in context:
                    meta_parts.append(f"{k}={context[k]}")
            if meta_parts:
                ctx_meta = "Telemetry: " + ", ".join(meta_parts) + "\n\n"

        prompt = (
            "You are an in-car safety assistant. Be calm, concise, and actionable.\n"
            f"{ctx_meta}"
            f"Context:\n{ctx_lines}\n\n"
            f"Question: {question}\n\n"
            "Answer in 1–2 sentences. Give a clear driving recommendation."
        )

        try:
            r = requests.post(
                f"{self.ollama_base}/chat/completions",
                headers={"Authorization": f"Bearer {self.ollama_key}"},
                json={
                    "model": self.ollama_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                },
                timeout=60
            )
            j = r.json()
            # if Ollama returns unexpected payload, fall back gracefully
            return j.get("choices", [{}])[0].get("message", {}).get("content", "").strip() or " ".join(chunks)
        except Exception:
            return " ".join(chunks) if chunks else "Please slow down and stay alert."
