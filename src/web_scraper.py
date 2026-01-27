import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Set
import re
from collections import deque

class AdvancedWebScraper:
    def __init__(self, delay: float = 1.0, max_depth: int = 2):
        self.delay = delay
        self.max_depth = max_depth
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.visited_urls: Set[str] = set()
        self.domain_restrictions = True
        
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to the same domain."""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)
            
            # Check if same domain (if restriction enabled)
            if self.domain_restrictions and parsed.netloc != base_parsed.netloc:
                return False
                
            # Skip common non-content URLs
            skip_patterns = [
                r'.*\.(pdf|jpg|jpeg|png|gif|svg|css|js|ico)$',
                r'.*/login.*',
                r'.*/register.*',
                r'.*/logout.*',
                r'.*/admin.*',
                r'.*/api.*',
                r'.*/feed.*',
                r'.*/sitemap.*',
                r'.*/search.*',
                r'.*/cart.*',
                r'.*/checkout.*',
                r'.*/account.*',
                r'.*/profile.*',
                r'.*/settings.*',
                r'.*/help.*',
                r'.*/faq.*',
                r'.*/contact.*',
                r'.*/privacy.*',
                r'.*/terms.*',
                r'.*/cookie.*',
                r'.*/legal.*'
            ]
            
            for pattern in skip_patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return False
                    
            return True
            
        except Exception:
            return False
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all valid links from a page."""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Remove fragment and query parameters for comparison
            clean_url = re.sub(r'#.*$', '', absolute_url)
            clean_url = re.sub(r'\?.*$', '', clean_url)
            
            if self.is_valid_url(clean_url, base_url):
                links.append(clean_url)
        
        return list(set(links))  # Remove duplicates
    
    def scrape_page(self, url: str) -> Dict[str, str]:
        """Scrape a single page and return its content."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
                element.decompose()
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # Extract main content with improved selectors
            content = self._extract_content_smart(soup)
            
            # Clean text
            content = self._clean_text(content)
            
            # Extract structured data
            headings = self._extract_headings(soup)
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'content': content,
                'headings': headings,
                'word_count': len(content.split())
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_content_smart(self, soup: BeautifulSoup) -> str:
        """Smart content extraction using multiple strategies."""
        content_strategies = [
            # Strategy 1: Look for main content areas
            ['main', 'article', '[role="main"]'],
            # Strategy 2: Common content classes
            ['.content', '.main-content', '.post-content', '.entry-content', '.article-content'],
            # Strategy 3: Common content IDs
            ['#content', '#main', '#post-content', '#article-content'],
            # Strategy 4: Large text blocks
            ['div', 'section']
        ]
        
        for selectors in content_strategies:
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text().strip()
                    # Check if content is substantial
                    if len(content) > 200 and len(content.split()) > 50:
                        return content
        
        # Fallback to body
        body = soup.find('body')
        return body.get_text().strip() if body else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract heading structure."""
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in headings.keys():
            elements = soup.find_all(level)
            headings[level] = [elem.get_text().strip() for elem in elements if elem.get_text().strip()]
        
        return headings
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\~\`]', '', text)
        # Remove multiple consecutive spaces
        text = re.sub(r' +', ' ', text)
        # Remove multiple consecutive punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def crawl_website(self, start_url: str, max_pages: int = 50) -> List[Dict[str, str]]:
        """Crawl a website using BFS approach."""
        pages = []
        urls_to_visit = deque([(start_url, 0)])  # (url, depth)
        
        while urls_to_visit and len(pages) < max_pages:
            url, depth = urls_to_visit.popleft()
            
            if url in self.visited_urls or depth > self.max_depth:
                continue
            
            self.visited_urls.add(url)
            
            print(f"Scraping: {url} (depth: {depth})")
            
            page_data = self.scrape_page(url)
            if page_data:
                pages.append(page_data)
                
                # Extract links if we haven't reached max pages and depth is within limit
                if len(pages) < max_pages and depth < self.max_depth:
                    try:
                        response = self.session.get(url, timeout=10)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        new_links = self.extract_links(soup, url)
                        for link in new_links:
                            if link not in self.visited_urls:
                                urls_to_visit.append((link, depth + 1))
                                
                    except Exception as e:
                        print(f"Error extracting links from {url}: {str(e)}")
            
            # Rate limiting
            time.sleep(self.delay)
        
        print(f"Crawling completed. Scraped {len(pages)} pages.")
        return pages
    
    def scrape_sitemap(self, base_url: str) -> List[str]:
        """Try to extract URLs from sitemap.xml."""
        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemap/sitemap.xml"
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'xml')
                urls = []
                
                for loc in soup.find_all('loc'):
                    url = loc.get_text().strip()
                    if self.is_valid_url(url, base_url):
                        urls.append(url)
                
                if urls:
                    print(f"Found {len(urls)} URLs in sitemap: {sitemap_url}")
                    return urls
                    
            except Exception as e:
                print(f"Error fetching sitemap {sitemap_url}: {str(e)}")
                continue
        
        return []
    
    def chunk_content_by_structure(self, pages: List[Dict[str, str]], 
                                 chunk_size: int = 1000, 
                                 overlap: int = 200) -> List[Dict[str, str]]:
        """Split content into chunks using semantic boundaries."""
        chunks = []
        
        for page in pages:
            content = page['content']
            headings = page.get('headings', {})
            
            # Try to chunk by headings first
            heading_chunks = self._chunk_by_headings(content, headings)
            
            if heading_chunks:
                for chunk_text in heading_chunks:
                    if len(chunk_text.strip()) > 50:
                        chunks.append({
                            'url': page['url'],
                            'title': page['title'],
                            'content': chunk_text,
                            'chunk_id': f"{page['url']}_{len(chunks)}",
                            'chunk_type': 'semantic'
                        })
            else:
                # Fallback to simple chunking
                for i in range(0, len(content), chunk_size - overlap):
                    chunk_text = content[i:i + chunk_size]
                    
                    if len(chunk_text.strip()) > 50:
                        chunks.append({
                            'url': page['url'],
                            'title': page['title'],
                            'content': chunk_text,
                            'chunk_id': f"{page['url']}_{i // (chunk_size - overlap)}",
                            'chunk_type': 'fixed_size'
                        })
        
        return chunks
    
    def _chunk_by_headings(self, content: str, headings: Dict[str, List[str]]) -> List[str]:
        """Try to chunk content based on heading structure."""
        # This is a simplified implementation
        # In practice, you'd need to map headings to their positions in the content
        
        chunks = []
        
        # Look for natural break points
        sentences = re.split(r'[.!?]+', content)
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < 1000:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
