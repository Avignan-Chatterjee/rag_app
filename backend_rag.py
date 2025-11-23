# backend_rag.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_milvus import Milvus
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import asyncio
import json
import os

app = FastAPI(title="Local RAG with Ollama + Milvus")

# === CONFIG ===
MILVUS_URI = "http://localhost:19530"
COLLECTION_NAME = "rag_docs"
EMBEDDING_MODEL = "mxbai-embed-large"        # Great open embedding model
LLM_MODEL = "llama3.2"                       # or "llama3.1", "mistral", "gemma2", etc.

# Initialize embeddings & LLM
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
llm = ChatOllama(model=LLM_MODEL, temperature=0.7, streaming=True)

# Connect to Milvus (auto-creates collection if not exists)
vectorstore = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": MILVUS_URI},
    collection_name=COLLECTION_NAME,
    index_params={"metric_type": "IP", "index_type": "IVF_FLAT", "params": {"nlist": 128}},
    auto_id=True,
)

# Build retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# Custom prompt
template = """Use only the following context to answer the question. Be concise.

Context:
{context}

Question: {question}
Answer:"""

prompt = PromptTemplate.from_template(template)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt},
)

class ChatRequest(BaseModel):
    message: str
    top_k: int = 6

# Streaming generator
async def stream_answer(question: str):
    #yield json.dumps({"token": "Searching documents... "}) + "\n"
    #yield json.dumps({"token": "for question " + question}) + "\n"
    await asyncio.sleep(0.3)

    # Stream tokens from LangChain + Ollama
    chunks = qa_chain.stream({"query": question})
    
    for chunk in chunks:
        #msg = f"Got this chunk : {str(chunk)}"
        #yield json.dumps({"token": msg}) + "\n"

        if "result" in chunk:
            text = chunk["result"]
            for word in text.split():
                yield json.dumps({"token": word + " "}) + "\n"
                await asyncio.sleep(0.02)
    #yield json.dumps({"token": "\n\nDone."}) + "\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(stream_answer(request.message), media_type="application/x-ndjson")

# === INGEST DOCUMENTS (run once or whenever you add files) ===
@app.post("/ingest")
async def ingest_folder(folder: str = "docs"):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader

    if not os.path.exists(folder):
        return {"error": "Folder not found"}

    loader = DirectoryLoader(folder, glob="**/*.*", loader_cls=TextLoader, silent_errors=False)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    vectorstore.add_documents(splits)
    return {"status": f"Ingested {len(splits)} chunks into Milvus"}

@app.get("/")
def health():
    return {"status": "RAG ready", "llm": LLM_MODEL, "collection": COLLECTION_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)