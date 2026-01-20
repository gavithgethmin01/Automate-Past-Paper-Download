import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
import time

class PastPapersScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.scraped_data = {}
    
    def fetch_page(self, url):
        """Fetch a webpage and return BeautifulSoup object"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, soup, base_url):
        """Extract all links from the page"""
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            links.append({
                'text': link.get_text(strip=True),
                'url': full_url
            })
        return links
    
    def extract_text_content(self, soup):
        """Extract main text content from the page"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        return text
    
    def extract_metadata(self, soup):
        """Extract metadata from the page"""
        metadata = {
            'title': soup.title.string if soup.title else '',
            'meta_description': '',
            'meta_keywords': ''
        }
        
        # Extract meta tags
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['meta_description'] = meta_desc.get('content', '')
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['meta_keywords'] = meta_keywords.get('content', '')
        
        return metadata
    
    def scrape_page(self, url):
        """Scrape a single page and extract all relevant information"""
        print(f"Scraping: {url}")
        
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        page_data = {
            'url': url,
            'metadata': self.extract_metadata(soup),
            'links': self.extract_links(soup, url),
            'text_content': self.extract_text_content(soup),
            'html_source': str(soup)
        }
        
        return page_data
    
    def save_to_file(self, data, filename='scraped_data.json'):
        """Save scraped data to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def save_html(self, html_content, filename='page_source.html'):
        """Save HTML source to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML saved to {filename}")
    
    def run(self, save_html=True, save_json=True):
        """Main method to run the scraper"""
        page_data = self.scrape_page(self.base_url)
        
        if page_data:
            if save_json:
                self.save_to_file(page_data, 'scraped_data.json')
            
            if save_html:
                self.save_html(page_data['html_source'], 'page_source.html')
            
            # Print summary
            print("\n=== Scraping Summary ===")
            print(f"Title: {page_data['metadata']['title']}")
            print(f"Links found: {len(page_data['links'])}")
            print(f"Text length: {len(page_data['text_content'])} characters")
            
            return page_data
        else:
            print("Failed to scrape the page")
            return None


# Example usage
if __name__ == "__main__":
    # Replace with the actual URL you want to scrape
    url = "https://example.com/general-english-past-papers"
    
    scraper = PastPapersScraper(url)
    data = scraper.run(save_html=True, save_json=True)
    
    # Optional: Print some extracted information
    if data:
        print("\n=== First 5 Links ===")
        for link in data['links'][:5]:
            print(f"- {link['text']}: {link['url']}")
