"""
Example usage of the AI Job Agent
"""
from ai_job_agent import AIJobAgent
from job_search import JobListing


def example_manual_job_search():
    """Example: Add manual job listings and process them"""
    agent = AIJobAgent()
    agent.initialize_profile()
    
    # Create some example job listings
    example_jobs = [
        {
            "title": "Software Engineer",
            "company": "Tech Company",
            "location": "Singapore",
            "description": "We are seeking a software engineer with expertise in full-stack development, cloud technologies, and modern programming frameworks. The ideal candidate will have experience in software development and system design.",
            "requirements": [
                "Bachelor's or Master's in Computer Science, Software Engineering, or related field",
                "Experience with web development frameworks",
                "Proficiency in Python, JavaScript, and modern programming languages",
                "Knowledge of cloud platforms and DevOps practices",
                "Strong problem-solving and collaboration skills"
            ],
            "url": "https://example.com/job/123",
            "source": "manual"
        },
        {
            "title": "Data Scientist",
            "company": "Analytics Company",
            "location": "Singapore",
            "description": "Join our team to develop data-driven solutions for business intelligence and analytics. Work on cutting-edge projects combining machine learning with real-world applications.",
            "requirements": [
                "Bachelor's or Master's in Data Science, Computer Science, or related field",
                "Experience with machine learning frameworks (PyTorch, scikit-learn)",
                "Background in data analysis, statistics, or machine learning",
                "Python programming skills",
                "Strong analytical and problem-solving abilities"
            ],
            "url": "https://example.com/job/456",
            "source": "manual"
        }
    ]
    
    # Add jobs to search engine
    jobs = agent.job_search.search_manual_jobs(example_jobs)
    agent.job_search.save_jobs("example_jobs.json")
    
    print(f"Added {len(jobs)} example jobs\n")
    
    # Match jobs to profile
    matched_jobs = agent.match_jobs(jobs)
    
    # Generate cover letters for top matches
    if matched_jobs:
        print(f"\n[GENERATE] Generating cover letters for top {min(3, len(matched_jobs))} matches...\n")
        for job in matched_jobs[:3]:
            cover_letter = agent.cover_letter_gen.generate_cover_letter(job)
            filename = agent.cover_letter_gen.save_cover_letter(cover_letter, job)
            print(f"[OK] Generated cover letter: {filename}")
            print(f"  Match Score: {job.match_score:.2%}\n")
    
    # Show stats
    agent.show_application_stats()


def example_full_workflow():
    """Example: Run the complete workflow"""
    agent = AIJobAgent()
    agent.run_full_workflow()


if __name__ == "__main__":
    print("=" * 60)
    print("AI Job Agent - Example Usage")
    print("=" * 60)
    print("\nThis example demonstrates:")
    print("1. Adding manual job listings")
    print("2. Matching jobs to your profile")
    print("3. Generating cover letters")
    print("\n" + "=" * 60 + "\n")
    
    # Run example with manual jobs
    example_manual_job_search()
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
    print("\nTo run the full workflow with real job searches:")
    print("  python ai_job_agent.py --full")
    print("\nOr customize your search:")
    print("  python ai_job_agent.py --search --keywords 'software engineer' --location 'Singapore'")
