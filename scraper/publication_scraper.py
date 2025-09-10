import requests
from bs4 import BeautifulSoup
from database.models import Publication, Faculty
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublicationScraper:
    def __init__(self, base_url: str = "https://scholar.google.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_publications(self, faculty_name: str) -> List[Dict]:
        """Search for publications by faculty name"""
        try:
            search_url = f"{self.base_url}/scholar?q=author:{faculty_name}"
            response = self.session.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            publications = []
            
            # Find publication items
            for item in soup.find_all('div', class_='gs_ri'):
                pub = {
                    'title': item.find('h3', class_='gs_rt').text,
                    'journal': item.find('div', class_='gs_a').text,
                    'year': self._extract_year(item),
                    'citations': self._extract_citations(item),
                    'doi': self._extract_doi(item)
                }
                publications.append(pub)
            
            return publications
            
        except Exception as e:
            logger.error(f"Error searching publications: {str(e)}")
            return []

    def _extract_year(self, item) -> int:
        """Extract publication year from item"""
        try:
            text = item.find('div', class_='gs_a').text
            year = int([s for s in text.split() if s.isdigit()][-1])
            return year
        except:
            return None

    def _extract_citations(self, item) -> int:
        """Extract citation count from item"""
        try:
            text = item.find('div', class_='gs_fl').text
            citations = int(text.split('Cited by ')[1].split()[0])
            return citations
        except:
            return 0

    def _extract_doi(self, item) -> str:
        """Extract DOI from item"""
        try:
            links = item.find_all('a')
            for link in links:
                if 'doi' in link.get('href', ''):
                    return link.get('href')
            return None
        except:
            return None

    def disambiguate_publications(self, publications: List[Dict], faculty: Faculty) -> List[Dict]:
        """Disambiguate publications by comparing with existing database records"""
        disambiguated = []
        for pub in publications:
            # Check if publication exists in database
            existing_pub = self.session.query(Publication).filter_by(
                title=pub['title'],
                journal=pub['journal']
            ).first()
            
            if existing_pub:
                # Update existing publication if needed
                if existing_pub.citations != pub['citations']:
                    existing_pub.citations = pub['citations']
                    existing_pub.last_updated = datetime.utcnow()
                    self.session.commit()
                disambiguated.append(existing_pub)
            else:
                # Create new publication
                new_pub = Publication(
                    title=pub['title'],
                    journal=pub['journal'],
                    year=pub['year'],
                    citations=pub['citations'],
                    doi=pub['doi'],
                    faculty=faculty,
                    is_disambiguated=True
                )
                self.session.add(new_pub)
                self.session.commit()
                disambiguated.append(new_pub)
        
        return disambiguated
