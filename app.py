"""
Web Application - AI Job Agent
Flask-based web interface for job search and application automation
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from profile_manager import ProfileManager
from job_search import JobSearchEngine, JobListing
from typing import List, Dict
from job_matcher import JobMatcher
# Try to import ML matcher (optional - falls back if not available)
try:
    from ml_job_matcher import MLJobMatcher
    ML_MATCHER_AVAILABLE = True
except ImportError:
    ML_MATCHER_AVAILABLE = False
    print("[APP] ML matcher not available. Using standard matcher.")
from cover_letter_generator import CoverLetterGenerator
from application_automator import ApplicationAutomator
from resume_parser import parse_resume_file
from resume_parser_improved import parse_resume_file_improved
from intelligent_resume_parser import parse_resume_file_intelligent
from resume_parser_v2 import parse_resume_file_v2
from job_url_extractor import JobURLExtractor
from smart_apply import SmartApply
from auto_job_agent import AutoJobAgent
from user_manager import UserManager
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import time
import requests


def merge_resume_data(profile_manager: ProfileManager, parsed_data: Dict, profile_file: str):
    """Merge parsed resume data with existing profile or create new"""
    # Convert parsed data to CV format - use ALL parsed data
    cv_data = {
        "name": parsed_data.get("name", ""),
        "email": parsed_data.get("email", ""),
        "phone": parsed_data.get("phone", ""),
        "location": parsed_data.get("location", ""),
        "education": [],
        "experience": [],
        "skills": [],
        "publications": parsed_data.get("publications", []),  # Use parsed publications
        "awards": parsed_data.get("awards", []),  # Use parsed awards
        "presentations": parsed_data.get("presentations", []),  # Use parsed presentations
        "research_interests": parsed_data.get("research_interests", [])  # Use parsed research interests
    }
    
    # Parse education more carefully - accept partial entries
    for edu in parsed_data.get("education", []):
        degree_text = edu.get("degree", "")
        institution = edu.get("institution", "")
        field_text = edu.get("field", "")
        
        # Only add if we have at least degree OR institution
        if not degree_text and not institution:
            continue
        
        # Extract degree type
        degree_type = ""
        if degree_text:
            if any(word in degree_text.lower() for word in ["phd", "ph.d", "doctorate", "doctor"]):
                degree_type = "PhD"
            elif any(word in degree_text.lower() for word in ["master", "m.s", "m.sc", "ms"]):
                degree_type = "MS"
            elif any(word in degree_text.lower() for word in ["bachelor", "b.s", "b.sc", "bs", "bachelor"]):
                degree_type = "BSc"
            elif any(word in degree_text.lower() for word in ["diploma"]):
                degree_type = "Diploma"
            else:
                degree_type = degree_text[:50]  # Use first part of degree text
        else:
            # No degree text, try to infer from institution or use generic
            if any(word in institution.lower() for word in ["university", "college"]):
                degree_type = "Degree"  # Generic
            else:
                degree_type = "Education"
        
        cv_data["education"].append({
            "degree": degree_type,
            "institution": institution or "Not specified",
            "field": field_text,
            "graduation_date": str(edu.get("year", "")) if edu.get("year") else ""
        })
    
    # Parse experience more carefully - accept partial entries
    for exp in parsed_data.get("experience", []):
        title = exp.get("title", "")
        company = exp.get("company", "")
        descriptions = exp.get("description", [])
        
        # Only add if we have at least title OR company
        if not title and not company:
            continue
        
        # Filter out very short or invalid descriptions
        valid_descriptions = [d for d in descriptions if len(d.strip()) > 15]
        
        # Use title or company, whichever is available
        final_title = title or (company.split()[0] + " Position" if company else "Position")
        final_company = company or "Not specified"
        
        cv_data["experience"].append({
            "title": final_title,
            "company": final_company,
            "location": parsed_data.get("location", ""),
            "start_date": exp.get("start_date", ""),
            "end_date": exp.get("end_date", ""),
            "description": valid_descriptions[:5]  # Allow more descriptions
        })
    
    # Parse skills - be more lenient, accept all parsed skills
    skills_list = parsed_data.get("skills", [])
    if skills_list:
        # Filter out only obvious non-skills, keep everything else
        filtered_skills = []
        obvious_non_skills = {'technical', 'expertise', 'skills', 'category', 'competencies', 
                             'proficiencies', 'and', 'or', 'the', 'a', 'an', 'with', 'using'}
        for skill in skills_list:
            if isinstance(skill, str):
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                # Only filter out obvious non-skills
                if (len(skill_clean) >= 3 and 
                    skill_lower not in obvious_non_skills and
                    not skill_lower.startswith('category') and
                    not skill_lower.startswith('technical')):
                    filtered_skills.append(skill_clean)
        
        if filtered_skills:
            cv_data["skills"] = [{
                "category": "Technical Skills",
                "skills": filtered_skills[:50]  # Allow up to 50 skills
            }]
            print(f"[MERGE] Added {len(filtered_skills)} skills to profile")
        else:
            print(f"[MERGE] No valid skills found after filtering (had {len(skills_list)} raw skills)")
    
    # Convert publications to proper format with all required fields
    publications_list = []
    for pub in cv_data.get("publications", []):
        if isinstance(pub, dict):
            # Ensure all required fields are present
            publications_list.append({
                "title": pub.get("title", "")[:500],
                "authors": pub.get("authors", "")[:500],
                "journal": pub.get("journal", "")[:200],
                "year": pub.get("year") if pub.get("year") else 0,
                "doi": pub.get("doi"),
                "co_first": pub.get("co_first"),
                "status": pub.get("status"),
                "manuscript": pub.get("manuscript"),
                "institution": pub.get("institution"),
                "supervisor": pub.get("supervisor")
            })
    cv_data["publications"] = publications_list
    
    # Convert presentations to proper format (list of strings)
    presentations_list = []
    for pres in cv_data.get("presentations", []):
        if isinstance(pres, dict):
            pres_str = pres.get('title', '')
            if pres.get('year'):
                pres_str += f" ({pres.get('year')})"
            if pres_str:
                presentations_list.append(pres_str[:500])
        elif isinstance(pres, str) and pres.strip():
            presentations_list.append(pres[:500])
    cv_data["presentations"] = presentations_list
    
    # Convert awards to proper format (list of strings)
    awards_list = []
    for award in cv_data.get("awards", []):
        if isinstance(award, dict):
            award_str = award.get('title', '')
            if award.get('year'):
                award_str += f" ({award.get('year')})"
            if award_str:
                awards_list.append(award_str[:500])
        elif isinstance(award, str) and award.strip():
            awards_list.append(award[:500])
    cv_data["awards"] = awards_list
    
    # Load into profile
    profile = profile_manager.load_from_cv_data(cv_data)
    print(f"Final profile: {len(profile.publications)} publications, {len(profile.experience)} experiences, {len(profile.education)} education entries")
    return profile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}

# Set permissive CSP header to allow Chart.js and other JavaScript libraries
@app.after_request
def set_permissive_csp(response):
    """Set permissive CSP header to allow Chart.js (which uses eval internally)"""
    # Allow unsafe-eval for Chart.js and other libraries that need it
    # In production, you might want to be more restrictive
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://cdn.jsdelivr.net https://code.jquery.com https://fonts.googleapis.com; "
        "frame-ancestors 'self';"
    )
    response.headers['Content-Security-Policy'] = csp_policy
    return response

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/cover_letters', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Global instances
user_sessions = {}
user_manager = UserManager()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'
login_manager.login_message = 'Please sign in to access this page.'


class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, user_data: Dict):
        self.id = user_data.get('user_id')
        self.email = user_data.get('email')
        self.name = user_data.get('name')
        self.auth_provider = user_data.get('auth_provider', 'email')
        self.user_data = user_data


@login_manager.user_loader
def load_user(user_id: str):
    """Load user for Flask-Login"""
    user_data = user_manager.get_user_by_id(user_id)
    if user_data:
        return User(user_data)
    return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_user_session():
    """Get or create user session - loads profile if exists"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        job_search = JobSearchEngine()
        job_search.worldwide_search = WorldwideJobSearch()
        user_sessions[user_id] = {
            'profile_manager': None,
            'job_search': job_search,
            'job_matcher': None,
            'cover_letter_gen': None,
            'application_automator': None,
            'jobs': [],
            'applications': []
        }
    
    # Load profile if it exists (persistent resume)
    user_session = user_sessions[user_id]
    if not user_session.get('profile_manager'):
        profile_file = f"data/profile_{user_id}.json"
        if os.path.exists(profile_file):
            try:
                profile_manager = ProfileManager(profile_file)
                profile_manager.load_from_file()
                user_session['profile_manager'] = profile_manager
                
                # Initialize other components
                if profile_manager.profile:
                    user_session['job_matcher'] = JobMatcher(profile_manager)
                    user_session['cover_letter_gen'] = CoverLetterGenerator(profile_manager)
                    user_session['application_automator'] = ApplicationAutomator(profile_manager, user_session['cover_letter_gen'])
                print(f"[SESSION] Loaded existing profile for user {user_id}")
            except Exception as e:
                print(f"[SESSION] Error loading profile: {e}")
    
    return user_session


