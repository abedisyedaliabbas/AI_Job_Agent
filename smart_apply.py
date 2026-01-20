"""
Smart Apply - Automated job application workflow
Extracts job from URL → Matches → Generates cover → Asks user → Applies
"""
from job_url_extractor import JobURLExtractor
from job_search import JobListing
from typing import Dict, Optional
from profile_manager import ProfileManager
from job_matcher import JobMatcher
from cover_letter_generator import CoverLetterGenerator
from application_automator import ApplicationAutomator


class SmartApply:
    """Smart automated application system"""
    
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
        self.extractor = JobURLExtractor()
        self.job_matcher = JobMatcher(profile_manager) if profile_manager.profile else None
        self.cover_letter_gen = CoverLetterGenerator(profile_manager) if profile_manager.profile else None
        self.application_automator = None
        if profile_manager.profile and self.cover_letter_gen:
            self.application_automator = ApplicationAutomator(profile_manager, self.cover_letter_gen)
    
    def process_job_url(self, url: str, auto_apply: bool = False) -> Dict:
        """
        Process a job URL: Extract → Match → Generate Cover → Apply
        Returns dict with all information for user review
        """
        if not self.profile_manager.profile:
            return {
                'success': False,
                'error': 'Please upload your resume first'
            }
        
        # Step 1: Extract job details
        extracted = self.extractor.extract_from_url(url)
        
        if not extracted.get('success'):
            return {
                'success': False,
                'error': extracted.get('error', 'Failed to extract job details'),
                'step': 'extraction'
            }
        
        # Step 2: Create job listing
        job_data = {
            'title': extracted.get('title', ''),
            'company': extracted.get('company', ''),
            'location': extracted.get('location', ''),
            'description': extracted.get('description', ''),
            'requirements': self.extractor.extract_requirements(extracted.get('description', '')),
            'url': extracted.get('url', url),
            'source': extracted.get('source', 'manual')
        }
        
        job = JobListing(**job_data)
        
        # Step 3: Match job to profile
        match_score = None
        if self.job_matcher:
            match_score = self.job_matcher.calculate_match_score(job)
            job.match_score = match_score
        
        # Step 4: Generate cover letter
        cover_letter = ""
        cover_letter_file = None
        if self.cover_letter_gen:
            try:
                cover_letter = self.cover_letter_gen.generate_cover_letter(job)
                cover_letter = self.cover_letter_gen.add_personal_touches(cover_letter, job)
                cover_letter_file = self.cover_letter_gen.save_cover_letter(cover_letter, job)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to generate cover letter: {str(e)}',
                    'step': 'cover_letter_generation',
                    'job': {
                        'title': job.title,
                        'company': job.company,
                        'location': job.location,
                        'match_score': match_score
                    }
                }
        
        # Step 5: Prepare application (if auto_apply)
        application_result = None
        if auto_apply and self.application_automator:
            try:
                application_result = self.application_automator.submit_application(job, auto_submit=False)
            except Exception as e:
                application_result = {
                    'status': 'error',
                    'message': str(e)
                }
        
        return {
            'success': True,
            'job': {
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description[:500] + '...' if len(job.description) > 500 else job.description,
                'requirements': job.requirements[:5],
                'url': job.url,
                'match_score': match_score,
                'match_percentage': round(match_score * 100, 1) if match_score else None
            },
            'cover_letter': cover_letter,
            'cover_letter_file': cover_letter_file,
            'application_result': application_result,
            'ready_to_apply': True
        }
    
    def apply_to_job(self, url: str) -> Dict:
        """Apply to a job URL (full automated workflow)"""
        result = self.process_job_url(url, auto_apply=True)
        
        if result.get('success'):
            # Save job to user's job list
            job_data = result['job']
            job = JobListing(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                description=job_data.get('description', ''),
                requirements=job_data.get('requirements', []),
                url=job_data['url'],
                match_score=job_data.get('match_score')
            )
            
            if self.application_automator:
                try:
                    self.application_automator.submit_application(job, auto_submit=False)
                except:
                    pass
        
        return result
