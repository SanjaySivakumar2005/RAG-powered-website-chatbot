#!/usr/bin/env python3
"""
Simple test to check if basic functionality works
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    st.title("🤖 RAG Website Chatbot - Simple Test")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API Key found")
        st.code(f"API Key starts with: {api_key[:10]}...")
    else:
        st.error("❌ OpenAI API Key not found")
        st.info("Please add your API key to the .env file")
    
    st.markdown("### Basic Test Complete!")
    st.markdown("If you can see this page, Streamlit is working correctly.")
    
    # Test basic functionality
    if st.button("Test Basic Import"):
        try:
            import requests
            import bs4
            st.success("✅ Basic libraries imported successfully")
        except Exception as e:
            st.error(f"❌ Import error: {e}")

if __name__ == "__main__":
    main()
