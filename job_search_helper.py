"""
Job Search Helper - Provides search URLs and instructions
"""
from urllib.parse import quote
from typing import List, Dict


class JobSearchHelper:
    """Helper class to generate job search URLs and provide instructions"""
    
    @staticmethod
    def generate_search_urls(keywords: List[str], location: str = "Singapore") -> Dict[str, str]:
        """Generate search URLs for various job boards"""
        query = " ".join(keywords)
        query_encoded = quote(query)
        location_encoded = quote(location)
        
        urls = {
            "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={query_encoded}&location={location_encoded}",
            "Indeed Singapore": f"https://sg.indeed.com/jobs?q={query_encoded}&l={location_encoded}",
            "JobStreet Singapore": f"https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=3&key={query_encoded}&location={location_encoded}",
            "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query_encoded}&locT=C&locId=1147401&locKeyword={location_encoded}",
            "MyCareersFuture (Singapore)": f"https://www.mycareersfuture.gov.sg/search?search={query_encoded}&sortBy=relevancy&page=0",
            "JobsDB Singapore": f"https://sg.jobsdb.com/j?q={query_encoded}&l={location_encoded}",
        }
        
        return urls
    
    @staticmethod
    def print_search_instructions(keywords: List[str], location: str = "Singapore"):
        """Print search URLs and instructions"""
        print("\n" + "=" * 60)
        print("Job Search URLs - Visit these to find jobs manually")
        print("=" * 60)
        print(f"\nKeywords: {', '.join(keywords)}")
        print(f"Location: {location}\n")
        
        urls = JobSearchHelper.generate_search_urls(keywords, location)
        
        for platform, url in urls.items():
            print(f"{platform}:")
            print(f"  {url}\n")
        
        print("=" * 60)
        print("\nInstructions:")
        print("1. Visit the URLs above to find jobs")
        print("2. When you find a job you're interested in:")
        print("   - Copy the job URL")
        print("   - Run: python add_jobs_manual.py")
        print("   - Or edit jobs.json directly")
        print("3. After adding jobs, run:")
        print("   python ai_job_agent.py --match")
        print("   python ai_job_agent.py --apply")
        print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    keywords = sys.argv[1:] if len(sys.argv) > 1 else ["software engineer", "data scientist"]
    location = "Singapore"
    
    JobSearchHelper.print_search_instructions(keywords, location)
