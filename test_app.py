#!/usr/bin/env python3
"""
Test script for the RAG Website Chatbot
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ingestion import WebsiteIngestion
from src.web_scraper import AdvancedWebScraper
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline

def test_basic_functionality():
    """Test basic functionality of the RAG system."""
    print("🧪 Testing RAG Website Chatbot...")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables!")
        print("Please set up your .env file with your OpenAI API key.")
        return False
    
    print("✅ Environment variables loaded")
    
    # Test website ingestion
    print("\n📥 Testing website ingestion...")
    try:
        ingestion = WebsiteIngestion(delay=0.5)
        
        # Use a simple test website
        test_url = "https://www.python.org/about/"
        print(f"Scraping: {test_url}")
        
        pages = ingestion.scrape_website(test_url, max_pages=2)
        
        if pages:
            print(f"✅ Successfully scraped {len(pages)} pages")
            for i, page in enumerate(pages[:2]):
                print(f"  Page {i+1}: {page['title'][:50]}...")
                print(f"    Content length: {len(page['content'])} characters")
        else:
            print("❌ No pages scraped")
            return False
            
    except Exception as e:
        print(f"❌ Error during ingestion: {str(e)}")
        return False
    
    # Test vector store
    print("\n🗄️ Testing vector store...")
    try:
        vector_store = VectorStore()
        
        # Chunk content
        chunks = ingestion.chunk_content(pages, chunk_size=500, overlap=100)
        print(f"Created {len(chunks)} chunks")
        
        # Create documents
        documents = vector_store.create_documents(chunks)
        
        # Create vector store
        vector_store.create_vector_store(documents)
        print("✅ Vector store created successfully")
        
        # Test similarity search
        results = vector_store.similarity_search("Python programming", k=2)
        print(f"✅ Similarity search returned {len(results)} results")
        
    except Exception as e:
        print(f"❌ Error with vector store: {str(e)}")
        return False
    
    # Test RAG pipeline
    print("\n🤖 Testing RAG pipeline...")
    try:
        rag_pipeline = RAGPipeline(vector_store=vector_store)
        
        # Test question answering
        question = "What is Python?"
        print(f"Question: {question}")
        
        result = rag_pipeline.answer_question(question)
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {len(result['sources'])}")
        
        if result['answer'] and not result['answer'].startswith("Error"):
            print("✅ RAG pipeline working correctly")
        else:
            print("❌ RAG pipeline failed")
            return False
            
    except Exception as e:
        print(f"❌ Error with RAG pipeline: {str(e)}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

def test_advanced_scraper():
    """Test the advanced web scraper."""
    print("\n🕷️ Testing advanced web scraper...")
    
    try:
        scraper = AdvancedWebScraper(delay=0.5, max_depth=1)
        
        test_url = "https://www.python.org/about/"
        pages = scraper.crawl_website(test_url, max_pages=3)
        
        if pages:
            print(f"✅ Advanced scraper crawled {len(pages)} pages")
            for page in pages[:2]:
                print(f"  - {page['title'][:50]}...")
                print(f"    Word count: {page['word_count']}")
                print(f"    Headings: {sum(len(h) for h in page['headings'].values())}")
        else:
            print("❌ Advanced scraper failed")
            return False
            
    except Exception as e:
        print(f"❌ Error with advanced scraper: {str(e)}")
        return False
    
    return True

def cleanup_test_files():
    """Clean up test files."""
    print("\n🧹 Cleaning up test files...")
    
    import shutil
    test_files = ["faiss_index", "faiss_metadata.pkl"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)
                print(f"  Removed: {file}")
            except Exception as e:
                print(f"  Error removing {file}: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting RAG Website Chatbot Tests")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_basic_functionality()
    success &= test_advanced_scraper()
    
    # Cleanup
    cleanup_test_files()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        print("\nTo run the chatbot:")
        print("  streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
