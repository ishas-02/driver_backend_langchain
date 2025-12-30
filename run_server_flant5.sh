#!/bin/bash
set -e

echo "🚀 Starting FLAN-T5 + Flask (LangChain)..."

export LLM_MODE=transformers
export LLM_MODEL=google/flan-t5-base

python server.py
