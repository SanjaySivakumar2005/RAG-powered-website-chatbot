#!/usr/bin/env python3
"""
Quick start script for RAG Website Chatbot
"""

import os
import sys

def main():
    print("🚀 RAG Website Chatbot Quick Start")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Check if .env file exists
    env_file = ".env"
    env_example = ".env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print("📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created")
            print("⚠️  Please edit .env file and add your OpenAI API key!")
        else:
            print("❌ .env.example file not found")
            sys.exit(1)
    else:
        print("✅ .env file exists")
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("✅ OpenAI API key found")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Error installing dependencies:")
            print(result.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        sys.exit(1)
    
    # Run the app
    print("\n🌟 Starting the chatbot...")
    print("The app will open in your web browser")
    print("Press Ctrl+C to stop the server")
    
    try:
        import subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting app: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
