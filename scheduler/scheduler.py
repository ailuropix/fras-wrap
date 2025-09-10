from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
from app import app, db
from scraper.publication_scraper import PublicationScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scraper = PublicationScraper()

def update_faculty_publications():
    """Update publications for all faculty members"""
    try:
        with app.app_context():
            # Get all faculty members
            faculty_members = Faculty.query.all()
            
            for faculty in faculty_members:
                logger.info(f"Updating publications for {faculty.name} ({faculty.department})")
                
                # Scrape publications
                publications = scraper.search_publications(faculty.name)
                
                # Disambiguate and store publications
                disambiguated_pubs = scraper.disambiguate_publications(publications, faculty)
                
                # Update faculty last_updated timestamp
                faculty.last_updated = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Updated {len(disambiguated_pubs)} publications for {faculty.name}")
                
    except Exception as e:
        logger.error(f"Error updating faculty publications: {str(e)}")
        db.session.rollback()

def initialize_scheduler():
    """Initialize the scheduler with jobs"""
    try:
        # Add job to run every day at midnight
        scheduler.add_job(
            update_faculty_publications,
            'cron',
            hour=0,
            minute=0,
            id='update_faculty_data'
        )
        
        # Add job to run every 6 hours during working hours
        for hour in range(9, 18, 6):  # 9 AM, 3 PM
            scheduler.add_job(
                update_faculty_publications,
                'cron',
                hour=hour,
                minute=0,
                id=f'update_faculty_data_{hour}'
            )
        
        scheduler.start()
        logger.info("Scheduler initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing scheduler: {str(e)}")

# Initialize scheduler when module is imported
initialize_scheduler()