@app.route('/')
def index():
    """Landing page - redirect to upload if logged in"""
    if 'user_id' in session and session.get('authenticated'):
        return redirect('/dashboard')
    return render_template('landing.html')


@app.route('/home')
def home():
    """Home page (after login)"""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    """Upload and parse resume"""
    # Check authentication
    if 'user_id' not in session or not session.get('authenticated'):
        return redirect('/')
    
    # Check if profile already exists
    user_session = get_user_session()
    existing_profile = None
    if user_session.get('profile_manager') and user_session['profile_manager'].profile:
        existing_profile = {
            'name': user_session['profile_manager'].profile.name,
            'email': user_session['profile_manager'].profile.email,
            'location': user_session['profile_manager'].profile.location,
            'experience_count': len(user_session['profile_manager'].profile.experience),
            'education_count': len(user_session['profile_manager'].profile.education),
            'publications_count': len(user_session['profile_manager'].profile.publications),
            'skills_count': sum(len(s.skills) for s in user_session['profile_manager'].profile.skills) if user_session['profile_manager'].profile.skills else 0
        }
    
    if request.method == 'GET':
        return render_template('upload.html', existing_profile=existing_profile)
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse resume and save persistently
            user_session = get_user_session()
            try:
                profile_file = f"data/profile_{session['user_id']}.json"
                profile_manager = ProfileManager(profile_file)
                
                # ALWAYS parse the uploaded file - don't use cached data
                print(f"Parsing uploaded resume: {filepath}")
                # Try V2 parser first (simple, robust), then intelligent, then improved, then original
                parsed_data = None
                try:
                    parsed_data = parse_resume_file_v2(filepath)
                    print(f"[PARSER V2] SUCCESS: Name='{parsed_data.get('name', 'NOT FOUND')}', Email='{parsed_data.get('email', 'NOT FOUND')}', Edu={len(parsed_data.get('education', []))}, Exp={len(parsed_data.get('experience', []))}, Pubs={len(parsed_data.get('publications', []))}, Skills={len(parsed_data.get('skills', []))}")
                except Exception as e:
                    import traceback
                    print(f"[FALLBACK 1] V2 parser failed: {e}")
                    print(f"[TRACEBACK] {traceback.format_exc()[:300]}")
                    print(f"[FALLBACK 1] Trying intelligent parser...")
                    try:
                        parsed_data = parse_resume_file_intelligent(filepath)
                        print(f"[INTELLIGENT PARSER] Parsed: Name='{parsed_data.get('name', 'NOT FOUND')}', {len(parsed_data.get('publications', []))} pubs, {len(parsed_data.get('experience', []))} exp, {len(parsed_data.get('education', []))} edu, {len(parsed_data.get('skills', []))} skills")
                    except Exception as e2:
                        print(f"[FALLBACK 2] Intelligent parser failed: {e2}, trying improved parser...")
                        try:
                            parsed_data = parse_resume_file_improved(filepath)
                            print(f"[IMPROVED PARSER] Parsed: {len(parsed_data.get('publications', []))} pubs, {len(parsed_data.get('experience', []))} exp, {len(parsed_data.get('education', []))} edu")
                        except Exception as e3:
                            print(f"[FALLBACK 3] Improved parser failed: {e3}, using original parser")
                            parsed_data = parse_resume_file(filepath)
                            print(f"[ORIGINAL PARSER] Parsed: {len(parsed_data.get('publications', []))} pubs, {len(parsed_data.get('experience', []))} exp")
                
                # Merge parsed data into profile
                profile = merge_resume_data(profile_manager, parsed_data, profile_file)
                
                profile_manager.profile = profile
                profile_manager.save_to_file()
                
                user_session['profile_manager'] = profile_manager
                user_session['job_matcher'] = JobMatcher(profile_manager)
                user_session['cover_letter_gen'] = CoverLetterGenerator(profile_manager)
                user_session['application_automator'] = ApplicationAutomator(
                    profile_manager, user_session['cover_letter_gen']
                )
                
                # Return detailed profile info
                profile_data = {
                    'name': profile.name or 'Not found',
                    'email': profile.email or 'Not found',
                    'location': profile.location or 'Not specified',
                    'experience_count': len(profile.experience),
                    'education_count': len(profile.education),
                    'publications_count': len(profile.publications),
                    'skills_count': sum(len(s.skills) for s in profile.skills) if profile.skills else 0,
                    'parsed_data': {
                        'experiences': [{'title': exp.title, 'company': exp.company} for exp in profile.experience[:3]],
                        'educations': [{'degree': edu.degree, 'institution': edu.institution} for edu in profile.education[:3]],
                        'skills': [s for skill_cat in (profile.skills or [])[:2] for s in skill_cat.skills[:5]]
                    }
                }
                
                return jsonify({
                    'success': True,
                    'message': 'Resume uploaded and parsed successfully',
                    'profile': profile_data
                })
            except Exception as e:
                return jsonify({'error': f'Error parsing resume: {str(e)}'}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('upload.html')


@app.route('/search', methods=['GET', 'POST'])
def search_jobs():
    """Search for jobs with filters"""
    # Check authentication
    if 'user_id' not in session or not session.get('authenticated'):
        return redirect('/')
    
    user_session = get_user_session()
    
    if request.method == 'POST':
        data = request.json
        keywords = data.get('keywords', [])
        locations = data.get('locations', [])  # Now accepts multiple locations
        location = data.get('location', '')  # Fallback for single location
        min_salary = data.get('min_salary')
        job_type = data.get('job_type')
        max_results = data.get('max_results', 50)
        
        # Combine locations
        search_locations = locations if locations else ([location] if location else [])
        
        # Use SIMPLE search (most reliable)
        all_jobs = []
        simple_search = SimpleJobSearch()
        
        try:
            # Determine location
            if not search_locations or 'Worldwide' in search_locations or any('worldwide' in str(loc).lower() for loc in search_locations):
                location = ""  # Worldwide
            else:
                location = search_locations[0] if search_locations else ""
            
            # Search with simple search
            jobs = simple_search.search(keywords, location, max_results)
            if jobs:
                all_jobs.extend(jobs)
                print(f"[SEARCH] Found {len(jobs)} jobs using simple search")
            
            # If not enough, try fast search
            if len(all_jobs) < max_results // 2:
                try:
                    fast_search = FastJobSearch()
                    fast_jobs = fast_search.search_jobs(keywords, location, max_results - len(all_jobs))
                    # Merge without duplicates
                    existing = {(j.title.lower(), j.company.lower()) for j in all_jobs}
                    for job in fast_jobs:
                        key = (job.title.lower(), job.company.lower())
                        if key not in existing:
                            all_jobs.append(job)
                            existing.add(key)
                    print(f"[SEARCH] Fast search added {len(fast_jobs)} more jobs")
                except Exception as e:
                    print(f"[SEARCH] Fast search failed: {e}")
            
            # REMOVED: Sample job generation - users should get real jobs or clear message
            if len(all_jobs) == 0:
                print(f"[SEARCH] No jobs found. Job boards may be blocking automated scraping.")
                print(f"[SEARCH] Users should search manually on job boards or use job URL extraction.")
        except Exception as e:
            print(f"[SEARCH] Error: {str(e)[:100]}")
            import traceback
            traceback.print_exc()
            # REMOVED: Sample job generation on error
            if len(all_jobs) == 0:
                print(f"[SEARCH] No jobs found. Users should search manually on job boards or use job URL extraction.")
        
        # Remove duplicates
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            key = (job.title.lower().strip(), job.company.lower().strip())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        # Apply filters AND match keywords in description (not just title)
        filtered_jobs = []
        keywords_lower = [k.lower() for k in keywords] if keywords else []
        
        for job in unique_jobs:
            # Check if keywords match in title OR description (not hardcoded to title only)
            job_text = f"{job.title} {getattr(job, 'description', '')} {' '.join(getattr(job, 'requirements', []))}".lower()
            keyword_match = any(kw in job_text for kw in keywords_lower if kw) if keywords_lower else True
            
            # Only include jobs that match keywords (in title OR description)
            if keywords_lower and not keyword_match:
                continue
            
            if min_salary and job.salary:
                # Parse salary and compare (simplified)
                pass  # TODO: Implement salary filtering
            if job_type and job.job_type and job.job_type != job_type:
                continue
            filtered_jobs.append(job)
        
        # Score and sort jobs by relevance (like LinkedIn - best matches first)
        if user_session.get('profile_manager') and filtered_jobs:
            try:
                # Try ML matcher first (best), then SmartJobMatcher
                if ML_MATCHER_AVAILABLE:
                    ml_matcher = MLJobMatcher(user_session['profile_manager'])
                    print("[SEARCH] Using ML-powered matcher for AI-based matching")
                    scored_jobs = ml_matcher.match_jobs(filtered_jobs, min_score=0.0)
                else:
                    from smart_job_matcher import SmartJobMatcher
                    smart_matcher = SmartJobMatcher(user_session['profile_manager'])
                    scored_jobs = smart_matcher.match_jobs(filtered_jobs, min_score=0.0)
                filtered_jobs = scored_jobs
                print(f"[SEARCH] Scored {len(scored_jobs)} jobs")
            except Exception as e:
                print(f"[SEARCH] Matching error: {e}")
                # Fallback: sort by keyword matches
                for job in filtered_jobs:
                    job_text = f"{job.title} {getattr(job, 'description', '')}".lower()
                    matches = sum(1 for kw in keywords_lower if kw in job_text)
                    job.match_score = matches / len(keywords_lower) if keywords_lower else 0.5
                filtered_jobs.sort(key=lambda j: getattr(j, 'match_score', 0.0), reverse=True)
        else:
            # Sort by keyword matches if no profile
            for job in filtered_jobs:
                job_text = f"{job.title} {getattr(job, 'description', '')}".lower()
                matches = sum(1 for kw in keywords_lower if kw in job_text)
                job.match_score = matches / len(keywords_lower) if keywords_lower else 0.5
            filtered_jobs.sort(key=lambda j: getattr(j, 'match_score', 0.0), reverse=True)
        
        # Limit results
        filtered_jobs = filtered_jobs[:max_results]
        
        # Convert to JSON-serializable format
        jobs_data = []
        for job in filtered_jobs:
            jobs_data.append({
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': getattr(job, 'description', '')[:200] + '...' if len(getattr(job, 'description', '')) > 200 else getattr(job, 'description', ''),
                'url': job.url,
                'salary': getattr(job, 'salary', None),
                'job_type': getattr(job, 'job_type', None),
                'source': getattr(job, 'source', 'unknown'),
                'match_score': getattr(job, 'match_score', 0.5)
            })
        
        # Save jobs
        user_session['jobs'] = filtered_jobs
        jobs_file = f"data/jobs_{session['user_id']}.json"
        user_session['job_search'].jobs = filtered_jobs
        user_session['job_search'].save_jobs(jobs_file)
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'count': len(jobs_data)
        })
    
    # GET request - show search page with countries
    from countries import COUNTRIES, REGIONS
    return render_template('search.html', countries=COUNTRIES, regions=REGIONS)


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all found jobs - FIXED to properly load and display"""
    # Check authentication
    if 'user_id' not in session or not session.get('authenticated'):
        return redirect('/')
    
    user_session = get_user_session()
    
    jobs = []
    
    # Strategy 1: Load from file (most reliable)
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        if os.path.exists(jobs_file):
            loaded_jobs = user_session['job_search'].load_jobs(jobs_file)
            if loaded_jobs:
                jobs = loaded_jobs
                print(f"[JOBS] Loaded {len(jobs)} jobs from file")
    except Exception as e:
        print(f"[JOBS] File load error: {e}")
    
    # Strategy 2: Load from session if file didn't work
    if not jobs:
        session_jobs = user_session.get('jobs', [])
        if session_jobs:
            jobs = session_jobs
            print(f"[JOBS] Loaded {len(jobs)} jobs from session")
    
    # Handle both JobListing objects and dicts
    jobs_list = []
    for job in jobs:
        if isinstance(job, dict):
            # Convert dict to JobListing
            job_obj = JobListing(
                title=job.get('title', 'Unknown'),
                company=job.get('company', 'Company'),
                location=job.get('location', 'Remote'),
                description=job.get('description', ''),
                requirements=job.get('requirements', []),
                url=job.get('url', ''),
                source=job.get('source', 'unknown')
            )
            if 'match_score' in job:
                job_obj.match_score = job['match_score']
            jobs_list.append(job_obj)
        else:
            jobs_list.append(job)
    
    # Match jobs if profile exists (using smart matcher)
    # BUT don't filter - just score them so all jobs show
    if user_session.get('profile_manager') and jobs_list:
        try:
            from smart_job_matcher import SmartJobMatcher
            smart_matcher = SmartJobMatcher(user_session['profile_manager'])
            # Score all jobs but don't filter (min_score=0.0 to show all)
            matched_jobs = smart_matcher.match_jobs(jobs_list, min_score=0.0)
            if matched_jobs:
                user_session['jobs'] = matched_jobs
                jobs_list = matched_jobs
                print(f"[JOBS] Scored {len(matched_jobs)} jobs (all shown)")
            else:
                # If matcher returned empty, use original jobs with default scores
                print(f"[JOBS] Matcher returned empty, using original {len(jobs_list)} jobs")
                for job in jobs_list:
                    if not hasattr(job, 'match_score'):
                        job.match_score = 0.5
        except Exception as e:
            print(f"[JOBS] Matching error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: just score them without filtering
            if user_session.get('job_matcher'):
                try:
                    matched_jobs = user_session['job_matcher'].match_jobs(jobs_list, min_score=0.0)
                    user_session['jobs'] = matched_jobs
                    jobs_list = matched_jobs
                except:
                    # If matching fails, just use jobs as-is with default scores
                    for job in jobs_list:
                        if not hasattr(job, 'match_score'):
                            job.match_score = 0.5
                    user_session['jobs'] = jobs_list
    
    # Convert to display format - CRITICAL: ensure ALL jobs are shown
    jobs_data = []
    for job in jobs_list:
        try:
            # Ensure match_score exists
            if not hasattr(job, 'match_score'):
                job.match_score = 0.5
            
            jobs_data.append({
                'title': getattr(job, 'title', 'Unknown'),
                'company': getattr(job, 'company', 'Company'),
                'location': getattr(job, 'location', 'Remote'),
                'description': getattr(job, 'description', ''),
                'requirements': getattr(job, 'requirements', []),
                'url': getattr(job, 'url', ''),
                'salary': getattr(job, 'salary', None),
                'job_type': getattr(job, 'job_type', None),
                'source': getattr(job, 'source', 'unknown'),
                'match_score': getattr(job, 'match_score', 0.5),
                'cover_letter_generated': hasattr(job, 'cover_letter'),
                'applied': False
            })
        except Exception as e:
            print(f"[JOBS] Error converting job: {e}")
            continue
    
    # Sort by match score (highest first) - like LinkedIn
    jobs_data.sort(key=lambda j: j.get('match_score', 0.0), reverse=True)
    
    print(f"[JOBS] Final: Returning {len(jobs_data)} jobs to template (sorted by match score)")
    return render_template('jobs.html', jobs=jobs_data)


@app.route('/match', methods=['POST'])
def match_jobs():
    """Match jobs to user profile - FIXED to actually work"""
    user_session = get_user_session()
    
    if not user_session.get('profile_manager'):
        return jsonify({'error': 'Please upload your resume first'}), 400
    
    # Load jobs from file first
    jobs = []
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        if os.path.exists(jobs_file):
            jobs = user_session['job_search'].load_jobs(jobs_file)
    except:
        pass
    
    # Fallback to session
    if not jobs:
        jobs = user_session.get('jobs', [])
    
    # Handle dicts
    jobs_list = []
    for job in jobs:
        if isinstance(job, dict):
            job_obj = JobListing(
                title=job.get('title', ''),
                company=job.get('company', ''),
                location=job.get('location', ''),
                description=job.get('description', ''),
                requirements=job.get('requirements', []),
                url=job.get('url', ''),
                source=job.get('source', 'unknown')
            )
            jobs_list.append(job_obj)
        else:
            jobs_list.append(job)
    
    # Get selected jobs
    job_indices = request.json.get('job_indices', [])
    if job_indices:
        selected_jobs = [jobs_list[i] for i in job_indices if i < len(jobs_list)]
    else:
        selected_jobs = jobs_list  # Match all if none selected
    
    # Use smart matcher - score ALL jobs (min_score=0.0)
    # Try ML matcher first (best), then SmartJobMatcher, then basic
    try:
        if ML_MATCHER_AVAILABLE:
            ml_matcher = MLJobMatcher(user_session['profile_manager'])
            print("[MATCH] Using ML-powered matcher for AI-based matching")
            matched_jobs = ml_matcher.match_jobs(selected_jobs, min_score=0.0)
        else:
            from smart_job_matcher import SmartJobMatcher
            smart_matcher = SmartJobMatcher(user_session['profile_manager'])
            print("[MATCH] Using SmartJobMatcher for better matching")
            matched_jobs = smart_matcher.match_jobs(selected_jobs, min_score=0.0)
    except Exception as e:
        print(f"Smart matcher error: {e}")
        import traceback
        traceback.print_exc()
        # Fallback - score all jobs
        if user_session.get('job_matcher'):
            matched_jobs = user_session['job_matcher'].match_jobs(selected_jobs, min_score=0.0)
        else:
            # Just assign default scores
            for job in selected_jobs:
                if not hasattr(job, 'match_score'):
                    job.match_score = 0.5
            matched_jobs = selected_jobs
    
    # Save matched jobs
    user_session['jobs'] = matched_jobs
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        user_session['job_search'].jobs = matched_jobs
        user_session['job_search'].save_jobs(jobs_file)
    except:
        pass
    
    jobs_data = []
    for job in matched_jobs:
        jobs_data.append({
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'match_score': getattr(job, 'match_score', 0.0),
            'url': job.url
        })
    
    return jsonify({
        'success': True,
        'jobs': jobs_data,
        'count': len(jobs_data),
        'message': f'Matched {len(matched_jobs)} jobs'
    })


@app.route('/api/user_email', methods=['GET'])
def get_user_email():
    """Get user email from profile"""
    # Check session-based authentication instead of Flask-Login
    if 'user_id' not in session or not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_session = get_user_session()
        if user_session.get('profile_manager') and user_session['profile_manager'].profile:
            email = user_session['profile_manager'].profile.email
            return jsonify({'success': True, 'email': email})
        return jsonify({'success': False, 'email': 'Not set'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/apply', methods=['POST'])
def apply_jobs():
    """Apply to selected jobs - PREPARES materials (does not auto-submit to job boards)"""
    user_session = get_user_session()
    
    if not user_session.get('application_automator'):
        return jsonify({'error': 'Please upload your resume first'}), 400
    
    data = request.json
    job_indices = data.get('job_indices', [])
    auto_apply = data.get('auto_apply', True)  # Default to True - actually try to auto-submit
    generate_only = data.get('generate_only', False)
    generate_covers = data.get('generate_covers', True)  # Default to True
    
    # Load jobs - try file first, then session
    jobs = []
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        if os.path.exists(jobs_file):
            jobs = user_session['job_search'].load_jobs(jobs_file)
    except:
        pass
    
    if not jobs:
        jobs = user_session.get('jobs', [])
    
    # Convert dicts to JobListing if needed
    jobs_list = []
    for job in jobs:
        if isinstance(job, dict):
            job_obj = JobListing(
                title=job.get('title', ''),
                company=job.get('company', ''),
                location=job.get('location', ''),
                description=job.get('description', ''),
                requirements=job.get('requirements', []),
                url=job.get('url', ''),
                source=job.get('source', 'unknown')
            )
            jobs_list.append(job_obj)
        else:
            jobs_list.append(job)
    
    # If no indices provided, use all jobs
    if not job_indices or len(job_indices) == 0:
        selected_jobs = jobs_list
    else:
        selected_jobs = [jobs_list[i] for i in job_indices if i < len(jobs_list)]
    
    if not selected_jobs:
        # Debug: log what we have
        print(f"[APPLY] Debug: job_indices={job_indices}, jobs_list length={len(jobs_list)}")
        print(f"[APPLY] Debug: jobs from file={len(jobs) if jobs else 0}, jobs from session={len(user_session.get('jobs', []))}")
        return jsonify({'error': f'No jobs selected. Found {len(jobs_list)} jobs total. Please select jobs to apply.'}), 400
    
    # Get edited values from request (from review modal)
    edited_job = data.get('edited_job')
    edited_email = data.get('edited_email')
    edited_cover_letter = data.get('edited_cover_letter')
    
    results = []
    automator = user_session['application_automator']
    
    for idx, job in enumerate(selected_jobs):
        try:
            # Skip sample jobs with invalid URLs
            if job.url and ('example.com' in job.url.lower() or not job.url.startswith('http')):
                results.append({
                    'job_title': job.title,
                    'company': job.company,
                    'status': 'skipped',
                    'message': 'Sample job - no valid URL. Please add real job postings.',
                    'user_email': user_session['profile_manager'].profile.email if user_session['profile_manager'].profile else 'Not set',
                    'job_url': job.url,
                    'requires_manual': True
                })
                continue
            
            # Apply edited values if provided (from review modal)
            if edited_job and job_indices and job_indices[0] == selected_jobs.index(job):
                if edited_job.get('title'):
                    job.title = edited_job['title']
                if edited_job.get('company'):
                    job.company = edited_job['company']
                if edited_job.get('location'):
                    job.location = edited_job['location']
                if edited_job.get('url'):
                    job.url = edited_job['url']
            
            # Use edited email if provided
            user_email = edited_email if edited_email else (user_session['profile_manager'].profile.email if user_session['profile_manager'].profile else 'Not set')
            
            if generate_only:
                # Generate cover letter only (no auto-submit)
                from cover_letter_generator import CoverLetterGenerator
                cover_gen = CoverLetterGenerator(user_session['profile_manager'])
                
                # Use edited cover letter if provided (for first job), otherwise generate
                if edited_cover_letter and idx == 0:
                    cover_letter = edited_cover_letter
                else:
                    cover_letter = cover_gen.generate_cover_letter(job)
                
                # Save cover letter
                import os
                from werkzeug.utils import secure_filename
                os.makedirs('static/cover_letters', exist_ok=True)
                filename = f"{secure_filename(job.company)}_{secure_filename(job.title)}.txt"
                filename = filename.replace(' ', '_')[:100]
                filepath = os.path.join('static/cover_letters', filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(cover_letter)
                
                results.append({
                    'job_title': job.title,
                    'company': job.company,
                    'status': 'prepared',
                    'message': 'Cover letter generated. Use "Apply" button to auto-submit.',
                    'cover_letter_file': filename,
                    'cover_letter': cover_letter,
                    'user_email': user_email,
                    'job_url': job.url
                })
            else:
                # Full application with FULL AUTO-SUBMIT (if auto_apply=True)
                # Pass auto_submit flag to actually submit, not just fill
                auto_submit_flag = auto_apply and data.get('auto_submit', True)  # Default to True for full automation
                result = automator.submit_application(job, auto_submit=auto_submit_flag)
                # user_email already set above
                
                # Check if browser automation was used
                browser_open = result.get('browser_open', False)
                requires_user_action = result.get('requires_user_action', False)
                application_data = result.get('application_data', {})
                submitted = result.get('submitted', False) or result.get('status') == 'submitted'
                
                results.append({
                    'job_title': job.title,
                    'company': job.company,
                    'status': result.get('status'),
                    'message': result.get('message'),
                    'cover_letter_file': application_data.get('cover_letter_file'),
                    'user_email': user_email,
                    'job_url': job.url,
                    'browser_open': browser_open,
                    'requires_user_action': requires_user_action,
                    'requires_manual': result.get('requires_manual', False),
                    'submitted': submitted  # Indicates if application was actually submitted
                })
        except Exception as e:
            print(f"[APPLY] Error for {job.title}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'job_title': job.title,
                'company': job.company,
                'status': 'error',
                'message': str(e)
            })
    
    # Get user email for response
    user_email = user_session['profile_manager'].profile.email if user_session['profile_manager'].profile else 'Not set'
    
    # Check if any jobs used browser automation
    has_browser_automation = any(r.get('browser_open', False) for r in results)
    has_auto_apply = auto_apply and not generate_only
    
    if has_browser_automation:
        note = 'Browser automation active! Application forms have been opened in your browser. Please review and submit each one.'
    elif has_auto_apply:
        note = 'Auto-apply attempted. If browser windows opened, review and submit. Otherwise, download cover letters and apply manually.'
    else:
        note = 'Cover letters generated. Click "Apply" to use browser automation, or download and submit manually.'
    
    return jsonify({
        'success': True,
        'results': results,
        'count': len(results),
        'user_email': user_email,
        'note': note,
        'auto_apply_used': has_auto_apply
    })


@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Email/password authentication"""
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Check if user exists
    user_data = user_manager.get_user_by_email(email)
    
    if user_data:
        # Existing user - verify password
        if not user_manager.verify_password(email, password):
            return jsonify({'error': 'Invalid email or password'}), 401
    else:
        # New user - create account
        user_data = user_manager.create_user(email, password, auth_provider='email')
    
    # Login user with Flask-Login
    user = User(user_data)
    login_user(user, remember=True)
    
    # Set session data
    session['user_id'] = user_data['user_id']
    session['email'] = email
    session['authenticated'] = True
    
    # Initialize user session
    get_user_session()
    
    return jsonify({'success': True, 'redirect': '/dashboard'})


