"""
Application Automator - Handles job application submission
"""
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from job_search import JobListing
from cover_letter_generator import CoverLetterGenerator
from profile_manager import ProfileManager
import os


class ApplicationAutomator:
    """Automates job application process"""
    
    def __init__(self, profile: ProfileManager, cover_letter_gen: CoverLetterGenerator):
        self.profile = profile
        self.cover_letter_gen = cover_letter_gen
        self.applications_log = "applications_log.json"
        self.applications = self.load_applications()
    
    def load_applications(self) -> List[Dict]:
        """Load application history"""
        try:
            with open(self.applications_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_applications(self):
        """Save application history"""
        with open(self.applications_log, 'w', encoding='utf-8') as f:
            json.dump(self.applications, f, indent=2, ensure_ascii=False)
    
    def has_applied(self, job: JobListing) -> bool:
        """Check if already applied to this job"""
        for app in self.applications:
            if (app.get("title", "").lower() == job.title.lower() and
                app.get("company", "").lower() == job.company.lower()):
                return True
        return False
    
    def prepare_application_materials(self, job: JobListing) -> Dict:
        """Prepare all materials needed for application"""
        if not self.profile.profile:
            raise ValueError("Profile not loaded")
        
        profile = self.profile.profile
        
        # Generate cover letter
        cover_letter = self.cover_letter_gen.generate_cover_letter(job)
        cover_letter = self.cover_letter_gen.add_personal_touches(cover_letter, job)
        
        # Save cover letter
        cover_letter_file = self.cover_letter_gen.save_cover_letter(cover_letter, job)
        
        # Prepare application data
        application_data = {
            "job_title": job.title,
            "company": job.company,
            "location": job.location,
            "job_url": job.url,
            "cover_letter": cover_letter,
            "cover_letter_file": cover_letter_file,
            "applicant_name": profile.name,
            "applicant_email": profile.email,
            "applicant_phone": profile.phone,
            "resume_file": "resume.pdf",  # User should provide this
            "applied_date": datetime.now().isoformat(),
            "status": "prepared"
        }
        
        return application_data
    
    def submit_application(self, job: JobListing, auto_submit: bool = False) -> Dict:
        """
        Submit application for a job
        auto_submit: If True, attempts to auto-submit (requires API access)
                     If False, prepares materials for manual submission
        """
        if self.has_applied(job):
            return {
                "status": "already_applied",
                "message": f"Already applied to {job.title} at {job.company}"
            }
        
        # Prepare application materials
        application_data = self.prepare_application_materials(job)
        
        if auto_submit:
            # Attempt automatic submission
            result = self._auto_submit(job, application_data)
        else:
            # Prepare for manual submission
            result = {
                "status": "prepared",
                "message": "Application materials prepared. Please submit manually.",
                "application_data": application_data
            }
        
        # Log application
        application_record = {
            "job_title": job.title,
            "company": job.company,
            "job_url": job.url,
            "applied_date": datetime.now().isoformat(),
            "status": result.get("status", "prepared"),
            "cover_letter_file": application_data.get("cover_letter_file"),
            "match_score": job.match_score
        }
        
        self.applications.append(application_record)
        self.save_applications()
        
        return result
    
    def _auto_submit(self, job: JobListing, application_data: Dict) -> Dict:
        """
        Actually submit application using browser automation
        Navigates to job site, handles login/account creation, fills forms
        """
        try:
            from auto_apply_engine import AutoApplyEngine
            
            # Initialize auto-apply engine (headless=False to show browser)
            auto_engine = AutoApplyEngine(self.profile, headless=False)
            
            # Get resume path (use uploaded resume if available)
            resume_path = application_data.get('resume_file')
            if resume_path and not os.path.isabs(resume_path):
                # Try to find in uploads folder
                uploads_path = os.path.join('uploads', resume_path)
                if os.path.exists(uploads_path):
                    resume_path = uploads_path
                else:
                    # Try to find any PDF in uploads folder
                    uploads_dir = 'uploads'
                    if os.path.exists(uploads_dir):
                        for file in os.listdir(uploads_dir):
                            if file.lower().endswith(('.pdf', '.doc', '.docx')):
                                resume_path = os.path.join(uploads_dir, file)
                                break
                    if not resume_path or not os.path.exists(resume_path):
                        resume_path = None
            
            print(f"[AUTO-SUBMIT] Applying to {job.title} at {job.company}")
            print(f"[AUTO-SUBMIT] URL: {job.url}")
            print(f"[AUTO-SUBMIT] Resume: {resume_path if resume_path else 'Not found'}")
            
            # Actually apply - this will navigate to job site and fill form
            result = auto_engine.apply_to_job(
                job=job,
                cover_letter=application_data.get('cover_letter', ''),
                resume_path=resume_path
            )
            
            if result.get('success'):
                if result.get('status') == 'ready_for_review':
                    return {
                        "status": "filled_ready_for_submit",
                        "message": result.get('message', 'Application form filled. Please review in browser and click submit.'),
                        "application_data": application_data,
                        "browser_open": True,
                        "requires_user_action": True
                    }
                elif result.get('status') == 'partially_filled':
                    return {
                        "status": "partially_filled",
                        "message": result.get('message', 'Some fields filled. Please complete manually.'),
                        "application_data": application_data,
                        "browser_open": True,
                        "requires_user_action": True
                    }
                else:
                    return {
                        "status": "submitted",
                        "message": "Application submitted successfully!",
                        "application_data": application_data
                    }
            else:
                return {
                    "status": "automation_failed",
                    "message": result.get('message', 'Browser automation failed. Please submit manually.'),
                    "application_data": application_data,
                    "requires_manual": True
                }
                
        except ImportError:
            return {
                "status": "selenium_not_available",
                "message": "Selenium not installed. Install: pip install selenium webdriver-manager",
                "application_data": application_data,
                "requires_manual": True
            }
        except Exception as e:
            print(f"[ERROR] Auto-submit failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Auto-submission error: {str(e)}. Please submit manually.",
                "application_data": application_data,
                "requires_manual": True
            }
    
    def batch_prepare_applications(self, jobs: List[JobListing], 
                                  min_match_score: float = 0.5) -> List[Dict]:
        """Prepare applications for multiple jobs"""
        prepared = []
        
        for job in jobs:
            if job.match_score and job.match_score >= min_match_score:
                if not self.has_applied(job):
                    try:
                        result = self.submit_application(job, auto_submit=False)
                        prepared.append(result)
                        print(f"[OK] Prepared application for {job.title} at {job.company}")
                        time.sleep(1)  # Rate limiting
                    except Exception as e:
                        print(f"[ERROR] Error preparing application for {job.title}: {e}")
        
        return prepared
    
    def get_application_stats(self) -> Dict:
        """Get statistics about applications"""
        if not self.applications:
            return {
                "total_applications": 0,
                "by_status": {},
                "by_month": {}
            }
        
        stats = {
            "total_applications": len(self.applications),
            "by_status": {},
            "by_month": {},
            "average_match_score": 0.0
        }
        
        scores = []
        for app in self.applications:
            # Count by status
            status = app.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by month
            applied_date = app.get("applied_date", "")
            if applied_date:
                month = applied_date[:7]  # YYYY-MM
                stats["by_month"][month] = stats["by_month"].get(month, 0) + 1
            
            # Collect match scores
            if app.get("match_score"):
                scores.append(app["match_score"])
        
        if scores:
            stats["average_match_score"] = sum(scores) / len(scores)
        
        return stats
