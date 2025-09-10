#!/usr/bin/env python3
"""
Debug script to test name matching accuracy in publication scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.publication_scraper import PublicationScraper

def test_name_matching():
    """Test name matching with different faculty names"""
    
    scraper = PublicationScraper()
    
    # Test cases
    test_cases = [
        {
            'name': 'Prachi Janrao',
            'department': 'Computer Science',
            'college': 'Thakur College of Engineering and Technology'
        },
        {
            'name': 'Anand Khandare', 
            'department': 'Computer Science',
            'college': 'Thakur College of Engineering and Technology'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print(f"Department: {test_case['department']}")
        print(f"College: {test_case['college']}")
        print(f"{'='*60}")
        
        try:
            publications = scraper.scrape_publications(
                test_case['name'], 
                test_case['department'], 
                test_case['college']
            )
            
            print(f"\nFound {len(publications)} publications:")
            
            for i, pub in enumerate(publications, 1):
                print(f"\n{i}. Title: {pub.get('title', 'No title')}")
                print(f"   Authors: {pub.get('authors', 'No authors')}")
                print(f"   Journal: {pub.get('journal', 'No journal')}")
                print(f"   Year: {pub.get('year', 'No year')}")
                print(f"   Citations: {pub.get('citations', 0)}")
                print(f"   Source: {pub.get('source', 'Unknown')}")
                
                # Check if the faculty name is actually in the authors
                authors = pub.get('authors', '')
                faculty_name = test_case['name']
                
                print(f"   Name Match Check:")
                print(f"   - Looking for: '{faculty_name}'")
                print(f"   - In authors: '{authors}'")
                
                # Test the improved matching logic
                faculty_parts = faculty_name.lower().split()
                authors_list = [a.strip() for a in authors.split(',')]
                
                name_match = False
                matched_author = None
                
                for author in authors_list:
                    author_lower = author.lower()
                    if all(part in author_lower for part in faculty_parts):
                        author_parts = author_lower.split()
                        if any(faculty_part in author_parts for faculty_part in faculty_parts):
                            name_match = True
                            matched_author = author
                            break
                
                if name_match:
                    print(f"   ✅ MATCH: Found in author '{matched_author}'")
                else:
                    print(f"   ❌ NO MATCH: Faculty name not found in authors")
                    print(f"   ⚠️  This publication may be incorrectly attributed!")
                
        except Exception as e:
            print(f"Error testing {test_case['name']}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Testing Publication Name Matching Accuracy")
    print("This script will help identify incorrectly attributed publications")
    test_name_matching()
