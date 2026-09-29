import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Agentic RAG Assistant", page_icon="🤖", layout="wide")

st.title("Production-Style Agentic RAG Assistant")
st.markdown("This application uses LangGraph, FastAPI, and FAISS to create a self-reflective, hallucination-resistant RAG system.")

with st.sidebar:
    st.header("1. Setup")
    openai_key = st.text_input("OpenAI API Key (Required)", type="password")
    
    st.header("2. Document Upload")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or Markdown", type=['pdf', 'txt', 'md'])
    if st.button("Ingest Document"):
        if uploaded_file is not None:
            with st.spinner("Processing document, creating embeddings..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success(response.json()["message"])
                    else:
                        st.error(f"Error: {response.json().get('detail', response.text)}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
        else:
            st.warning("Please select a file first.")

st.header("3. Query the Knowledge Base")
query = st.text_input("Ask a question about the uploaded documents:")

if st.button("Submit Query"):
    if not openai_key:
        st.error("Please provide an OpenAI API key in the sidebar.")
    elif query:
        with st.spinner("Agent is thinking, grading, and correcting..."):
            try:
                # We send the API key by temporarily setting it as an environment variable in the backend if possible,
                # but since this is a clean API, the backend should ideally take it in the request or headers.
                # However, our backend config expects it in os.environ.
                # To make this robust without modifying backend massively, let's just assume the backend has it OR 
                # we can pass it but we didn't add it to QueryRequest.
                # Let's adjust backend to use os.environ temporarily for this demo since it's local.
                
                # As a workaround, we'll inform the user if it's missing.
                payload = {"query": query}
                headers = {"x-api-key": openai_key}
                
                response = requests.post(f"{API_URL}/query", json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    
                    st.subheader("Answer")
                    
                    import time
                    def stream_text(text):
                        for word in text.split(" "):
                            yield word + " "
                            time.sleep(0.03)
                            
                    st.write_stream(stream_text(data["answer"]))
                    
                    with st.expander("Agent Reasoning Steps"):
                        for step in data["agent_steps"]:
                            st.write(f"- {step}")
                            
                    with st.expander("Citations (Retrieved Chunks)"):
                        if data["citations"]:
                            for chunk in data["citations"]:
                                meta = chunk["metadata"]
                                page_info = f" (Page {meta['page']})" if meta.get("page") else ""
                                st.markdown(f"**Source: {meta['source']}{page_info}** - Score: {chunk.get('relevance_score', 0):.2f}")
                                st.info(chunk["text"])
                        else:
                            st.write("No citations were used.")
                else:
                    st.error(f"Error: {response.json().get('detail', response.text)}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
    else:
        st.warning("Please enter a query.")
