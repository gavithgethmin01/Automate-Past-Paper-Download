import requests
from bs4 import BeautifulSoup
import json
import csv
from urllib.parse import urljoin
import time

class PastPapersWikiScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.papers = []
    
    def fetch_page(self, url):
        """Fetch a webpage and return BeautifulSoup object"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_paper_links(self, soup):
        """Extract all past paper links from the page"""
        papers = []
        
        # Find all articles with class 'jeg_post'
        articles = soup.find_all('article', class_='jeg_post')
        
        for article in articles:
            try:
                # Find the h3 tag with class 'jeg_post_title'
                title_tag = article.find('h3', class_='jeg_post_title')
                
                if title_tag:
                    # Find the anchor tag inside h3
                    link_tag = title_tag.find('a', href=True)
                    
                    if link_tag:
                        paper_info = {
                            'title': link_tag.get_text(strip=True),
                            'url': link_tag['href']
                        }
                        
                        # Extract description if available
                        excerpt = article.find('div', class_='jeg_post_excerpt')
                        if excerpt:
                            desc_p = excerpt.find('p')
                            if desc_p:
                                paper_info['description'] = desc_p.get_text(strip=True)
                        
                        # Extract image if available
                        thumb = article.find('div', class_='jeg_thumb')
                        if thumb:
                            img = thumb.find('img')
                            if img:
                                paper_info['image'] = img.get('src') or img.get('data-src')
                        
                        papers.append(paper_info)
                        print(f"Found: {paper_info['title']}")
            
            except Exception as e:
                print(f"Error extracting paper info: {e}")
                continue
        
        return papers
    
    def scrape_all_papers(self):
        """Scrape all papers from the main page"""
        soup = self.fetch_page(self.base_url)
        
        if not soup:
            print("Failed to fetch the page")
            return []
        
        self.papers = self.extract_paper_links(soup)
        
        print(f"\n=== Total papers found: {len(self.papers)} ===")
        return self.papers
    
    def save_to_json(self, filename='past_papers.json'):
        """Save scraped papers to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.papers, f, indent=2, ensure_ascii=False)
        print(f"\nData saved to {filename}")
    
    def save_to_csv(self, filename='past_papers.csv'):
        """Save scraped papers to CSV file"""
        if not self.papers:
            print("No papers to save")
            return
        
        keys = self.papers[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.papers)
        
        print(f"Data saved to {filename}")
    
    def print_papers(self):
        """Print all papers in a formatted way"""
        print("\n" + "="*80)
        print("PAST PAPERS LIST")
        print("="*80)
        
        for i, paper in enumerate(self.papers, 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   URL: {paper['url']}")
            if 'description' in paper:
                print(f"   Description: {paper['description']}")
            print("-" * 80)
    
    def filter_by_year(self, year):
        """Filter papers by year"""
        filtered = [p for p in self.papers if str(year) in p['title']]
        print(f"\nFound {len(filtered)} papers for year {year}")
        return filtered
    
    def filter_by_type(self, paper_type):
        """Filter papers by type (e.g., 'Marking Scheme', 'Past Paper')"""
        filtered = [p for p in self.papers if paper_type.lower() in p['title'].lower()]
        print(f"\nFound {len(filtered)} papers of type '{paper_type}'")
        return filtered


# Example usage
if __name__ == "__main__":
    # URL for General English Past Papers Wiki
    url = "https://pastpapers.wiki/category/general-english/"
    
    # Create scraper instance
    scraper = PastPapersWikiScraper(url)
    
    # Scrape all papers
    papers = scraper.scrape_all_papers()
    
    # Print all papers
    scraper.print_papers()
    
    # Save to files
    scraper.save_to_json('general_english_papers.json')
    scraper.save_to_csv('general_english_papers.csv')
    
    # Example: Filter by year
    print("\n" + "="*80)
    papers_2024 = scraper.filter_by_year(2024)
    for paper in papers_2024:
        print(f"- {paper['title']}: {paper['url']}")
    
    # Example: Filter by type
    print("\n" + "="*80)
    marking_schemes = scraper.filter_by_type("Marking Scheme")
    for scheme in marking_schemes:
        print(f"- {scheme['title']}: {scheme['url']}")
