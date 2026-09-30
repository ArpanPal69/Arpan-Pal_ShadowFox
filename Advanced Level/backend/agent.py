from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from schemas import RetrievedChunk
from pydantic import BaseModel, Field
import faiss_retriever
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY
import os

class AgentState(TypedDict):
    question: str
    original_question: str
    documents: List[RetrievedChunk]
    answer: str
    loop_count: int
    steps: List[str]
    document_ids: List[str]
    api_key: str

# LLMs will be initialized inside nodes dynamically using the API key from the state to ensure thread-safety and dynamic injection.

class GradeResult(BaseModel):
    is_relevant: bool = Field(description="True if the document contains information relevant to the question, False otherwise.")

class HallucinationResult(BaseModel):
    is_grounded: bool = Field(description="True if the answer is strictly grounded in the facts from the documents, False if it hallucinates.")

def retrieve_node(state: AgentState):
    state["steps"].append("Retrieving documents from FAISS and applying Cross-Encoder Reranking.")
    docs = faiss_retriever.get_relevant_documents(
        state["question"], 
        top_k=5, 
        doc_filter=state.get("document_ids")
    )
    return {"documents": docs, "loop_count": state.get("loop_count", 0) + 1}

def grade_documents_node(state: AgentState):
    state["steps"].append("Grading documents for relevance using LLM.")
    filtered_docs = []
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0, 
        api_key=state["api_key"], 
        base_url="https://openrouter.ai/api/v1"
    )
    grader = llm.with_structured_output(GradeResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a grader assessing relevance of a retrieved document to a user question. Answer True if it contains relevant information, False otherwise."),
        ("human", "Question: {question}\n\nDocument: {document}")
    ])
    grader_chain = prompt | grader
    
    for doc in state["documents"]:
        try:
            res = grader_chain.invoke({"question": state["question"], "document": doc.text})
            if res.is_relevant:
                filtered_docs.append(doc)
        except Exception:
            # On error, we assume irrelevant to be safe
            pass
            
    if len(filtered_docs) == 0 and len(state["documents"]) > 0:
         state["steps"].append("All retrieved documents were deemed irrelevant.")
    elif len(filtered_docs) > 0:
         state["steps"].append(f"{len(filtered_docs)} out of {len(state['documents'])} documents passed relevance grading.")
         
    return {"documents": filtered_docs}

def rewrite_query_node(state: AgentState):
    state["steps"].append("Rewriting the query to improve retrieval.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at optimizing user questions for vector store retrieval. Formulate a better question based on the original. Only output the new question."),
        ("human", "Original Question: {question}")
    ])
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0, 
        api_key=state["api_key"], 
        base_url="https://openrouter.ai/api/v1"
    )
    rewriter = prompt | llm
    better_query = rewriter.invoke({"question": state["question"]})
    return {"question": better_query.content}

def generate_node(state: AgentState):
    state["steps"].append("Generating answer based strictly on relevant documents.")
    context = "\n\n".join([f"Document {i+1} (Source: {doc.metadata.source}):\n{doc.text}" for i, doc in enumerate(state["documents"])])
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an advanced assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question comprehensively. If you don't know the answer, just say that you don't know. Provide detailed, well-structured answers using bullet points or paragraphs where appropriate to fully satisfy the user's query.\n\nContext:\n{context}"),
        ("human", "Question: {question}")
    ])
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0, 
        api_key=state["api_key"], 
        base_url="https://openrouter.ai/api/v1"
    )
    chain = prompt | llm
    answer = chain.invoke({"context": context, "question": state["question"]})
    return {"answer": answer.content}

def hallucination_checker_node(state: AgentState):
    state["steps"].append("Checking answer for hallucinations.")
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0, 
        api_key=state["api_key"], 
        base_url="https://openrouter.ai/api/v1"
    )
    checker = llm.with_structured_output(HallucinationResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a hallucination checker. Given the documents and an answer, evaluate if the answer is grounded ONLY in the facts present in the documents. Answer True if grounded, False if hallucinates."),
        ("human", "Documents: {documents}\n\nAnswer: {answer}")
    ])
    context = "\n\n".join([doc.text for doc in state["documents"]])
    chain = prompt | checker
    try:
        res = chain.invoke({"documents": context, "answer": state["answer"]})
        if res.is_grounded:
            state["steps"].append("Answer passed hallucination check.")
            return {"loop_count": state["loop_count"]}
        else:
            state["steps"].append("Hallucination detected. Need to re-retrieve or rewrite.")
            return {"answer": "HALLUCINATION_DETECTED"}
    except Exception:
         return {"loop_count": state["loop_count"]}

def decide_to_generate(state: AgentState):
    if len(state["documents"]) > 0:
        return "generate"
    if state["loop_count"] >= 3:
        return "end_with_failure"
    return "rewrite"
    
def check_hallucination(state: AgentState):
    if state.get("answer") == "HALLUCINATION_DETECTED":
        if state["loop_count"] >= 3:
            return "end_with_failure"
        return "rewrite"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade", grade_documents_node)
workflow.add_node("rewrite", rewrite_query_node)
workflow.add_node("generate", generate_node)
workflow.add_node("hallucination_check", hallucination_checker_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges("grade", decide_to_generate, {
    "generate": "generate",
    "rewrite": "rewrite",
    "end_with_failure": END
})
workflow.add_edge("rewrite", "retrieve")
workflow.add_edge("generate", "hallucination_check")
workflow.add_conditional_edges("hallucination_check", check_hallucination, {
    "rewrite": "rewrite",
    "end_with_failure": END,
    "__end__": END
})

rag_app = workflow.compile()
