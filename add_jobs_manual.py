"""
Manual Job Entry Tool - Add jobs manually or from URLs
"""
import json
from job_search import JobSearchEngine, JobListing
from typing import List, Dict


def add_jobs_from_urls(urls: List[str], keywords: List[str] = None) -> List[JobListing]:
    """
    Add jobs by providing URLs to job postings
    This is a helper to manually add jobs you find
    """
    jobs = []
    search_engine = JobSearchEngine()
    
    print("=" * 60)
    print("Manual Job Entry")
    print("=" * 60)
    print("\nTo add jobs manually, you can:")
    print("1. Use the search URLs provided by the job search")
    print("2. Add jobs directly using this script")
    print("3. Edit jobs.json directly\n")
    
    return jobs


def create_job_from_dict(job_data: Dict) -> JobListing:
    """Create a JobListing from a dictionary"""
    return JobListing(
        title=job_data.get("title", ""),
        company=job_data.get("company", ""),
        location=job_data.get("location", ""),
        description=job_data.get("description", ""),
        requirements=job_data.get("requirements", []),
        url=job_data.get("url", ""),
        salary=job_data.get("salary"),
        job_type=job_data.get("job_type"),
        posted_date=job_data.get("posted_date"),
        source=job_data.get("source", "manual")
    )


def add_job_interactive():
    """Interactive job entry"""
    print("\nEnter job details (press Enter to skip optional fields):")
    
    title = input("Job Title: ").strip()
    if not title:
        print("Title is required!")
        return None
    
    company = input("Company: ").strip()
    location = input("Location: ").strip() or "Singapore"
    url = input("Job URL: ").strip()
    description = input("Description (or press Enter to skip): ").strip()
    
    requirements = []
    print("Enter requirements (one per line, press Enter twice when done):")
    while True:
        req = input("  Requirement: ").strip()
        if not req:
            break
        requirements.append(req)
    
    job_data = {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "requirements": requirements,
        "url": url,
        "source": "manual"
    }
    
    return create_job_from_dict(job_data)


if __name__ == "__main__":
    print("Manual Job Entry Tool")
    print("=" * 60)
    
    # Load existing jobs
    search_engine = JobSearchEngine()
    existing_jobs = search_engine.load_jobs()
    print(f"\nCurrently have {len(existing_jobs)} jobs in jobs.json")
    
    # Add new jobs
    new_jobs = []
    while True:
        job = add_job_interactive()
        if job:
            new_jobs.append(job)
            add_more = input("\nAdd another job? (y/n): ").strip().lower()
            if add_more != 'y':
                break
        else:
            break
    
    if new_jobs:
        # Combine with existing
        all_jobs = existing_jobs + new_jobs
        search_engine.jobs = all_jobs
        search_engine.save_jobs()
        print(f"\n[OK] Added {len(new_jobs)} jobs. Total: {len(all_jobs)} jobs")
    else:
        print("\nNo jobs added.")
