import os
import sys
from src.ingestion import WebsiteIngestion
from src.vector_store import VectorStore
import gc

def ingest_claysys():
    url = "https://www.claysys.com"
    print(f"🚀 Starting manual ingestion for {url}...")
    
    # 1. Scrape
    ingestion = WebsiteIngestion(delay=0.1)
    pages = ingestion.scrape_website(url, max_pages=10)
    
    if not pages:
        print("❌ Failed to scrape pages.")
        return
    
    print(f"✅ Scraped {len(pages)} pages.")
    
    # 2. Chunk
    chunks = ingestion.chunk_content(pages, chunk_size=500, overlap=50)
    print(f"✅ Created {len(chunks)} chunks.")
    
    # 3. Vector Store
    vs = VectorStore()
    # Force clear old data
    vs.clear_store()
    
    documents = vs.create_documents(chunks)
    vs.create_vector_store(documents)
    
    print("✅ Vector store updated successfully with ClaySys data!")
    
    # Cleanup
    del pages, chunks, documents
    gc.collect()

if __name__ == "__main__":
    ingest_claysys()
