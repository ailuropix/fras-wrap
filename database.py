from app import db, Faculty, Publication
from datetime import datetime

def init_db():
    """Initialize the database and create tables"""
    try:
        # Create tables
        db.create_all()
        print("Database tables created successfully")
        
        # Add sample data (optional)
        sample_faculty = Faculty(
            name="John Doe",
            department="Computer Science",
            last_updated=datetime.utcnow()
        )
        db.session.add(sample_faculty)
        db.session.commit()
        print("Sample data added successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.session.rollback()

def update_publications(faculty_id, publications):
    """Update publications for a specific faculty member"""
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            print(f"Faculty member with id {faculty_id} not found")
            return
            
        # Remove existing publications to avoid duplicates
        Publication.query.filter_by(faculty_id=faculty_id).delete()
        
        # Add new publications
        for pub in publications:
            new_pub = Publication(
                title=pub.get('title', ''),
                authors=pub.get('authors', ''),
                journal=pub.get('journal', ''),
                year=pub.get('year', 0),
                citations=pub.get('citations', 0),
                doi=pub.get('doi', ''),
                faculty_id=faculty_id
            )
            db.session.add(new_pub)
            
        faculty.last_updated = datetime.utcnow()
        db.session.commit()
        print(f"Successfully updated {len(publications)} publications for {faculty.name}")
        
    except Exception as e:
        print(f"Error updating publications: {e}")
        db.session.rollback()

def get_faculty_publications(faculty_id):
    """Get all publications for a specific faculty member"""
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return None
            
        publications = Publication.query.filter_by(faculty_id=faculty_id).all()
        return {
            'faculty': faculty,
            'publications': publications
        }
    except Exception as e:
        print(f"Error getting publications: {e}")
        return None
