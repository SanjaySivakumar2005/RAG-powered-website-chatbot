import os
import pickle
from typing import List, Dict, Any
import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize the vector store with embeddings."""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        self.vector_store = None
        self.index_path = "faiss_index"
        self.metadata_path = "faiss_metadata.pkl"
        
    def create_documents(self, chunks: List[Dict[str, str]]) -> List[Document]:
        """Convert chunks to LangChain documents."""
        documents = []
        
        for chunk in chunks:
            # Create metadata
            metadata = {
                'url': chunk['url'],
                'title': chunk['title'],
                'chunk_id': chunk.get('chunk_id', '')
            }
            
            # Create document
            doc = Document(
                page_content=chunk['content'],
                metadata=metadata
            )
            documents.append(doc)
        
        return documents
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents."""
        try:
            # Create FAISS index
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
            # Save the index and metadata
            self.save_vector_store()
            
            print(f"Created vector store with {len(documents)} documents")
            return self.vector_store
            
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            raise
    
    def save_vector_store(self):
        """Save the vector store to disk."""
        if self.vector_store:
            # Save FAISS index
            self.vector_store.save_local(self.index_path)
            
            # Save additional metadata
            metadata = {
                'docstore': self.vector_store.docstore,
                'index_to_docstore_id': self.vector_store.index_to_docstore_id
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            print("Vector store saved successfully")
    
    def load_vector_store(self) -> FAISS:
        """Load vector store from disk."""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load FAISS index
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                
                # Load metadata
                with open(self.metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                
                self.vector_store.docstore = metadata['docstore']
                self.vector_store.index_to_docstore_id = metadata['index_to_docstore_id']
                
                print("Vector store loaded successfully")
                return self.vector_store
            else:
                print("No existing vector store found")
                return None
                
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return None
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents."""
        if not self.vector_store:
            print("Vector store not initialized")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """Search for similar documents with relevance scores."""
        if not self.vector_store:
            print("Vector store not initialized")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"Error during similarity search with score: {str(e)}")
            return []
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to the vector store."""
        if not self.vector_store:
            print("Vector store not initialized. Creating new one...")
            self.create_vector_store(documents)
        else:
            try:
                self.vector_store.add_documents(documents)
                self.save_vector_store()
                print(f"Added {len(documents)} new documents to vector store")
            except Exception as e:
                print(f"Error adding documents: {str(e)}")
                raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        try:
            stats = {
                "status": "initialized",
                "total_documents": len(self.vector_store.docstore._dict),
                "index_dimension": self.vector_store.index.d,
                "index_type": type(self.vector_store.index).__name__
            }
            return stats
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def clear_store(self):
        """Clear the vector store."""
        try:
            # Remove files
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            # Clear memory
            self.vector_store = None
            
            print("Vector store cleared successfully")
        except Exception as e:
            print(f"Error clearing vector store: {str(e)}")
