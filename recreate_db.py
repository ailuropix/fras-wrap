#!/usr/bin/env python3
"""
Simple database recreation script without Unicode issues
"""

from app import app, db, Faculty, Publication
import os

def recreate_database():
    """Recreate database with correct schema including authors field"""
    
    with app.app_context():
        print("Recreating database with correct schema...")
        
        # Remove existing database file if it exists
        db_path = 'instance/faculty_research.db'
        if os.path.exists(db_path):
            print("Removing old database...")
            os.remove(db_path)
        
        # Create all tables with new schema (including authors field)
        print("Creating tables with authors field...")
        db.create_all()
        
        print("SUCCESS: Database recreated with correct schema!")
        print("The Publication model now includes the authors field.")

if __name__ == "__main__":
    recreate_database()
