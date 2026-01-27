import os
import gc
from typing import List, Dict, Any
import torch
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

from .vector_store import VectorStore

load_dotenv()

class RAGPipeline:
    def __init__(self, 
                 model_name: str = "local-llm",
                 temperature: float = 0.1,
                 vector_store: VectorStore = None):
        """Initialize the RAG pipeline."""
        self.model_name = model_name
        if model_name == "local-llm":
            print("Loading local T5 model (Ultra-Light)...")
            # Explicitly clear any existing torch memory
            if torch.cuda.is_available(): torch.cuda.empty_cache()
            
            self.llm = HuggingFacePipeline.from_model_id(
                model_id="t5-small",
                task="text2text-generation",
                model_kwargs={"temperature": 0.0, "max_length": 128}
            )
            print("Model loaded successfully.")
        else:
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        
        self.vector_store = vector_store
        self.qa_chain = None
        self.conversation_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def create_qa_chain(self) -> RetrievalQA:
        """Create a question-answering chain."""
        if not self.vector_store or not self.vector_store.vector_store:
            raise ValueError("Vector store not initialized")
        
        # Create retriever
        retriever = self.vector_store.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}
        )
        
        # Create prompt template
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer from the context, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        Always say "thanks for asking!" at the end of the answer.
        
        Context: {context}
        
        Question: {question}
        
        Helpful Answer:"""
        
        QA_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True
        )
        
        return self.qa_chain
    
    def create_conversational_chain(self) -> ConversationalRetrievalChain:
        """Create a conversational RAG chain."""
        if not self.vector_store or not self.vector_store.vector_store:
            raise ValueError("Vector store not initialized")
        
        # Create retriever
        retriever = self.vector_store.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}
        )
        
        # Create conversational chain
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            verbose=True
        )
        
        return self.conversation_chain
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG pipeline."""
        if not self.qa_chain:
            self.create_qa_chain()
        
        try:
            result = self.qa_chain({"query": question})
            
            # Format response
            response = {
                "answer": result.get("result", ""),
                "source_documents": result.get("source_documents", []),
                "question": question
            }
            
            # Add source information
            sources = []
            for doc in response["source_documents"]:
                sources.append({
                    "content": doc.page_content[:200] + "...",
                    "url": doc.metadata.get("url", ""),
                    "title": doc.metadata.get("title", "")
                })
            
            response["sources"] = sources
            
            return response
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def chat(self, question: str) -> Dict[str, Any]:
        """Chat with the RAG pipeline (Simplified for memory)."""
        # Switching to simplified QA chain instead of ConversationalRetrievalChain to save memory
        if not self.qa_chain:
            self.create_qa_chain()
        
        try:
            # Explicit memory management before inference
            gc.collect()
            
            # We use the QA chain directly to avoid keeping long chat history in memory
            result = self.qa_chain({"query": question})
            
            # Format response
            response = {
                "answer": result.get("result", ""),
                "source_documents": result.get("source_documents", []),
                "chat_history": [], # Minimal memory usage
                "question": question
            }
            
            # Add source information
            sources = []
            for doc in response["source_documents"]:
                sources.append({
                    "content": doc.page_content[:200] + "...",
                    "url": doc.metadata.get("url", ""),
                    "title": doc.metadata.get("title", "")
                })
            
            response["sources"] = sources
            
            return response
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "chat_history": self.memory.chat_memory.messages,
                "question": question
            }
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        print("Conversation memory cleared")
    
    def get_relevant_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Get relevant documents for a query."""
        if not self.vector_store:
            return []
        
        docs = self.vector_store.similarity_search(query, k=k)
        
        relevant_docs = []
        for doc in docs:
            relevant_docs.append({
                "content": doc.page_content,
                "url": doc.metadata.get("url", ""),
                "title": doc.metadata.get("title", ""),
                "chunk_id": doc.metadata.get("chunk_id", "")
            })
        
        return relevant_docs
    
    def update_vector_store(self, vector_store: VectorStore):
        """Update the vector store used by the pipeline."""
        self.vector_store = vector_store
        # Reset chains to use new vector store
        self.qa_chain = None
        self.conversation_chain = None
        print("Vector store updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        # Helper to get model name safely
        model_name = getattr(self.llm, "model_name", "local-model")
        
        stats = {
            "llm_model": model_name,
            "temperature": getattr(self.llm, "temperature", 0.1),
            "memory_messages": len(self.memory.chat_memory.messages),
            "qa_chain_initialized": self.qa_chain is not None,
            "conversation_chain_initialized": self.conversation_chain is not None
        }
        
        if self.vector_store:
            stats.update(self.vector_store.get_stats())
        
        return stats
