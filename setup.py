from setuptools import setup, find_packages

setup(
    name="rag-website-chatbot",
    version="1.0.0",
    description="RAG-Powered Website Chatbot",
    packages=find_packages(),
    install_requires=[
        "langchain==0.1.0",
        "langchain-openai==0.0.5",
        "langchain-community==0.0.12",
        "faiss-cpu==1.7.4",
        "beautifulsoup4==4.12.2",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "streamlit==1.29.0",
        "tiktoken==0.5.2",
        "numpy==1.24.3",
        "pandas==2.0.3",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
)
