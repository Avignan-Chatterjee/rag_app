# rag_app

# Local RAG Chat App – 100% Private & Offline  
**Run your own ChatGPT-style assistant**  
No cloud. No API keys. No data ever leaves your computer.


## Features
- Fully offline RAG (Retrieval-Augmented Generation)
- Powered by Ollama (`llama3.2`, `llama3.1`, `gemma2`, `mistral`, etc.)
- Milvus standalone vector database (GPU-accelerated via ROCm possible)
- Real-time token streaming
- Beautiful ChatGPT-like Streamlit UI
- Ingest PDFs, TXT, MD from a folder
- Runs perfectly on AMD Ryzen 9 + Radeon RX 7000/9000 series
- Zero external dependencies after first setup

## Tech Stack
| Component          | Technology                          |
|--------------------|-------------------------------------|
| LLM                | Ollama (`llama3.2` recommended)     |
| Embeddings         | `mxbai-embed-large` via Ollama      |
| Vector DB          | Milvus Standalone (Docker)          |
| Backend            | FastAPI + LangChain                 |
| Frontend           | Streamlit (dark mode, streaming)    |
| GPU Acceleration   | ROCm 6.1+ (optional but recommended) |

## Prerequisites
- AMD Ryzen 9 CPU + Radeon GPU (RX 7000/9000 series recommended)
- Ubuntu 22.04/24.04 or Windows + WSL2 (ROCm works best on Linux)
- Docker & Docker Compose
- Python 3.10+
- Ollama installed and running

## Quick Start (5 minutes)

```bash
# 1. Clone repo
git clone https://github.com/yourusername/rag_app.git
cd rag_app

# 2. Start Milvus (vector DB)
docker compose -f vector_db/docker-compose.yml up -d

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Pull models in Ollama (run once)
ollama pull llama3.2
ollama pull mxbai-embed-large

# 5. Add your documents
mkdir docs
cp /path/to/your/files/*.pdf docs/
cp /path/to/your/files/*.txt docs/

# 6. Start App.
./start.sh
```

Open http://localhost:8501 → start chatting with your private documents!

## Project Structure
```
rag_app/
├── docs/                  ← Put your PDFs, .txt, .md here
├── backend_rag.py         ← FastAPI + Ollama + Milvus RAG logic
├── rag_chat_ui.py         ← Streamlit chat interface
├── requirements.txt
|── vector_db
    |── docker-compose.yml ← Milvus standalone + etcd + minio
```

## Screenshots
![UI](assets/screenshot1.png)  
*Clean, responsive, streaming chat interface*

## Contributing
Pull requests are welcome! Especially:
- Better prompt templates
- Hybrid search (BM25 + vector)
- Chat history persistence
- PDF upload directly in UI

---

**Your documents never leave your machine. Your AI stays yours.**

Made with love for local, private, and powerful AI.  
Star this repo if you believe in offline intelligence!