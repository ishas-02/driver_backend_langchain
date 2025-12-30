# #!/bin/bash
# set -e

# echo "🦙 Starting Ollama + Flask (LangChain)..."

# # Start ollama if not running
# if ! pgrep -x "ollama" > /dev/null; then
#   echo "⚠️ Ollama not running. Starting..."
#   ollama serve &
#   sleep 2
# fi

# ollama list | grep -q "llama3.1" || ollama pull llama3.1

# export LLM_MODE=ollama
# export OLLAMA_BASE_URL="http://localhost:11434/v1"
# export OLLAMA_MODEL="llama3.1"
# export OLLAMA_API_KEY="ollama"

# python server.py

#!/bin/bash

# ✅ Correct PATH (directory, not executable)
export PATH="/opt/homebrew/bin:$PATH"

echo "🦙 Starting Flask backend with Ollama (local LLM mode)..."

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null
then
    echo "⚠️ Ollama server not running — starting it now..."
    ollama serve &
    sleep 3
fi

# Pull model if missing
ollama list | grep -q "llama3.1" || ollama pull llama3.1

# LLM configuration
export LLM_MODE=ollama
export OLLAMA_BASE_URL="http://localhost:11434/v1"
export OLLAMA_MODEL="llama3.1"
export OLLAMA_API_KEY="ollama"

# Start Flask backend
python server.py