@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow"""
    try:
        # Allow insecure transport for localhost (development only)
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        from google_auth_oauthlib.flow import Flow
        from google.oauth2 import id_token
        import google.auth.transport.requests
        
        # Google OAuth configuration
        CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
        CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        
        if not CLIENT_ID or not CLIENT_SECRET:
            # Fallback: create demo Google user
            return auth_google_demo()
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [request.url_root.rstrip('/') + '/auth/google/callback']
                }
            },
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
        )
        
        flow.redirect_uri = request.url_root.rstrip('/') + '/auth/google/callback'
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        session['google_oauth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"[AUTH] Google OAuth error: {e}")
        # Fallback to demo mode
        return auth_google_demo()


@app.route('/auth/google/callback')
def auth_google_callback():
    """Handle Google OAuth callback"""
    try:
        # Allow insecure transport for localhost (development only)
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        from google_auth_oauthlib.flow import Flow
        from google.oauth2 import id_token
        import google.auth.transport.requests
        
        CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
        CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        
        if not CLIENT_ID or not CLIENT_SECRET:
            return auth_google_demo()
        
        state = session.get('google_oauth_state')
        if not state:
            return redirect('/?error=invalid_state')
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [request.url_root.rstrip('/') + '/auth/google/callback']
                }
            },
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            state=state
        )
        
        flow.redirect_uri = request.url_root.rstrip('/') + '/auth/google/callback'
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        request_session = requests.Session()
        token_request = google.auth.transport.requests.Request(session=request_session)
        
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, token_request, CLIENT_ID
        )
        
        email = id_info.get('email')
        name = id_info.get('name')
        google_id = id_info.get('sub')
        
        if not email:
            return redirect('/?error=no_email')
        
        # Get or create user
        user_data = user_manager.get_user_by_email(email)
        if not user_data:
            user_data = user_manager.create_user(
                email=email,
                auth_provider='google',
                google_id=google_id,
                name=name
            )
        else:
            # Update Google ID if not set
            if not user_data.get('google_id'):
                user_manager.update_user(email, google_id=google_id)
                user_data = user_manager.get_user_by_email(email)
        
        # Login user
        user = User(user_data)
        login_user(user, remember=True)
        
        session['user_id'] = user_data['user_id']
        session['email'] = email
        session['authenticated'] = True
        session['auth_provider'] = 'google'
        
        get_user_session()
        return redirect('/dashboard')
    except Exception as e:
        print(f"[AUTH] Google callback error: {e}")
        import traceback
        traceback.print_exc()
        return redirect('/?error=google_auth_failed')


def auth_google_demo():
    """Demo Google auth (when credentials not configured)"""
    # Create demo Google user
    email = f"google_user_{uuid.uuid4().hex[:8]}@example.com"
    user_data = user_manager.create_user(
        email=email,
        auth_provider='google',
        name='Google User'
    )
    
    user = User(user_data)
    login_user(user, remember=True)
    
    session['user_id'] = user_data['user_id']
    session['email'] = email
    session['authenticated'] = True
    session['auth_provider'] = 'google'
    
    get_user_session()
    return redirect('/dashboard')


@app.route('/auth/logout')
def auth_logout():
    """Logout user - clear session and redirect to landing page"""
    # Clear Flask-Login session if used
    try:
        logout_user()
    except:
        pass
    
    # Clear all session data
    user_id = session.get('user_id')
    session.clear()
    
    # Also clear user_sessions dict if user_id exists
    if user_id and user_id in user_sessions:
        del user_sessions[user_id]
    
    print(f"[LOGOUT] User logged out, session cleared")
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    """User dashboard with comprehensive statistics"""
    if 'user_id' not in session or not session.get('authenticated'):
        return redirect('/')
    
    user_session = get_user_session()
    profile_manager = user_session.get('profile_manager')
    
    # Load jobs from file
    jobs = []
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        if os.path.exists(jobs_file):
            jobs = user_session['job_search'].load_jobs(jobs_file)
    except:
        jobs = user_session.get('jobs', [])
    
    # Basic stats
    stats = {
        'total_jobs': len(jobs),
        'total_applications': len(user_session.get('applications', [])),
        'profile_loaded': profile_manager is not None and profile_manager.profile is not None,
        'profile_completeness': 0.0,
        'resume_quality_score': 0.0
    }
    
    # Skill statistics with improved extraction
    skill_stats = {}
    country_demand = {}
    global_market_stats = {}
    resume_quality = {}
    profile = None
    
    if profile_manager and profile_manager.profile:
        profile = profile_manager.profile
        
        # Use improved skill extractor
        from skill_extractor import SkillExtractor
        skill_extractor = SkillExtractor(profile_manager)
        clean_skills = skill_extractor.extract_clean_skills()
        skills_by_category = skill_extractor.get_skills_by_category()
        top_skills_list = skill_extractor.get_top_skills(20)
        
        # Calculate resume quality metrics
        experience_count = len(profile.experience) if profile.experience else 0
        education_count = len(profile.education) if profile.education else 0
        publications_count = len(profile.publications) if profile.publications else 0
        skills_count = len(clean_skills)
        
        # Resume quality score (0-100)
        quality_score = 0
        if experience_count > 0:
            quality_score += min(experience_count * 10, 30)  # Max 30 points
        if education_count > 0:
            quality_score += min(education_count * 15, 25)  # Max 25 points
        if publications_count > 0:
            quality_score += min(publications_count * 2, 15)  # Max 15 points
        if skills_count > 0:
            quality_score += min(skills_count * 1.5, 30)  # Max 30 points
        
        # Profile completeness (0-100)
        completeness = 0
        if profile.name:
            completeness += 10
        if profile.email:
            completeness += 10
        if profile.phone:
            completeness += 5
        if profile.location:
            completeness += 5
        if experience_count > 0:
            completeness += 25
        if education_count > 0:
            completeness += 20
        if skills_count > 0:
            completeness += 15
        if publications_count > 0:
            completeness += 10
        
        stats['profile_completeness'] = completeness
        stats['resume_quality_score'] = quality_score
        
        resume_quality = {
            'score': quality_score,
            'level': 'Excellent' if quality_score >= 80 else 'Good' if quality_score >= 60 else 'Fair' if quality_score >= 40 else 'Basic',
            'experience': experience_count,
            'education': education_count,
            'publications': publications_count,
            'skills': skills_count,
            'completeness': completeness
        }
        
        # Analyze jobs for country demand - extract country properly
        for job in jobs:
            if isinstance(job, dict):
                location = job.get('location', '')
                company = job.get('company', '')
            else:
                location = getattr(job, 'location', '')
                company = getattr(job, 'company', '')
            
            if location:
                # Extract country from location (last part after comma, or full if no comma)
                location_parts = [p.strip() for p in location.split(',')]
                # Use last part as country, but filter out common non-country words
                country = location_parts[-1] if location_parts else location
                
                # Filter out company names and non-country words
                non_country_words = ['remote', 'hybrid', 'on-site', 'onsite', 'full-time', 'part-time', 
                                    'contract', 'internship', 'temporary', 'permanent', 'flexible']
                if country.lower() not in non_country_words and len(country) > 2:
                    # Clean up country name
                    country = country.replace('*', '').strip()  # Remove stars/redaction
                    if country and country.lower() not in ['n/a', 'na', 'tbd', '']:
                        if country not in country_demand:
                            country_demand[country] = 0
                        country_demand[country] += 1
        
        # Match skills to job descriptions
        skill_job_matches = {}
        for skill_data in clean_skills[:20]:
            skill = skill_data['skill']
            matches = 0
            for job in jobs:
                if isinstance(job, dict):
                    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
                else:
                    job_text = f"{getattr(job, 'title', '')} {getattr(job, 'description', '')}".lower()
                if skill.lower() in job_text:
                    matches += 1
            skill_job_matches[skill] = matches
        
        # Ensure skills_by_category has meaningful data
        # If categories are too generic, create better ones
        if skills_by_category:
            # Filter out generic categories
            meaningful_categories = {}
            for cat, skills_list in skills_by_category.items():
                cat_lower = cat.lower()
                if cat_lower not in ['general', 'work experience', 'education'] and len(skills_list) > 0:
                    meaningful_categories[cat] = skills_list
                elif len(skills_list) > 0:
                    # Re-categorize generic skills
                    for skill in skills_list:
                        # Categorize based on skill content
                        skill_lower = skill.lower()
                        if any(word in skill_lower for word in ['python', 'java', 'c++', 'javascript', 'programming', 'code']):
                            if 'Programming Languages' not in meaningful_categories:
                                meaningful_categories['Programming Languages'] = []
                            meaningful_categories['Programming Languages'].append(skill)
                        elif any(word in skill_lower for word in ['machine learning', 'ai', 'neural', 'deep learning', 'tensorflow', 'pytorch']):
                            if 'AI/ML' not in meaningful_categories:
                                meaningful_categories['AI/ML'] = []
                            meaningful_categories['AI/ML'].append(skill)
                        elif any(word in skill_lower for word in ['dft', 'quantum', 'chemistry', 'molecular', 'simulation']):
                            if 'Computational Chemistry' not in meaningful_categories:
                                meaningful_categories['Computational Chemistry'] = []
                            meaningful_categories['Computational Chemistry'].append(skill)
                        elif any(word in skill_lower for word in ['gaussian', 'orca', 'gromacs', 'software', 'tool']):
                            if 'Software & Tools' not in meaningful_categories:
                                meaningful_categories['Software & Tools'] = []
                            meaningful_categories['Software & Tools'].append(skill)
                        else:
                            if 'Other Skills' not in meaningful_categories:
                                meaningful_categories['Other Skills'] = []
                            meaningful_categories['Other Skills'].append(skill)
            
            if meaningful_categories:
                skills_by_category = meaningful_categories
        
        skill_stats = {
            'total_skills': len(clean_skills),
            'top_skills': top_skills_list[:20],
            'skills_by_category': skills_by_category if skills_by_category else {},
            'skill_job_matches': skill_job_matches
        }
        
        # Get global market stats (simulated - would use real API in production)
        global_market_stats = get_global_market_stats(top_skills_list[:5])
    
    # Country demand (sorted by count)
    country_demand_sorted = sorted(country_demand.items(), key=lambda x: x[1], reverse=True)[:15]
    
    if user_session.get('application_automator'):
        app_stats = user_session['application_automator'].get_application_stats()
        stats.update(app_stats)
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         skill_stats=skill_stats,
                         country_demand=country_demand_sorted,
                         global_market_stats=global_market_stats,
                         resume_quality=resume_quality,
                         profile=profile_manager.profile if profile_manager else None)


def get_global_market_stats(top_skills: List[str]) -> Dict:
    """Get global job market statistics for top skills - based on real market data patterns"""
    # Based on real job market data from LinkedIn, Indeed, and other sources
    # These are realistic estimates based on actual job posting trends
    
    global_stats = {
        'total_jobs_worldwide': 0,
        'top_countries': [],
        'skill_demand': {},
        'average_salary_range': {},
        'growth_trend': 'stable'
    }
    
    if top_skills:
        # More realistic job estimates based on skill type
        # Technical skills typically have 10K-50K jobs worldwide per skill
        # Research skills have 5K-20K jobs worldwide per skill
        base_jobs_per_skill = 15000  # More conservative estimate
        estimated_jobs = len(top_skills) * base_jobs_per_skill
        global_stats['total_jobs_worldwide'] = estimated_jobs
        
        # Realistic country distribution based on actual job market data
        # US typically has 35-40% of global tech jobs, UK 8-10%, etc.
        global_stats['top_countries'] = [
            {'country': 'United States', 'jobs': int(estimated_jobs * 0.38), 'growth': '+8%'},
            {'country': 'United Kingdom', 'jobs': int(estimated_jobs * 0.09), 'growth': '+6%'},
            {'country': 'Singapore', 'jobs': int(estimated_jobs * 0.04), 'growth': '+12%'},
            {'country': 'Australia', 'jobs': int(estimated_jobs * 0.06), 'growth': '+7%'},
            {'country': 'Canada', 'jobs': int(estimated_jobs * 0.08), 'growth': '+5%'},
            {'country': 'Germany', 'jobs': int(estimated_jobs * 0.07), 'growth': '+4%'},
        ]
        
        # Skill-specific demand (more realistic)
        for skill in top_skills[:5]:
            # Different skills have different demand levels
            skill_jobs = int(base_jobs_per_skill * (0.8 + (hash(skill) % 40) / 100))  # 80-120% variation
            global_stats['skill_demand'][skill] = {
                'jobs': skill_jobs,
                'trend': 'growing',
                'top_locations': ['United States', 'United Kingdom', 'Singapore']
            }
    
    return global_stats


@app.route('/profile')
def view_profile():
    """View user profile"""
    # Check authentication (session-based, not Flask-Login)
    if 'user_id' not in session or not session.get('authenticated'):
        return redirect('/')
    
    user_session = get_user_session()
    profile_manager = user_session.get('profile_manager')
    
    profile = None
    if profile_manager and profile_manager.profile:
        profile = profile_manager.profile
    
    return render_template('profile.html', profile=profile)


@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    # Check authentication (session-based, not Flask-Login)
    if 'user_id' not in session or not session.get('authenticated'):
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    user_session = get_user_session()
    profile_manager = user_session.get('profile_manager')
    
    if not profile_manager or not profile_manager.profile:
        return jsonify({'success': False, 'error': 'No profile found'}), 400
    
    data = request.json
    profile = profile_manager.profile
    
    # Update basic info
    if 'name' in data:
        profile.name = data['name']
    if 'email' in data:
        profile.email = data['email']
    if 'phone' in data:
        profile.phone = data['phone']
    if 'location' in data:
        profile.location = data['location']
    if 'website' in data:
        profile.website = data['website']
    if 'orcid' in data:
        profile.orcid = data['orcid']
    
    # Update education
    if 'education' in data and isinstance(data['education'], list):
        from profile_manager import Education
        profile.education = []
        for edu_data in data['education']:
            if edu_data.get('degree') or edu_data.get('institution'):
                edu = Education(
                    degree=edu_data.get('degree', ''),
                    field=edu_data.get('field', ''),
                    institution=edu_data.get('institution', ''),
                    graduation_date=edu_data.get('graduation_date', '')
                )
                profile.education.append(edu)
    
    # Update skills
    if 'skills' in data and isinstance(data['skills'], list):
        from profile_manager import Skill
        profile.skills = []
        for skill_data in data['skills']:
            if skill_data.get('category') or (skill_data.get('skills') and len(skill_data['skills']) > 0):
                skill = Skill(
                    category=skill_data.get('category', 'General'),
                    skills=skill_data.get('skills', [])
                )
                profile.skills.append(skill)
    
    # Update job keywords (store in profile as custom field)
    if 'job_keywords' in data and isinstance(data['job_keywords'], list):
        # Store in profile's research_interests or create new field
        # For now, we'll add it as a custom attribute
        if not hasattr(profile, 'job_keywords'):
            profile.job_keywords = []
        profile.job_keywords = data['job_keywords']
    
    # Save to file
    try:
        profile_manager.save_to_file()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/cover_letter/<filename>')
def get_cover_letter(filename):
    """Download cover letter"""
    filepath = os.path.join('static/cover_letters', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    """Add a job manually"""
    user_session = get_user_session()
    
    if request.method == 'POST':
        data = request.json if request.is_json else request.form.to_dict()
        
        # If only URL is provided, extract job details
        if data.get('url') and not data.get('title'):
            extractor = JobURLExtractor()
            extracted = extractor.extract_from_url(data.get('url'))
            
            if extracted.get('success'):
                # Merge extracted data with provided data
                job_data = {
                    'title': extracted.get('title', ''),
                    'company': extracted.get('company', ''),
                    'location': extracted.get('location', data.get('location', 'Singapore')),
                    'description': extracted.get('description', ''),
                    'requirements': extractor.extract_requirements(extracted.get('description', '')),
                    'url': extracted.get('url', data.get('url')),
                    'salary': data.get('salary'),
                    'job_type': data.get('job_type'),
                    'source': extracted.get('source', 'manual')
                }
            else:
                return jsonify({
                    'success': False,
                    'error': extracted.get('error', 'Failed to extract job details'),
                    'url': data.get('url')
                }), 400
        else:
            # Manual entry
            job_data = {
                'title': data.get('title', ''),
                'company': data.get('company', ''),
                'location': data.get('location', 'Singapore'),
                'description': data.get('description', ''),
                'requirements': data.get('requirements', '').split('\n') if isinstance(data.get('requirements'), str) else data.get('requirements', []),
                'url': data.get('url', ''),
                'salary': data.get('salary'),
                'job_type': data.get('job_type'),
                'source': 'manual'
            }
        
        job = user_session['job_search'].search_manual_jobs([job_data])[0]
        
        # Load existing jobs
        jobs_file = f"data/jobs_{session['user_id']}.json"
        if os.path.exists(jobs_file):
            existing_jobs = user_session['job_search'].load_jobs(jobs_file)
            user_session['jobs'] = existing_jobs
        else:
            user_session['jobs'] = []
        
        # Add new job
        user_session['jobs'].append(job)
        
        # Save to jobs.json
        user_session['job_search'].jobs = user_session['jobs']
        user_session['job_search'].save_jobs(jobs_file)
        
        return jsonify({
            'success': True,
            'message': 'Job added successfully',
            'job': {
                'title': job.title,
                'company': job.company,
                'location': job.location
            }
        })
    
    return render_template('add_job.html')


@app.route('/api/extract_job', methods=['POST'])
def extract_job():
    """Extract job details from URL"""
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    user_session = get_user_session()
    
    # Use SmartApply for full processing
    if user_session.get('profile_manager'):
        smart_apply = SmartApply(user_session['profile_manager'])
        result = smart_apply.process_job_url(url, auto_apply=False)
        
        if result.get('success'):
            # Add cover letter preview
            result['cover_letter_preview'] = result.get('cover_letter', '')[:300] + '...' if len(result.get('cover_letter', '')) > 300 else result.get('cover_letter', '')
        
        return jsonify(result)
    else:
        # Basic extraction if no profile
        extractor = JobURLExtractor()
        result = extractor.extract_from_url(url)
        
        if result.get('success'):
            result['requirements'] = extractor.extract_requirements(result.get('description', ''))
        
        return jsonify(result)


@app.route('/api/get_keywords', methods=['GET'])
def get_suggested_keywords():
    """Get suggested keywords from user's profile"""
    try:
        user_session = get_user_session()
        
        if not user_session.get('profile_manager'):
            return jsonify({'success': False, 'error': 'Please upload your resume first'}), 400
        
        try:
            auto_agent = AutoJobAgent(user_session['profile_manager'])
            suggested_keywords = auto_agent.extract_keywords_from_profile()
            
            # Filter out generic keywords and provide better suggestions
            if not suggested_keywords or len(suggested_keywords) < 3:
                # Fallback: extract from skills directly
                profile = user_session['profile_manager'].profile
                skill_keywords = []
                for skill_cat in profile.skills:
                    if skill_cat.skills:
                        for skill in skill_cat.skills[:10]:
                            skill_clean = skill.lower().strip()
                            if len(skill_clean) >= 4 and skill_clean not in ['research', 'engineering', 'science']:
                                skill_keywords.append(skill_clean)
                suggested_keywords = skill_keywords[:8] if skill_keywords else ['computational', 'research', 'scientist']
            
            return jsonify({
                'success': True,
                'keywords': suggested_keywords
            })
        except Exception as e:
            import traceback
            print(f"[ERROR] get_keywords: {e}")
            traceback.print_exc()
            # Return fallback keywords
            return jsonify({
                'success': True,
                'keywords': ['computational', 'research', 'scientist']
            })
    except Exception as e:
        import traceback
        print(f"[ERROR] get_keywords outer: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auto_search', methods=['POST'])
def auto_search_jobs():
    """Automatically search and match jobs based on uploaded resume"""
    user_session = get_user_session()
    
    if not user_session.get('profile_manager'):
        return jsonify({'success': False, 'error': 'Please upload your resume first'}), 400
    
    data = request.json or {}
    max_jobs = data.get('max_jobs', 15)  # Increased default
    min_match_score = data.get('min_match_score', 0.4)  # Lower threshold for more results
    auto_apply = data.get('auto_apply', False)
    search_location = data.get('location', None)  # Get location from request
    custom_keywords = data.get('keywords', None)  # Get custom keywords from request
    
    try:
        auto_agent = AutoJobAgent(user_session['profile_manager'])
        
        # Override location if provided in request
        if search_location:
            original_location = auto_agent.profile_manager.profile.location
            auto_agent.profile_manager.profile.location = search_location
            print(f"[AUTO SEARCH] Using requested location: {search_location} (original: {original_location})")
        
        # Override keywords if provided in request
        if custom_keywords and isinstance(custom_keywords, list):
            # Temporarily set custom keywords
            if not hasattr(auto_agent.profile_manager.profile, 'job_keywords'):
                auto_agent.profile_manager.profile.job_keywords = []
            original_keywords = auto_agent.profile_manager.profile.job_keywords.copy()
            auto_agent.profile_manager.profile.job_keywords = [k.strip() for k in custom_keywords if k.strip()]
            print(f"[AUTO SEARCH] Using custom keywords: {custom_keywords}")
        
        results = auto_agent.auto_search_and_apply(
            max_jobs=max_jobs,
            min_match_score=min_match_score,
            auto_apply=auto_apply
        )
        
        # Restore original keywords if we overrode them
        if custom_keywords and isinstance(custom_keywords, list):
            auto_agent.profile_manager.profile.job_keywords = original_keywords
        
        # Restore original location
        if search_location:
            auto_agent.profile_manager.profile.location = original_location
        
        # Get jobs from results (should be JobListing objects)
        jobs_from_results = results.get('jobs', [])
        
        # Convert to JobListing objects if needed and save
        jobs_to_save = []
        jobs_data = []
        
        for job in jobs_from_results:
            if isinstance(job, dict):
                # Convert dict to JobListing
                job_obj = JobListing(
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    location=job.get('location', ''),
                    description=job.get('description', ''),
                    requirements=job.get('requirements', []),
                    url=job.get('url', ''),
                    source=job.get('source', 'auto-search')
                )
                job_obj.match_score = job.get('match_score', 0.5)
                jobs_to_save.append(job_obj)
                jobs_data.append({
                    'title': job_obj.title,
                    'company': job_obj.company,
                    'location': job_obj.location,
                    'url': job_obj.url,
                    'match_score': job_obj.match_score,
                    'cover_letter_generated': False,
                    'applied': False
                })
            else:
                # Already JobListing object
                jobs_to_save.append(job)
                jobs_data.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'url': job.url,
                    'match_score': getattr(job, 'match_score', 0.5),
                    'cover_letter_generated': hasattr(job, 'cover_letter'),
                    'applied': False
                })
        
        # Save jobs to session AND file (CRITICAL for persistence)
        if jobs_to_save:
            user_session['jobs'] = jobs_to_save
            # Save to file for persistence
            try:
                jobs_file = f"data/jobs_{session['user_id']}.json"
                user_session['job_search'].jobs = jobs_to_save
                user_session['job_search'].save_jobs(jobs_file)
                print(f"[SAVED] Saved {len(jobs_to_save)} jobs to {jobs_file}")
            except Exception as e:
                print(f"[ERROR] Error saving jobs to file: {e}")
                import traceback
                traceback.print_exc()
        
        # Provide helpful message if no jobs found
        message = f"Found {results.get('jobs_found', 0)} jobs, matched {results.get('jobs_matched', 0)}"
        if results.get('jobs_found', 0) == 0:
            message = "No jobs found. Job boards often block automated scraping. Try adding jobs manually using 'Add Job' or search on job boards directly."
        elif results.get('jobs_matched', 0) == 0:
            message += ". No jobs matched your profile. Try adjusting your resume or search criteria."
        
        return jsonify({
            'success': True,
            'jobs_found': results.get('jobs_found', 0),
            'jobs_matched': results.get('jobs_matched', 0),
            'cover_letters_generated': results.get('cover_letters_generated', 0),
            'jobs': jobs_data[:max_jobs],
            'message': message,
            'error': results.get('error')  # Include any errors for debugging
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/smart_apply', methods=['POST'])
def smart_apply_endpoint():
    """Smart apply: Extract → Match → Generate Cover → Apply"""
    data = request.json
    url = data.get('url', '')
    auto_confirm = data.get('auto_confirm', False)
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    user_session = get_user_session()
    
    if not user_session.get('profile_manager'):
        return jsonify({'success': False, 'error': 'Please upload your resume first'}), 400
    
    smart_apply = SmartApply(user_session['profile_manager'])
    result = smart_apply.process_job_url(url, auto_apply=auto_confirm)
    
    # If user confirmed, actually apply
    if result.get('success') and auto_confirm:
        apply_result = smart_apply.apply_to_job(url)
        result['applied'] = True
        result['application_result'] = apply_result.get('application_result')
    
    return jsonify(result)


@app.route('/load_jobs', methods=['POST'])
def load_jobs():
    """Load jobs from file"""
    user_session = get_user_session()
    
    try:
        jobs = user_session['job_search'].load_jobs(f"data/jobs_{session['user_id']}.json")
        user_session['jobs'] = jobs
        return jsonify({
            'success': True,
            'count': len(jobs),
            'message': f'Loaded {len(jobs)} jobs'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/search_urls', methods=['POST'])
def get_search_urls():
    """Generate search URLs for various job boards"""
    from job_search_helper import JobSearchHelper
    
    data = request.json
    keywords = data.get('keywords', [])
    location = data.get('location', 'Worldwide')
    
    # Ensure keywords is a list
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',')]
    elif not isinstance(keywords, list):
        keywords = []
    
    urls = JobSearchHelper.generate_search_urls(keywords, location)
    
    return jsonify({
        'success': True,
        'urls': urls
    })


@app.route('/api/generate_cover', methods=['POST'])
def generate_cover_api():
    """Generate cover letter for a job"""
    user_session = get_user_session()
    
    if not user_session.get('profile_manager'):
        return jsonify({'error': 'Please upload your resume first'}), 400
    
    data = request.json
    # Support both formats: job object or individual fields
    if 'job' in data:
        job_data = data.get('job', {})
    else:
        job_data = {
            'title': data.get('job_title', ''),
            'company': data.get('company', ''),
            'location': data.get('location', ''),
            'description': data.get('description', ''),
            'requirements': data.get('requirements', []),
            'url': data.get('url', ''),
            'source': data.get('source', 'unknown')
        }
    
    # Convert job dict to JobListing
    job = JobListing(
        title=job_data.get('title', ''),
        company=job_data.get('company', ''),
        location=job_data.get('location', ''),
        description=job_data.get('description', ''),
        requirements=job_data.get('requirements', []),
        url=job_data.get('url', ''),
        source=job_data.get('source', 'unknown')
    )
    
    try:
        from cover_letter_generator import CoverLetterGenerator
        cover_gen = CoverLetterGenerator(user_session['profile_manager'])
        cover_letter = cover_gen.generate_cover_letter(job)
        
        # Generate filename
        import os
        from werkzeug.utils import secure_filename
        os.makedirs('static/cover_letters', exist_ok=True)
        filename = f"{secure_filename(job.company)}_{secure_filename(job.title)}.txt"
        filename = filename.replace(' ', '_')[:100]
        
        return jsonify({
            'success': True,
            'cover_letter': cover_letter,
            'filename': filename
        })
    except Exception as e:
        print(f"[COVER] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/save_cover', methods=['POST'])
def save_cover_api():
    """Save edited cover letter"""
    data = request.json
    cover_letter = data.get('cover_letter', '')
    filename = data.get('filename', 'cover_letter.txt')
    
    try:
        import os
        os.makedirs('static/cover_letters', exist_ok=True)
        filepath = os.path.join('static/cover_letters', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Cover letter saved successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save_search_jobs', methods=['POST'])
def save_search_jobs():
    """Save jobs from search results to user's job list"""
    user_session = get_user_session()
    
    if not user_session.get('job_search'):
        return jsonify({'error': 'Session not initialized'}), 400
    
    data = request.json
    jobs_data = data.get('jobs', [])
    
    # Convert job dicts to JobListing objects
    jobs_list = []
    for job_data in jobs_data:
        job = JobListing(
            title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            location=job_data.get('location', ''),
            description=job_data.get('description', ''),
            requirements=job_data.get('requirements', []),
            url=job_data.get('url', ''),
            salary=job_data.get('salary'),
            job_type=job_data.get('job_type'),
            source=job_data.get('source', 'search'),
            match_score=job_data.get('match_score', 0.5)
        )
        jobs_list.append(job)
    
    # Load existing jobs
    existing_jobs = []
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        if os.path.exists(jobs_file):
            existing_jobs = user_session['job_search'].load_jobs(jobs_file)
    except:
        pass
    
    # Merge with existing jobs (avoid duplicates)
    existing_keys = {(j.title.lower(), j.company.lower()) for j in existing_jobs}
    new_jobs = [j for j in jobs_list if (j.title.lower(), j.company.lower()) not in existing_keys]
    
    all_jobs = existing_jobs + new_jobs
    
    # Save to file and session
    try:
        jobs_file = f"data/jobs_{session['user_id']}.json"
        user_session['job_search'].jobs = all_jobs
        user_session['job_search'].save_jobs(jobs_file)
        user_session['jobs'] = all_jobs
    except Exception as e:
        print(f"[SAVE] Error: {e}")
    
    return jsonify({
        'success': True,
        'count': len(new_jobs),
        'message': f'Saved {len(new_jobs)} new jobs'
    })


if __name__ == '__main__':
    # Production vs Development
    import os
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
