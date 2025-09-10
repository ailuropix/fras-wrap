#!/usr/bin/env python3
"""
Database Initialization Script
Recreates the database with the correct schema including college field
"""

from app import app, db, Faculty, Publication
from datetime import datetime
import os

def init_database():
    """Initialize the database with correct schema"""
    print("🗄️ Initializing database...")
    
    with app.app_context():
        # Remove existing database file if it exists
        db_path = 'instance/faculty_research.db'
        if os.path.exists(db_path):
            print("Removing existing database...")
            os.remove(db_path)
        
        # Create all tables with new schema
        print("Creating tables with new schema...")
        db.create_all()
        
        # Add sample faculty data
        sample_faculty = Faculty(
            name="Dr. Sample Faculty",
            college="Thakur College of Engineering and Technology",
            department="Computer Science",
            last_updated=datetime.utcnow()
        )
        
        db.session.add(sample_faculty)
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print(f"Sample faculty added: {sample_faculty.name}")

if __name__ == "__main__":
    init_database()
