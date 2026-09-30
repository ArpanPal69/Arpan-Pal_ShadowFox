import streamlit as st
import os
import tempfile
from backend_logic import RAGPipeline

st.set_page_config(page_title="Document QA Assistant", layout="wide")

st.title("Document-Based Question Answering Assistant (RAG Pipeline)")

# Initialize session state for the RAG pipeline
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None

# Sidebar for Setup and Ingestion
with st.sidebar:
    st.header("1. Configuration")
    
    model_type = st.selectbox("Select Model Provider", ["OpenAI", "OpenRouter", "HuggingFace (Local)"])
    
    api_key = None
    openrouter_model = None
    if model_type in ["OpenAI", "OpenRouter"]:
        api_key = st.text_input(f"{model_type} API Key", type="password", help="Your key is not stored and is only used in memory.")
        if model_type == "OpenRouter":
            openrouter_model = st.text_input("OpenRouter Model Slug", value="openrouter/free", help="Find free models at openrouter.ai/models?max_price=0")
    else:
        st.info("Using free local HuggingFace models. No API key required! Note: The first run may take a few minutes to download the models (~1GB).")
    
    st.header("2. Document Upload")
    uploaded_files = st.file_uploader("Upload PDF or TXT files", type=["pdf", "txt"], accept_multiple_files=True)
    
    if st.button("Process Documents"):
        if model_type in ["OpenAI", "OpenRouter"] and not api_key:
            st.error(f"Please enter an {model_type} API Key first.")
        elif not uploaded_files:
            st.error("Please upload at least one file.")
        else:
            with st.spinner("Processing documents (extracting, chunking & embedding)..."):
                try:
                    # Initialize the pipeline ONCE
                    pipeline = RAGPipeline(api_key=api_key, model_type=model_type, openrouter_model=openrouter_model)
                    
                    for uploaded_file in uploaded_files:
                        # Save the uploaded file temporarily to process it
                        file_ext = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Process the document
                        pipeline.process_document(tmp_path, uploaded_file.name)
                        
                        # Clean up the temporary file
                        os.remove(tmp_path)
                        
                    st.session_state.rag_pipeline = pipeline
                    st.success(f"Successfully processed {len(uploaded_files)} document(s).")
                except Exception as e:
                    error_str = str(e)
                    if "insufficient_quota" in error_str or "429" in error_str or "credit_balance_exhausted" in error_str:
                        st.error(f"💳 **Billing Error:** Your {model_type} account has run out of credits or rate limited. Please switch to the free 'HuggingFace (Local)' model provider in the sidebar.")
                    elif "AuthenticationError" in error_str or "401" in error_str:
                        st.error(f"🔑 **Authentication Error:** The {model_type} API key provided is invalid. Please double-check your key.")
                    else:
                        st.error(f"⚠️ Error processing document: {e}")

# Main Interface for Retrieval & Generation
st.header("3. Ask Questions")
user_query = st.text_input("Enter your question about the uploaded document:")

if st.button("Ask"):
    if not st.session_state.rag_pipeline:
        st.error("Please select a model, upload, and process a document first.")
    elif not user_query.strip():
        st.warning("Please enter a valid question.")
    else:
        with st.spinner("Searching document and generating answer..."):
            try:
                result = st.session_state.rag_pipeline.answer_query(user_query)
                answer = result["answer"]
                sources = result["sources"]
                
                st.subheader("Answer")
                st.write(answer)
                
                # Innovative Feature: Source Context Visibility
                if sources:
                    st.subheader("Sources (Retrieved Context)")
                    for i, source in enumerate(sources):
                        with st.expander(f"Source Chunk {i+1}"):
                            st.write(source)
                            
            except Exception as e:
                error_str = str(e)
                if "insufficient_quota" in error_str or "429" in error_str or "credit_balance_exhausted" in error_str:
                    st.error(f"💳 **Billing Error:** Your {st.session_state.rag_pipeline.model_type} account has run out of credits. Please switch to the free 'HuggingFace (Local)' model provider in the sidebar.")
                elif "AuthenticationError" in error_str or "401" in error_str:
                    st.error(f"🔑 **Authentication Error:** The {st.session_state.rag_pipeline.model_type} API key provided is invalid. Please double-check your key.")
                else:
                    st.error(f"⚠️ Error generating answer: {e}")
