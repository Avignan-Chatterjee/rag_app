#!/bin/bash
# File: start_rag_app.sh
# Purpose: Start FastAPI backend + Streamlit UI + ingest data, fail fast on any error

set -euo pipefail   # <-- crucial: stop on any failure

# Optional: colorful output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting RAG application...${NC}"

# 1. Start FastAPI backend (on port 8000 by default)
echo "Launching backend (backend_rag.py)..."
python backend_rag.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# 2. Start Streamlit frontend
echo "Launching Streamlit UI (rag_chat_ui.py)..."
streamlit run rag_chat_ui.py --server.port=8501 &
STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

# 3. Give the FastAPI server a moment to start
echo "Waiting 5 seconds for FastAPI to be ready..."
sleep 5   # increased from 2 → more reliable

# 4. Trigger ingestion
echo "Triggering ingestion from folder 'docs'..."
curl -X POST "http://127.0.0.1:8000/ingest?folder=docs" \
     --fail --silent --show-error || {
       echo -e "${RED}Ingestion failed!${NC}" >&2
       kill $BACKEND_PID $STREAMLIT_PID 2>/dev/null || true
       exit 1
     }
echo "\n"

# 5. Success!
echo -e "${GREEN}All steps completed successfully!${NC}"
echo -e "   FastAPI backend running (PID ${YELLOW}$BACKEND_PID${NC})"
echo -e "   Streamlit UI running at ${BLUE}http://localhost:8501${NC} (PID ${YELLOW}$STREAMLIT_PID)${NC}"
echo "   Ingestion complete"
echo "Press Ctrl+C to stop both processes"

# Keep script alive so you can Ctrl+C to kill both
wait