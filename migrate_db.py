#!/usr/bin/env python3
"""
Database Migration Script
Adds college field to Faculty table and recreates database with new schema
"""

import os
import sqlite3
from app import app, db, Faculty, Publication

def backup_existing_data():
    """Backup existing data before migration"""
    try:
        # Check if database file exists
        db_path = 'instance/faculty_research.db'
        if not os.path.exists(db_path):
            print("No existing database found. Creating new database...")
            return [], []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Backup faculty data
        faculty_data = []
        try:
            cursor.execute("SELECT id, name, department, last_updated FROM faculty")
            faculty_data = cursor.fetchall()
            print(f"Backed up {len(faculty_data)} faculty records")
        except sqlite3.OperationalError as e:
            print(f"Faculty table doesn't exist or has different schema: {e}")
        
        # Backup publication data
        publication_data = []
        try:
            cursor.execute("SELECT id, title, authors, journal, year, citations, doi, faculty_id FROM publication")
            publication_data = cursor.fetchall()
            print(f"Backed up {len(publication_data)} publication records")
        except sqlite3.OperationalError as e:
            print(f"Publication table doesn't exist or has different schema: {e}")
        
        conn.close()
        return faculty_data, publication_data
        
    except Exception as e:
        print(f"Error backing up data: {e}")
        return [], []

def migrate_database():
    """Perform the database migration"""
    print("Starting database migration...")
    
    # Backup existing data
    faculty_backup, publication_backup = backup_existing_data()
    
    # Create application context
    with app.app_context():
        # Drop all tables and recreate with new schema
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables with updated schema...")
        db.create_all()
        
        # Restore faculty data with default college
        if faculty_backup:
            print("Restoring faculty data...")
            for faculty_row in faculty_backup:
                faculty = Faculty(
                    name=faculty_row[1],
                    college="Thakur College of Engineering and Technology",  # Default college
                    department=faculty_row[2],
                    last_updated=faculty_row[3]
                )
                db.session.add(faculty)
            
            db.session.commit()
            print(f"Restored {len(faculty_backup)} faculty records with default college")
        
        # Restore publication data
        if publication_backup:
            print("Restoring publication data...")
            for pub_row in publication_backup:
                publication = Publication(
                    title=pub_row[1],
                    authors=pub_row[2],
                    journal=pub_row[3],
                    year=pub_row[4],
                    citations=pub_row[5],
                    doi=pub_row[6],
                    faculty_id=pub_row[7]
                )
                db.session.add(publication)
            
            db.session.commit()
            print(f"Restored {len(publication_backup)} publication records")
        
        print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
