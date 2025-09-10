#!/usr/bin/env python3
"""
Simple script to check publications in database and identify potential issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Faculty, Publication

def check_publications():
    """Check all publications in database"""
    
    with app.app_context():
        print("Checking all publications in database...")
        print("=" * 60)
        
        faculties = Faculty.query.all()
        
        for faculty in faculties:
            print(f"\nFaculty: {faculty.name}")
            print(f"Department: {faculty.department}")
            print(f"College: {faculty.college}")
            print(f"ID: {faculty.id}")
            
            publications = Publication.query.filter_by(faculty_id=faculty.id).all()
            print(f"Publications: {len(publications)}")
            
            if publications:
                print("\nTop 5 Publications:")
                for i, pub in enumerate(publications[:5], 1):
                    print(f"\n{i}. {pub.title}")
                    print(f"   Authors: {pub.authors}")
                    print(f"   Journal: {pub.journal}")
                    print(f"   Year: {pub.year}")
                    print(f"   Citations: {pub.citations}")
                    
                    # Check if faculty name is in authors
                    faculty_name_parts = faculty.name.lower().split()
                    authors_lower = pub.authors.lower()
                    
                    name_found = all(part in authors_lower for part in faculty_name_parts)
                    
                    if name_found:
                        print(f"   Status: CORRECT - Faculty name found in authors")
                    else:
                        print(f"   Status: POTENTIAL ISSUE - Faculty name not clearly found")
                        print(f"   WARNING: This publication may be incorrectly attributed!")
            
            print("-" * 40)

if __name__ == "__main__":
    check_publications()
