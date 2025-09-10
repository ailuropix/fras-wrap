import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict
import urllib.parse
import json

class PublicationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_publications(self, faculty_name, department, college=""):
        """Scrape real publications from multiple sources"""
        print(f"Scraping real publications for {faculty_name} from {department}, {college}")
        
        all_publications = []
        
        # Try Google Scholar first
        gs_publications = self.search_google_scholar(faculty_name, department, college)
        all_publications.extend(gs_publications)
        
        # Try CrossRef API for additional publications
        crossref_publications = self.search_crossref(faculty_name)
        all_publications.extend(crossref_publications)
        
        # Remove duplicates
        unique_publications = self.resolve_ambiguity(all_publications)
        
        print(f"Found {len(unique_publications)} real publications for {faculty_name}")
        return unique_publications

    def search_google_scholar(self, faculty_name, department, college=""):
        """Search Google Scholar for real publications"""
        try:
            # Construct search query
            query_parts = [faculty_name]
            if department:
                query_parts.append(department)
            if college:
                query_parts.append(college)
            
            query = " ".join(query_parts)
            encoded_query = urllib.parse.quote(query)
            
            # Google Scholar search URL
            url = f"https://scholar.google.com/scholar?q={encoded_query}&hl=en"
            
            print(f"Searching Google Scholar: {url}")
            
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch Google Scholar results: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            publications = []
            
            # Parse Google Scholar results
            results = soup.find_all('div', class_='gs_ri')
            
            for result in results[:10]:  # Limit to top 10 results
                try:
                    # Extract title
                    title_elem = result.find('h3', class_='gs_rt')
                    if not title_elem:
                        continue
                    
                    title_link = title_elem.find('a')
                    title = title_link.text if title_link else title_elem.text
                    title = re.sub(r'\[.*?\]', '', title).strip()  # Remove [PDF] etc.
                    
                    # Extract authors and publication info
                    authors_elem = result.find('div', class_='gs_a')
                    authors_text = authors_elem.text if authors_elem else ""
                    
                    # Parse authors and year
                    authors = ""
                    year = None
                    if authors_text:
                        # Extract year (usually at the end)
                        year_match = re.search(r'\b(19|20)\d{2}\b', authors_text)
                        if year_match:
                            year = int(year_match.group())
                        
                        # Extract authors (before the year and venue)
                        authors_part = re.split(r'\s*-\s*', authors_text)[0]
                        authors = authors_part.strip()
                    
                    # Extract citation count
                    citations = 0
                    citation_elem = result.find('a', string=re.compile(r'Cited by \d+'))
                    if citation_elem:
                        citation_match = re.search(r'Cited by (\d+)', citation_elem.text)
                        if citation_match:
                            citations = int(citation_match.group(1))
                    
                    # Extract journal/venue
                    journal = ""
                    if authors_text and '-' in authors_text:
                        parts = authors_text.split('-')
                        if len(parts) > 1:
                            journal = parts[1].strip()
                            # Remove year from journal name
                            journal = re.sub(r'\b(19|20)\d{2}\b', '', journal).strip()
                    
                    # Only include if faculty name appears in authors
                    if faculty_name.lower() in authors.lower():
                        publications.append({
                            'title': title,
                            'authors': authors,
                            'journal': journal,
                            'year': year or 0,
                            'citations': citations,
                            'doi': '',
                            'source': 'Google Scholar'
                        })
                
                except Exception as e:
                    print(f"Error parsing Google Scholar result: {e}")
                    continue
            
            print(f"Found {len(publications)} publications from Google Scholar")
            return publications
            
        except Exception as e:
            print(f"Error searching Google Scholar: {e}")
            return []

    def search_crossref(self, faculty_name):
        """Search CrossRef API for publications"""
        try:
            # CrossRef API search
            url = "https://api.crossref.org/works"
            params = {
                'query.author': faculty_name,
                'rows': 20,
                'sort': 'relevance'
            }
            
            print(f"Searching CrossRef API for {faculty_name}")
            
            response = self.session.get(url, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch CrossRef results: {response.status_code}")
                return []
            
            data = response.json()
            publications = []
            
            for item in data.get('message', {}).get('items', []):
                try:
                    # Extract publication details
                    title = item.get('title', [''])[0] if item.get('title') else ''
                    
                    # Extract authors
                    authors_list = []
                    for author in item.get('author', []):
                        given = author.get('given', '')
                        family = author.get('family', '')
                        if given and family:
                            authors_list.append(f"{given} {family}")
                        elif family:
                            authors_list.append(family)
                    
                    authors = ', '.join(authors_list)
                    
                    # Multi-factor verification for accurate attribution
                    if not self.verify_publication_attribution(item, faculty_name, department, college):
                        continue
                    
                    # Extract other details
                    journal = item.get('container-title', [''])[0] if item.get('container-title') else ''
                    
                    # Extract year
                    year = 0
                    if item.get('published-print'):
                        year = item['published-print']['date-parts'][0][0]
                    elif item.get('published-online'):
                        year = item['published-online']['date-parts'][0][0]
                    
                    # Extract DOI
                    doi = item.get('DOI', '')
                    
                    # Extract citation count (if available)
                    citations = item.get('is-referenced-by-count', 0)
                    
                    publications.append({
                        'title': title,
                        'authors': authors,
                        'journal': journal,
                        'year': year,
                        'citations': citations,
                        'doi': doi,
                        'source': 'CrossRef'
                    })
                
                except Exception as e:
                    print(f"Error parsing CrossRef result: {e}")
                    continue
            
            print(f"Found {len(publications)} publications from CrossRef")
            return publications
            
        except Exception as e:
            print(f"Error searching CrossRef: {e}")
            return []

    def search_researchgate(self, faculty_name, department, college=""):
        """ResearchGate search - simplified due to anti-scraping measures"""
        # ResearchGate has strong anti-scraping measures
        # For now, return empty list but keep method for future enhancement
        return []

    def resolve_ambiguity(self, publications):
        """Remove duplicate publications by title similarity"""
        if not publications:
            return []
        
        unique_publications = []
        seen_titles = set()
        
        for pub in publications:
            title = pub.get('title', '').lower().strip()
            if not title:
                continue
            
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', title)
            normalized_title = ' '.join(normalized_title.split())
            
            # Check if we've seen a similar title
            is_duplicate = False
            for seen_title in seen_titles:
                # Simple similarity check - if titles are very similar, consider duplicate
                if self.title_similarity(normalized_title, seen_title) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.add(normalized_title)
                unique_publications.append(pub)
        
        return unique_publications

    def title_similarity(self, title1, title2):
        """Calculate similarity between two titles"""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
