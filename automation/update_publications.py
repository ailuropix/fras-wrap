import schedule
import time
from datetime import datetime
from app import Faculty
from core.comparison import PublicationComparator
from database import update_publications
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_log.log'),
        logging.StreamHandler()
    ]
)

comparator = PublicationComparator()

def update_all_faculty():
    """Update publications for all faculty members"""
    try:
        logging.info("Starting update process for all faculty members")
        
        # Get all faculty members
        faculty_list = Faculty.query.all()
        
        if not faculty_list:
            logging.warning("No faculty members found in database")
            return
            
        for faculty in faculty_list:
            logging.info(f"Updating publications for {faculty.name}")
            
            # Get comparison report
            report = comparator.generate_comparison_report(faculty.id)
            
            if 'error' in report:
                logging.error(f"Error updating {faculty.name}: {report['error']}")
                continue
                
            # Update publications in database
            update_publications(faculty.id, report['changes']['added'])
            
            # Log changes
            if report['changes']['added']:
                logging.info(f"Added {len(report['changes']['added'])} new publications for {faculty.name}")
            if report['changes']['updated']:
                logging.info(f"Updated {len(report['changes']['updated'])} publications for {faculty.name}")
            if report['changes']['removed']:
                logging.info(f"Removed {len(report['changes']['removed'])} publications for {faculty.name}")
                
        logging.info("Update process completed successfully")
        
    except Exception as e:
        logging.error(f"Error in update process: {str(e)}")

def main():
    # Schedule the update to run every day at 2 AM
    schedule.every().day.at("02:00").do(update_all_faculty)
    
    logging.info("Update scheduler started")
    
    # Run initial update
    update_all_faculty()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    main()
