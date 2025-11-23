# rag_chat_ui.py - FIXED streaming version with httpx
import streamlit as st
import httpx
import json

st.set_page_config(page_title="Local RAG Chat", page_icon="Brain", layout="centered")

# ==================== CONFIG ====================
BACKEND_URL = "http://127.0.0.1:8000/chat"   # Change if your backend uses different port

st.title("Brain Local RAG Assistant")
st.caption("100% private • Fully offline")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("RAG Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.slider("Max Tokens", 256, 4096, 2048, 128)
    top_k = st.slider("Top-K Retrieval", 1, 20, 5)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ==================== INIT HISTORY ====================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your local RAG assistant. Ask me anything about your documents!"}
    ]

# ==================== DISPLAY MESSAGES ====================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================== USER INPUT ====================
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # CORRECT WAY TO STREAM WITH HTTPX
            with httpx.stream("POST", BACKEND_URL, json={
                "message": prompt,
                "history": st.session_state.messages[:-1],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_k": top_k,
            }, timeout=300.0) as response:
                
                response.raise_for_status()
                
                for chunk in response.iter_lines():
                    if chunk:
                        try:
                            #data = json.loads(chunk.decode("utf-8"))
                            data = json.loads(chunk)
                            if "token" in data:
                                full_response += data["token"]
                                message_placeholder.markdown(full_response + "▌")
                            elif "error" in data:
                                st.error(data["error"])
                        except json.JSONDecodeError:
                            continue  # skip malformed lines

            message_placeholder.markdown(full_response)

        except httpx.ConnectError:
            st.error("Cannot connect to backend. Is `backend.py` running on port 8000?")
        except httpx.HTTPStatusError as e:
            st.error(f"Backend error: {e.response.status_code}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

        # Save final response
        st.session_state.messages.append({"role": "assistant", "content": full_response})