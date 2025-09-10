from datetime import datetime
from typing import List, Dict, Optional
from app import Faculty, Publication
from database import get_faculty_publications
from scrapers.publication_scraper import PublicationScraper

class PublicationComparator:
    def __init__(self):
        self.scraper = PublicationScraper()

    def compare_publications(self, old_pubs: List[Publication], new_pubs: List[Dict]) -> Dict:
        """
        Compare old and new publications and return changes
        Returns a dictionary with:
        - added: New publications
        - updated: Updated publications
        - removed: Removed publications
        """
        changes = {
            'added': [],
            'updated': [],
            'removed': []
        }

        # Convert old publications to dict for easier comparison
        old_pub_dict = {pub.title.lower(): pub for pub in old_pubs}

        # Track new publications
        new_pub_titles = set([pub['title'].lower() for pub in new_pubs])

        # Check for added and updated publications
        for new_pub in new_pubs:
            title = new_pub['title'].lower()
            if title not in old_pub_dict:
                changes['added'].append(new_pub)
            else:
                old_pub = old_pub_dict[title]
                if (old_pub.citations != new_pub.get('citations', 0) or
                    old_pub.journal != new_pub.get('journal', '') or
                    old_pub.year != new_pub.get('year', 0)):
                    changes['updated'].append({
                        'old': {
                            'citations': old_pub.citations,
                            'journal': old_pub.journal,
                            'year': old_pub.year
                        },
                        'new': new_pub
                    })

        # Check for removed publications
        for old_title in old_pub_dict.keys():
            if old_title not in new_pub_titles:
                changes['removed'].append(old_title)

        return changes

    def update_faculty_publications(self, faculty_id: int) -> Dict:
        """Update publications for a specific faculty member"""
        # Get existing publications
        faculty_data = get_faculty_publications(faculty_id)
        if not faculty_data:
            return {'error': 'Faculty not found'}

        faculty = faculty_data['faculty']
        old_publications = faculty_data['publications']

        # Scrape new publications
        new_publications = self.scraper.scrape_publications(
            faculty.name,
            faculty.department
        )

        # Compare publications
        changes = self.compare_publications(old_publications, new_publications)

        return {
            'faculty_id': faculty_id,
            'changes': changes,
            'last_updated': datetime.utcnow().isoformat()
        }

    def get_publication_metrics(self, publications: List[Publication]) -> Dict:
        """Calculate metrics for a list of publications"""
        if not publications:
            return {
                'total_publications': 0,
                'total_citations': 0,
                'average_citations': 0,
                'recent_publications': 0
            }

        total_publications = len(publications)
        total_citations = sum(pub.citations for pub in publications)
        average_citations = total_citations / total_publications
        
        current_year = datetime.now().year
        recent_publications = sum(1 for pub in publications if pub.year >= current_year - 2)

        return {
            'total_publications': total_publications,
            'total_citations': total_citations,
            'average_citations': average_citations,
            'recent_publications': recent_publications
        }

    def generate_comparison_report(self, faculty_id: int) -> Dict:
        """Generate a comprehensive comparison report for a faculty member"""
        update_result = self.update_faculty_publications(faculty_id)
        
        if 'error' in update_result:
            return update_result

        faculty_data = get_faculty_publications(faculty_id)
        metrics = self.get_publication_metrics(faculty_data['publications'])

        return {
            'faculty_id': faculty_id,
            'name': faculty_data['faculty'].name,
            'department': faculty_data['faculty'].department,
            'metrics': metrics,
            'changes': update_result['changes'],
            'last_updated': update_result['last_updated']
        }
