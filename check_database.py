#!/usr/bin/env python3
"""
Database inspection script to check if publications are being stored
"""

from app import app, db, Faculty, Publication

def check_database():
    """Check what's actually stored in the database"""
    
    with app.app_context():
        print("DATABASE INSPECTION")
        print("=" * 50)
        
        # Check faculty records
        faculty_count = Faculty.query.count()
        print(f"Total Faculty Records: {faculty_count}")
        
        if faculty_count > 0:
            print("\nFaculty Records:")
            for faculty in Faculty.query.all():
                print(f"  - ID: {faculty.id}")
                print(f"    Name: {faculty.name}")
                print(f"    College: {faculty.college}")
                print(f"    Department: {faculty.department}")
                print(f"    Last Updated: {faculty.last_updated}")
                print()
        
        # Check publication records
        pub_count = Publication.query.count()
        print(f"Total Publication Records: {pub_count}")
        
        if pub_count > 0:
            print("\nPublication Records:")
            for pub in Publication.query.all():
                print(f"  - ID: {pub.id}")
                print(f"    Title: {pub.title}")
                print(f"    Authors: {pub.authors}")
                print(f"    Journal: {pub.journal}")
                print(f"    Year: {pub.year}")
                print(f"    Citations: {pub.citations}")
                print(f"    Faculty ID: {pub.faculty_id}")
                print()
        else:
            print("ERROR: No publications found in database!")
            print("This explains why the dashboard shows 0 results.")
        
        print("=" * 50)

if __name__ == "__main__":
    check_database()
