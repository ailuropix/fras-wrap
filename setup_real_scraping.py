#!/usr/bin/env python3
"""
Automated Setup Script for Real Web Scraping
This script safely initializes the database and prepares the system for real publication scraping
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_flask_running():
    """Check if Flask is currently running on port 5000"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    return result == 0

def safe_db_init():
    """Safely initialize the database"""
    print("Setting up Faculty Research Analytics with Real Web Scraping...")
    
    # Check if Flask is running
    if check_flask_running():
        print("WARNING: Flask server is currently running on port 5000")
        print("   Please stop the Flask server (Ctrl+C) before running this script")
        print("   Then run this script again")
        return False
    
    # Import app components
    try:
        from app import app, db, Faculty, Publication
        from datetime import datetime
        
        print("Successfully imported Flask app components")
    except ImportError as e:
        print(f"ERROR: Error importing Flask components: {e}")
        return False
    
    # Initialize database
    try:
        with app.app_context():
            # Check if database exists
            db_path = Path('instance/faculty_research.db')
            if db_path.exists():
                print("Removing old database...")
                db_path.unlink()
            
            # Create new database with correct schema
            print("Creating new database with college field...")
            db.create_all()
            
            print("SUCCESS: Database initialized successfully!")
            print("Ready for real publication scraping from:")
            print("   - Google Scholar")
            print("   - CrossRef API")
            print("   - Advanced duplicate detection")
            print("   - Faculty name verification")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Error initializing database: {e}")
        return False

def start_flask():
    """Start the Flask application"""
    print("\nStarting Flask server with real web scraping...")
    print("   Server will be available at: http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop the server")
    
    try:
        # Start Flask app
        os.system("python app.py")
    except KeyboardInterrupt:
        print("\nFlask server stopped")

if __name__ == "__main__":
    print("=" * 60)
    print("Faculty Research Analytics - Real Web Scraping Setup")
    print("=" * 60)
    
    if safe_db_init():
        print("\n" + "=" * 60)
        print("SUCCESS: Setup Complete! Your system now features:")
        print("   - Real Google Scholar scraping")
        print("   - CrossRef API integration") 
        print("   - Legitimate publication data only")
        print("   - Advanced ambiguity resolution")
        print("   - College-specific search enhancement")
        print("=" * 60)
        
        # Ask user if they want to start Flask
        response = input("\nStart Flask server now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            start_flask()
        else:
            print("\nTo start the server later, run: python app.py")
            print("Then visit: http://127.0.0.1:5000")
    else:
        print("\nERROR: Setup failed. Please check the errors above.")
        sys.exit(1)
