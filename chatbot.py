import os
import streamlit as st

# Attempt to import heavy libraries safely
try:
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    # Load embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # Load FAISS index
    if os.path.exists("faiss_index"):
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    else:
        db = None
except Exception as e:
    # We don't want to show the error immediately on import if possible, 
    # but we'll store it to show during the chat or as a warning.
    _import_error = str(e)
    db = None
else:
    _import_error = None

def get_answer(query):
    if _import_error:
        return f"System Error: {_import_error}\n\nThis is likely a Python 3.14 compatibility issue with numpy. Please see instructions to fix."
    
    if db is None:
        return "Sorry, the AI engine is currently unavailable (FAISS index 'faiss_index' not found)."
        
    try:
        docs = db.similarity_search(query, k=2)
        if not docs:
            return "Sorry, I could not find relevant information."
        return docs[0].page_content
    except Exception as e:
        return f"Error during search: {str(e)}"

def get_answer_safe(query):
    """A wrapper for get_answer to ensure no crashes occur in the UI."""
    try:
        return get_answer(query)
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
