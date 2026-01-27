#!/usr/bin/env python3
"""
Flask version of the RAG chatbot for better compatibility
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re

load_dotenv()

app = Flask(__name__)

class SimpleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract content
            content = soup.get_text()
            content = re.sub(r'\s+', ' ', content).strip()
            
            return {
                'url': url,
                'title': title_text,
                'content': content[:2000]  # Limit content length
            }
        except Exception as e:
            return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'})
    
    scraper = SimpleScraper()
    result = scraper.scrape_page(url)
    
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    context = data.get('context', '')
    
    if not message:
        return jsonify({'error': 'Message is required'})
    
    # Simple mock response for now
    response = f"This is a mock response to: '{message}'. Context: {context[:100]}..."
    
    return jsonify({
        'response': response,
        'sources': [{'title': 'Sample Source', 'url': 'http://example.com'}]
    })

if __name__ == '__main__':
    print("🚀 Starting Flask RAG Chatbot...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000, host='0.0.0.0')
