from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///faculty_research.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    publications = db.relationship('Publication', backref='faculty', lazy=True)

class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.String(500))  # Added missing authors field
    journal = db.Column(db.String(200))
    year = db.Column(db.Integer)
    citations = db.Column(db.Integer, default=0)
    doi = db.Column(db.String(100))
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    is_disambiguated = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_faculty():
    from scrapers.publication_scraper import PublicationScraper
    
    data = request.json
    college = data.get('college')
    faculty_name = data.get('name')
    department = data.get('department')
    
    try:
        print(f"Processing search request for: {faculty_name}, {department}, {college}")
        
        # Check if faculty already exists
        faculty = Faculty.query.filter_by(name=faculty_name, college=college, department=department).first()
        
        if not faculty:
            # Create new faculty record
            faculty = Faculty(name=faculty_name, college=college, department=department)
            db.session.add(faculty)
            db.session.commit()
            print(f"Created new faculty record: {faculty.id}")
        else:
            print(f"Found existing faculty record: {faculty.id}")
        
        # Scrape publications with error handling
        publications = []
        try:
            scraper = PublicationScraper()
            publications = scraper.scrape_publications(faculty_name, department, college)
            print(f"Scraper returned {len(publications)} publications")
        except Exception as scrape_error:
            print(f"Scraping error: {scrape_error}")
            # Fallback: return a message about scraping failure but don't crash
            return jsonify({
                'status': 'partial_success',
                'message': f'Faculty record created for {faculty_name}, but publication scraping failed: {str(scrape_error)}',
                'faculty_id': faculty.id,
                'publications_found': 0
            })
        
        # Store publications in database
        publications_added = 0
        print(f"Starting to store {len(publications)} publications in database...")
        
        for i, pub in enumerate(publications):
            try:
                print(f"Processing publication {i+1}/{len(publications)}: {pub.get('title', 'No title')[:50]}...")
                
                # Check if publication already exists to avoid duplicates
                existing_pub = Publication.query.filter_by(
                    title=pub.get('title', ''),
                    faculty_id=faculty.id
                ).first()
                
                if existing_pub:
                    print(f"  - Publication already exists, skipping")
                    continue
                
                print(f"  - Creating new publication record")
                new_pub = Publication(
                    title=pub.get('title', ''),
                    authors=pub.get('authors', ''),
                    journal=pub.get('journal', ''),
                    year=pub.get('year', 0),
                    citations=pub.get('citations', 0),
                    doi=pub.get('doi', ''),
                    faculty_id=faculty.id
                )
                
                print(f"  - Adding to database session")
                db.session.add(new_pub)
                publications_added += 1
                print(f"  - Successfully queued publication {publications_added}")
                
            except Exception as pub_error:
                print(f"ERROR adding publication {i+1}: {pub_error}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"Attempting to commit {publications_added} publications to database...")
        try:
            db.session.commit()
            print(f"SUCCESS: Committed {publications_added} publications to database")
        except Exception as commit_error:
            print(f"ERROR during database commit: {commit_error}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise commit_error
        
        return jsonify({
            'status': 'success',
            'message': f'Found {len(publications)} publications for {faculty_name} ({publications_added} new)',
            'faculty_id': faculty.id,
            'faculty_name': faculty_name,
            'publications_found': len(publications),
            'publications_added': publications_added,
            'redirect_url': f'/faculty/{faculty.id}'
        })
        
    except Exception as e:
        print(f"Critical error in search_faculty: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'status': 'error', 
            'message': f'Search failed: {str(e)}'
        }), 500

@app.route('/dashboard')
def dashboard():
    """Dashboard route with server-side data rendering"""
    try:
        # Get all faculty and their publications
        faculty_list = Faculty.query.all()
        all_publications = Publication.query.all()
        
        # Calculate metrics
        total_publications = len(all_publications)
        total_citations = sum(pub.citations for pub in all_publications)
        
        # Get publication trends by year
        trends = {}
        for pub in all_publications:
            year = pub.year or 2023
            if year not in trends:
                trends[year] = {'count': 0, 'citations': 0}
            trends[year]['count'] += 1
            trends[year]['citations'] += pub.citations
        
        publication_trends = [{'year': year, 'count': data['count'], 'citations': data['citations']} 
                            for year, data in sorted(trends.items())]
        
        # Get top publications by citations
        top_publications = sorted(all_publications, key=lambda x: x.citations, reverse=True)[:5]
        
        # Get last updated time
        last_updated = faculty_list[0].last_updated if faculty_list else None
        
        dashboard_data = {
            'total_publications': total_publications,
            'total_citations': total_citations,
            'last_updated': last_updated,
            'top_publications': top_publications,
            'publication_trends': publication_trends
        }
        
        print(f"Dashboard data: {total_publications} publications, {total_citations} citations")
        return render_template('dashboard.html', data=dashboard_data)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Return empty data if there's an error
        dashboard_data = {
            'total_publications': 0,
            'total_citations': 0,
            'last_updated': None,
            'top_publications': [],
            'publication_trends': []
        }
        return render_template('dashboard.html', data=dashboard_data)

@app.route('/faculty/<int:faculty_id>')
def faculty_results(faculty_id):
    """Faculty-specific results page"""
    try:
        # Get specific faculty and their publications
        faculty = Faculty.query.get_or_404(faculty_id)
        faculty_publications = Publication.query.filter_by(faculty_id=faculty_id).all()
        
        # Calculate metrics for this faculty only
        total_publications = len(faculty_publications)
        total_citations = sum(pub.citations for pub in faculty_publications)
        
        # Get publication trends by year for this faculty
        trends = {}
        for pub in faculty_publications:
            year = pub.year or 2023
            if year not in trends:
                trends[year] = {'count': 0, 'citations': 0}
            trends[year]['count'] += 1
            trends[year]['citations'] += pub.citations
        
        publication_trends = [{'year': year, 'count': data['count'], 'citations': data['citations']} 
                            for year, data in sorted(trends.items())]
        
        # Get top publications by citations for this faculty
        top_publications = sorted(faculty_publications, key=lambda x: x.citations, reverse=True)[:5]
        
        faculty_data = {
            'faculty': faculty,
            'total_publications': total_publications,
            'total_citations': total_citations,
            'last_updated': faculty.last_updated,
            'top_publications': top_publications,
            'publication_trends': publication_trends
        }
        
        print(f"Faculty {faculty.name}: {total_publications} publications, {total_citations} citations")
        return render_template('faculty_results.html', data=faculty_data)
        
    except Exception as e:
        print(f"Faculty results error: {e}")
        return redirect(url_for('dashboard'))

@app.route('/api/dashboard')
def api_dashboard():
    from datetime import timedelta
    
    try:
        # Get all faculty and their publications
        faculty_list = Faculty.query.all()
        all_publications = Publication.query.all()
        
        # Calculate metrics
        total_publications = len(all_publications)
        total_citations = sum(pub.citations for pub in all_publications)
        
        # Get publication trends by year
        trends = {}
        for pub in all_publications:
            year = pub.year or 2023
            if year not in trends:
                trends[year] = {'count': 0, 'citations': 0}
            trends[year]['count'] += 1
            trends[year]['citations'] += pub.citations
        
        publication_trends = [{'year': year, 'count': data['count'], 'citations': data['citations']} 
                            for year, data in sorted(trends.items())]
        
        # Get top publications by citations
        top_publications = sorted(all_publications, key=lambda x: x.citations, reverse=True)[:5]
        top_pubs_data = [{
            'title': pub.title,
            'journal': pub.journal,
            'year': pub.year,
            'citations': pub.citations
        } for pub in top_publications]
        
        # Get last updated time
        last_updated = max([f.last_updated for f in faculty_list]) if faculty_list else datetime.utcnow()
        
        return jsonify({
            'totalPublications': total_publications,
            'totalCitations': total_citations,
            'publicationTrends': publication_trends,
            'topPublications': top_pubs_data,
            'lastUpdated': last_updated.isoformat(),
            'nextUpdate': (last_updated.replace(hour=2, minute=0, second=0) + 
                         timedelta(days=1)).isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        publication_trends = [{
            'year': pub.year,
            'count': pub.count,
            'citations': pub.citations
        } for pub in publications]

        top_pubs = [{
            'title': pub.title,
            'journal': pub.journal,
            'year': pub.year,
            'citations': pub.citations
        } for pub in top_publications]

        return jsonify({
            'totalPublications': total_publications,
            'totalCitations': total_citations,
            'lastUpdated': last_updated.isoformat(),
            'publicationTrends': publication_trends,
            'topPublications': top_pubs
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
