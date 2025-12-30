#!/bin/bash

API_URL="http://127.0.0.1:8000/ask"

queries=(
  "What does risk level 0 mean?"
  "What does risk level 1 mean?"
  "What does risk level 2 mean?"
  "What does risk level 3 mean?"
  "What does risk level 4 mean?"
  "What should I do if the system says critical risk?"
  "How can I reduce risk while driving fast?"
  "How does speed affect accident risk?"
  "What does driver distraction mean?"
  "Why is following distance important?"
  "What is a safe distance to follow another vehicle?"
  "How does stereo depth help in safety?"
  "How does depth estimation affect risk prediction?"
  "Why did the system warn me now?"
  "How can I improve my driving behavior?"
)

echo "🚀 Running 15 evaluation queries..."
echo "----------------------------------"

for q in "${queries[@]}"; do
  echo "🧠 Query: $q"
  curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$q\"}"
  echo -e "\n----------------------------------"
  sleep 0.3
done

echo "✅ All queries completed."
echo "📄 Exporting CSV..."
curl -s http://127.0.0.1:8000/export_csv
echo -e "\n🎉 Done. results.csv generated."
