#!/usr/bin/env python3
"""
Debug script to test the publication scraper and name matching logic
"""

from scrapers.publication_scraper import PublicationScraper
import json

def debug_scraper():
    """Debug the scraper to see what's happening with name matching"""
    
    scraper = PublicationScraper()
    faculty_name = "Anand Khandare"
    department = "Artificial Intelligence and Data Science"
    college = "Thakur College of Engineering and Technology"
    
    print(f"DEBUG: Debugging scraper for: {faculty_name}")
    print("=" * 60)
    
    # Test CrossRef API directly
    print("\nTesting CrossRef API...")
    try:
        crossref_pubs = scraper.search_crossref(faculty_name)
        print(f"CrossRef returned {len(crossref_pubs)} publications")
        
        if crossref_pubs:
            print("\nSample CrossRef publications:")
            for i, pub in enumerate(crossref_pubs[:3]):  # Show first 3
                print(f"\n{i+1}. Title: {pub.get('title', 'N/A')}")
                print(f"   Authors: {pub.get('authors', 'N/A')}")
                print(f"   Journal: {pub.get('journal', 'N/A')}")
                print(f"   Year: {pub.get('year', 'N/A')}")
                print(f"   Citations: {pub.get('citations', 'N/A')}")
        else:
            print("ERROR: No publications found from CrossRef")
            
    except Exception as e:
        print(f"ERROR: CrossRef error: {e}")
    
    # Test Google Scholar
    print("\nTesting Google Scholar...")
    try:
        gs_pubs = scraper.search_google_scholar(faculty_name, department, college)
        print(f"Google Scholar returned {len(gs_pubs)} publications")
        
        if gs_pubs:
            print("\nSample Google Scholar publications:")
            for i, pub in enumerate(gs_pubs[:3]):  # Show first 3
                print(f"\n{i+1}. Title: {pub.get('title', 'N/A')}")
                print(f"   Authors: {pub.get('authors', 'N/A')}")
                print(f"   Journal: {pub.get('journal', 'N/A')}")
                print(f"   Year: {pub.get('year', 'N/A')}")
                print(f"   Citations: {pub.get('citations', 'N/A')}")
        else:
            print("ERROR: No publications found from Google Scholar")
            
    except Exception as e:
        print(f"ERROR: Google Scholar error: {e}")
    
    # Test full scraper
    print("\nTesting full scraper...")
    try:
        all_pubs = scraper.scrape_publications(faculty_name, department, college)
        print(f"Full scraper returned {len(all_pubs)} publications after deduplication")
        
        if all_pubs:
            print("\nFinal publications:")
            for i, pub in enumerate(all_pubs):
                print(f"\n{i+1}. Title: {pub.get('title', 'N/A')}")
                print(f"   Authors: {pub.get('authors', 'N/A')}")
                print(f"   Source: {pub.get('source', 'N/A')}")
        else:
            print("ERROR: No publications found after processing")
            
    except Exception as e:
        print(f"ERROR: Full scraper error: {e}")
    
    print("\n" + "=" * 60)
    print("DEBUG: Debug complete!")

if __name__ == "__main__":
    debug_scraper()
