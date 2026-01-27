import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Any
import re

class WebsiteIngestion:
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def scrape_page(self, url: str) -> Dict[str, Any]:
        """Scrape a single page and return its content and links."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Validate content
            if not content or len(content.strip()) < 100:
                print(f"Warning: Very little content found for {url}. The site may require JavaScript.")
                # We can choose to return None here or validation depending on strictness
                # For now, let's allow it but log it, or if it's truly empty, return None
                if not content or len(content.strip()) == 0:
                    return None
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Clean text
            content = self._clean_text(content)
            
            return {
                'url': url,
                'title': title_text,
                'content': content,
                'links': links
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"Access denied (403) for {url}. The site may have anti-bot protection.")
            elif e.response.status_code == 404:
                print(f"Page not found (404) for {url}.")
            else:
                print(f"HTTP error scaping {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from a page."""
        # Try to find main content areas
        main_content = ""
        
        # Common content selectors
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = element.get_text()
                break
        
        # If no main content found, use body
        if not main_content:
            body = soup.find('body')
            main_content = body.get_text() if body else ""
        
        return main_content
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        # Remove multiple consecutive spaces
        text = re.sub(r' +', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def scrape_website(self, base_url: str, max_pages: int = 10) -> List[Dict[str, str]]:
        """Scrape multiple pages from a website."""
        pages = []
        visited_urls = set()
        urls_to_visit = [base_url]
        
        while urls_to_visit and len(pages) < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in visited_urls:
                continue
                
            visited_urls.add(url)
            
            page_data = self.scrape_page(url)
            if page_data:
                pages.append(page_data)
                
                # Find additional links on the same domain
                if len(pages) < max_pages:
                    new_urls = page_data.get('links', [])
                    urls_to_visit.extend(new_urls)
            
            # Rate limiting
            time.sleep(self.delay)
        
        return pages
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract valid links from the page that belong to the same domain."""
        base_domain = urlparse(base_url).netloc
        links = set()
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Resolve relative URLs
            full_url = urljoin(base_url, href)
            
            # Parse the new URL
            parsed_url = urlparse(full_url)
            
            # Check conditions
            if (parsed_url.netloc == base_domain and  # Same domain
                parsed_url.scheme in ('http', 'https') and  # Valid scheme
                not any(full_url.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.css', '.js'])): # Not a static asset
                
                # Remove fragment
                clean_url = full_url.split('#')[0]
                
                # Avoid self-reference to the exact same page (simple check)
                if clean_url != base_url:
                    links.add(clean_url)
        
        return list(links)
    
    def chunk_content(self, pages: List[Dict[str, str]], chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, str]]:
        """Split content into chunks for better retrieval."""
        chunks = []
        
        for page in pages:
            content = page['content']
            
            # Split into chunks
            for i in range(0, len(content), chunk_size - overlap):
                chunk_text = content[i:i + chunk_size]
                
                if len(chunk_text.strip()) > 50:  # Skip very small chunks
                    chunks.append({
                        'url': page['url'],
                        'title': page['title'],
                        'content': chunk_text,
                        'chunk_id': f"{page['url']}_{i // (chunk_size - overlap)}"
                    })
        
        return chunks
