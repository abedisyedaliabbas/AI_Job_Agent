"""
AI Job Agent - Main orchestrator for job search and application system
"""
import json
import argparse
from typing import List, Dict, Optional
from profile_manager import ProfileManager
from cv_parser import parse_abedi_cv
from job_search import JobSearchEngine, JobListing
from job_matcher import JobMatcher
from cover_letter_generator import CoverLetterGenerator
from application_automator import ApplicationAutomator


class AIJobAgent:
    """Main AI agent for job search and application"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize components
        self.profile_manager = ProfileManager(self.config.get("profile_file", "profile.json"))
        self.job_search = JobSearchEngine(self.config.get("api_keys", {}))
        self.job_matcher = None  # Will be initialized after profile is loaded
        self.cover_letter_gen = None  # Will be initialized after profile is loaded
        self.application_automator = None  # Will be initialized after profile is loaded
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default config
            return {
                "profile_file": "profile.json",
                "search_keywords": [
                    "software engineer",
                    "data scientist",
                    "research scientist",
                    "product manager",
                    "business analyst"
                ],
                "location": "Singapore",
                "min_match_score": 0.5,
                "auto_apply": False,
                "max_jobs_per_search": 50,
                "api_keys": {}
            }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def initialize_profile(self):
        """Initialize profile from CV data"""
        try:
            # Try to load existing profile
            self.profile_manager.load_from_file()
            print(f"[OK] Loaded existing profile for {self.profile_manager.profile.name}")
        except FileNotFoundError:
            # Create profile from CV parser
            print("Creating profile from CV data...")
            cv_data = parse_abedi_cv()
            self.profile_manager.load_from_cv_data(cv_data)
            self.profile_manager.save_to_file()
            print(f"[OK] Created profile for {self.profile_manager.profile.name}")
        
        # Initialize dependent components
        self.job_matcher = JobMatcher(self.profile_manager)
        self.cover_letter_gen = CoverLetterGenerator(self.profile_manager)
        self.application_automator = ApplicationAutomator(
            self.profile_manager,
            self.cover_letter_gen
        )
    
    def search_jobs(self, keywords: Optional[List[str]] = None, 
                   location: Optional[str] = None) -> List[JobListing]:
        """Search for jobs"""
        keywords = keywords or self.config.get("search_keywords", [])
        location = location or self.config.get("location", "Singapore")
        
        print(f"\n[SEARCH] Searching for jobs...")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Location: {location}\n")
        
        jobs = self.job_search.search_all_sources(
            keywords=keywords,
            location=location,
            max_results_per_source=self.config.get("max_jobs_per_search", 20)
        )
        
        print(f"\nFound {len(jobs)} jobs from automated search")
        
        # If no jobs found, provide helpful instructions
        if len(jobs) == 0:
            print("\n" + "=" * 60)
            print("[INFO] No jobs found via automated search.")
            print("[INFO] This is common as job boards block automated scraping.")
            print("\n[SOLUTION] Use manual job entry:")
            print("  1. Run: python job_search_helper.py 'keyword1' 'keyword2'")
            print("     This will show you search URLs to visit")
            print("  2. Visit the URLs and find jobs you're interested in")
            print("  3. Add jobs manually:")
            print("     - Run: python add_jobs_manual.py")
            print("     - Or edit jobs.json directly")
            print("  4. Then run: python ai_job_agent.py --match")
            print("=" * 60)
            
            # Import and show search URLs
            try:
                from job_search_helper import JobSearchHelper
                JobSearchHelper.print_search_instructions(keywords, location)
            except:
                pass
        
        # Save jobs
        self.job_search.save_jobs("jobs.json")
        
        return jobs
    
    def match_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """Match and score jobs against profile"""
        if not self.job_matcher:
            raise ValueError("Profile not initialized. Call initialize_profile() first.")
        
        print(f"\n[MATCH] Matching {len(jobs)} jobs to your profile...")
        
        min_score = self.config.get("min_match_score", 0.5)
        matched_jobs = self.job_matcher.match_jobs(jobs, min_score=min_score)
        
        print(f"Found {len(matched_jobs)} jobs with match score >= {min_score}")
        
        # Display top matches
        print("\n[TOP MATCHES] Top 10 Matches:")
        for i, job in enumerate(matched_jobs[:10], 1):
            print(f"{i}. {job.title} at {job.company} - Score: {job.match_score:.2%}")
        
        return matched_jobs
    
    def prepare_applications(self, jobs: List[JobListing], 
                            min_match_score: Optional[float] = None) -> List[Dict]:
        """Prepare applications for matched jobs"""
        if not self.application_automator:
            raise ValueError("Profile not initialized. Call initialize_profile() first.")
        
        min_score = min_match_score or self.config.get("min_match_score", 0.5)
        
        print(f"\n[PREPARE] Preparing applications for jobs with score >= {min_score}...")
        
        # Filter jobs by match score
        qualified_jobs = [job for job in jobs if job.match_score and job.match_score >= min_score]
        
        prepared = self.application_automator.batch_prepare_applications(
            qualified_jobs,
            min_match_score=min_score
        )
        
        print(f"\n[OK] Prepared {len(prepared)} applications")
        
        return prepared
    
    def show_application_stats(self):
        """Display application statistics"""
        if not self.application_automator:
            print("Profile not initialized.")
            return
        
        stats = self.application_automator.get_application_stats()
        
        print("\n[STATS] Application Statistics:")
        print(f"Total Applications: {stats['total_applications']}")
        print(f"Average Match Score: {stats.get('average_match_score', 0):.2%}")
        
        if stats.get('by_status'):
            print("\nBy Status:")
            for status, count in stats['by_status'].items():
                print(f"  {status}: {count}")
        
        if stats.get('by_month'):
            print("\nBy Month:")
            for month, count in sorted(stats['by_month'].items()):
                print(f"  {month}: {count}")
    
    def run_full_workflow(self):
        """Run the complete job search and application workflow"""
        print("=" * 60)
        print("AI Job Agent - Starting Full Workflow")
        print("=" * 60)
        
        # 1. Initialize profile
        self.initialize_profile()
        
        # 2. Search for jobs
        jobs = self.search_jobs()
        
        if not jobs:
            print("\n[WARNING] No jobs found. Try adjusting search keywords or location.")
            return
        
        # 3. Match jobs
        matched_jobs = self.match_jobs(jobs)
        
        if not matched_jobs:
            print("\n[WARNING] No jobs matched your profile. Try lowering the minimum match score.")
            return
        
        # 4. Prepare applications
        prepared = self.prepare_applications(matched_jobs)
        
        # 5. Show stats
        self.show_application_stats()
        
        print("\n" + "=" * 60)
        print("[OK] Workflow Complete!")
        print("=" * 60)
        print(f"\nCover letters saved. Review and submit applications manually.")
        print(f"Application log saved to: applications_log.json")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Job Agent - Automated Job Search and Application")
    parser.add_argument("--search", action="store_true", help="Search for jobs")
    parser.add_argument("--match", action="store_true", help="Match existing jobs to profile")
    parser.add_argument("--apply", action="store_true", help="Prepare applications")
    parser.add_argument("--stats", action="store_true", help="Show application statistics")
    parser.add_argument("--full", action="store_true", help="Run full workflow (search + match + apply)")
    parser.add_argument("--keywords", nargs="+", help="Search keywords")
    parser.add_argument("--location", type=str, help="Job location")
    parser.add_argument("--min-score", type=float, help="Minimum match score (0.0-1.0)")
    
    args = parser.parse_args()
    
    agent = AIJobAgent()
    
    if args.full:
        agent.run_full_workflow()
    else:
        agent.initialize_profile()
        
        if args.search:
            keywords = args.keywords or agent.config.get("search_keywords")
            location = args.location or agent.config.get("location")
            agent.search_jobs(keywords, location)
        
        if args.match:
            jobs = agent.job_search.load_jobs()
            if jobs:
                agent.match_jobs(jobs)
            else:
                print("No jobs found. Run --search first.")
        
        if args.apply:
            jobs = agent.job_search.load_jobs()
            if jobs:
                min_score = args.min_score or agent.config.get("min_match_score", 0.5)
                agent.prepare_applications(jobs, min_match_score=min_score)
            else:
                print("No jobs found. Run --search first.")
        
        if args.stats:
            agent.show_application_stats()
        
        if not any([args.search, args.match, args.apply, args.stats]):
            # Default: run full workflow
            agent.run_full_workflow()


if __name__ == "__main__":
    main()
