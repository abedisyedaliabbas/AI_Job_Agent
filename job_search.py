"""
Job Search Module - Searches for jobs from various sources
"""
import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import time
import re
from urllib.parse import quote, urlencode
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("[WARNING] BeautifulSoup4 not installed. Web scraping disabled. Install with: pip install beautifulsoup4")


@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    url: str
    salary: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    posted_date: Optional[str] = None
    source: Optional[str] = None  # linkedin, indeed, etc.
    match_score: Optional[float] = None


class JobSearchEngine:
    """Searches for jobs from multiple sources"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.jobs: List[JobListing] = []
    
    def search_linkedin(self, keywords: List[str], location: str = "Singapore", 
                       max_results: int = 50) -> List[JobListing]:
        """
        Search LinkedIn jobs
        Note: LinkedIn requires authentication for API access. This generates a search URL.
        For automated access, use LinkedIn API with proper OAuth authentication.
        """
        jobs = []
        search_query = " ".join(keywords)
        
        # Build LinkedIn job search URL
        # LinkedIn job search URL format
        location_encoded = quote(location)
        query_encoded = quote(search_query)
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={query_encoded}&location={location_encoded}"
        
        print(f"LinkedIn search URL: {linkedin_url}")
        print("[INFO] LinkedIn requires authentication for API access.")
        print("[INFO] To use LinkedIn API, you need to:")
        print("  1. Create a LinkedIn app at https://www.linkedin.com/developers/")
        print("  2. Get OAuth 2.0 credentials")
        print("  3. Add access token to config.json")
        print("[INFO] For now, you can manually visit the URL above to find jobs.")
        
        # If API key is provided, try to use it
        if self.api_keys.get("linkedin"):
            try:
                headers = {
                    'Authorization': f'Bearer {self.api_keys.get("linkedin")}',
                    'Content-Type': 'application/json'
                }
                # LinkedIn API v2 job search endpoint
                # Note: This is a placeholder - actual implementation requires proper API setup
                print("[INFO] LinkedIn API key found, but full API integration requires additional setup.")
            except Exception as e:
                print(f"[WARNING] LinkedIn API error: {e}")
        
        return jobs
    
    def search_indeed(self, keywords: List[str], location: str = "Singapore",
                     max_results: int = 50) -> List[JobListing]:
        """
        Search Indeed jobs using web scraping
        Note: Be respectful of rate limits and Indeed's terms of service.
        """
        jobs = []
        if not BS4_AVAILABLE:
            print("[WARNING] BeautifulSoup4 not available. Install with: pip install beautifulsoup4")
            return jobs
        
        search_query = " ".join(keywords)
        print(f"Searching Indeed for: {search_query} in {location}")
        
        try:
            # Build Indeed search URL
            # Indeed URL format: https://sg.indeed.com/jobs?q=query&l=location
            location_code = self._get_indeed_location_code(location)
            query_encoded = quote(search_query)
            
            if location_code:
                indeed_url = f"https://{location_code}.indeed.com/jobs?q={query_encoded}&l={location}"
            else:
                indeed_url = f"https://www.indeed.com/jobs?q={query_encoded}&l={location}"
            
            print(f"Indeed URL: {indeed_url}")
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            # Make request with rate limiting
            time.sleep(2)  # Be respectful - wait 2 seconds between requests
            response = requests.get(indeed_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings (Indeed's HTML structure may vary)
                job_cards = soup.find_all('div', class_=re.compile(r'job_seen_beacon|jobsearch-SerpJobCard'))
                
                for card in job_cards[:max_results]:
                    try:
                        # Extract job title
                        title_elem = card.find('h2', class_=re.compile(r'jobTitle|title'))
                        if not title_elem:
                            title_elem = card.find('a', {'data-jk': True})
                        title = title_elem.get_text(strip=True) if title_elem else "N/A"
                        
                        # Extract company
                        company_elem = card.find('span', class_=re.compile(r'companyName'))
                        if not company_elem:
                            company_elem = card.find('a', class_=re.compile(r'company'))
                        company = company_elem.get_text(strip=True) if company_elem else "N/A"
                        
                        # Extract location
                        location_elem = card.find('div', class_=re.compile(r'companyLocation'))
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Extract job URL
                        link_elem = card.find('a', href=True)
                        if link_elem:
                            job_url = link_elem['href']
                            if not job_url.startswith('http'):
                                job_url = f"https://www.indeed.com{job_url}"
                        else:
                            job_url = indeed_url
                        
                        # Extract description snippet
                        desc_elem = card.find('div', class_=re.compile(r'summary|job-snippet'))
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        if title != "N/A" and company != "N/A":
                            job = JobListing(
                                title=title,
                                company=company,
                                location=job_location,
                                description=description,
                                requirements=[],  # Would need to visit individual job pages
                                url=job_url,
                                source="indeed"
                            )
                            jobs.append(job)
                    except Exception as e:
                        print(f"[WARNING] Error parsing job card: {e}")
                        continue
                
                print(f"[OK] Found {len(jobs)} jobs from Indeed")
            else:
                print(f"[WARNING] Indeed returned status code {response.status_code}")
                print(f"[INFO] You can manually search at: {indeed_url}")
        
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Error connecting to Indeed: {e}")
            print("[INFO] This might be due to network issues or rate limiting.")
        except Exception as e:
            print(f"[WARNING] Error scraping Indeed: {e}")
            print("[INFO] Indeed's HTML structure may have changed. Consider using their API or manual search.")
        
        return jobs
    
    def _get_indeed_location_code(self, location: str) -> str:
        """Get Indeed country code for location"""
        location_lower = location.lower()
        location_map = {
            'singapore': 'sg',
            'united states': 'www',
            'usa': 'www',
            'uk': 'uk',
            'united kingdom': 'uk',
            'australia': 'au',
            'canada': 'ca',
            'india': 'in',
            'germany': 'de',
            'france': 'fr',
        }
        
        for key, code in location_map.items():
            if key in location_lower:
                return code
        
        return 'www'  # Default to US site
    
    def search_glassdoor(self, keywords: List[str], location: str = "Singapore",
                        max_results: int = 50) -> List[JobListing]:
        """Search Glassdoor jobs"""
        jobs = []
        search_query = " ".join(keywords)
        print(f"Searching Glassdoor for: {search_query} in {location}")
        
        # Glassdoor requires authentication for API access
        # Build search URL for manual use
        query_encoded = quote(search_query)
        location_encoded = quote(location)
        glassdoor_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query_encoded}&locT=C&locId=1147401&locKeyword={location_encoded}"
        
        print(f"Glassdoor URL: {glassdoor_url}")
        print("[INFO] Glassdoor requires API partnership for automated access.")
        print("[INFO] You can manually search at the URL above.")
        
        return jobs
    
    def search_jobstreet(self, keywords: List[str], location: str = "Singapore",
                        max_results: int = 50) -> List[JobListing]:
        """Search JobStreet (popular in Singapore/SE Asia)"""
        jobs = []
        if not BS4_AVAILABLE:
            return jobs
        
        search_query = " ".join(keywords)
        print(f"Searching JobStreet for: {search_query} in {location}")
        
        try:
            # JobStreet Singapore URL
            query_encoded = quote(search_query)
            location_encoded = quote(location)
            jobstreet_url = f"https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=3&key={query_encoded}&location={location_encoded}"
            
            print(f"JobStreet URL: {jobstreet_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
            
            time.sleep(2)
            response = requests.get(jobstreet_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # JobStreet HTML structure - this may need adjustment
                job_cards = soup.find_all('article', class_=re.compile(r'job|card'))
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h1') or card.find('h2') or card.find('a', class_=re.compile(r'title'))
                        title = title_elem.get_text(strip=True) if title_elem else None
                        
                        company_elem = card.find('span', class_=re.compile(r'company')) or card.find('a', class_=re.compile(r'company'))
                        company = company_elem.get_text(strip=True) if company_elem else None
                        
                        if title and company:
                            link_elem = card.find('a', href=True)
                            job_url = link_elem['href'] if link_elem else jobstreet_url
                            if not job_url.startswith('http'):
                                job_url = f"https://www.jobstreet.com.sg{job_url}"
                            
                            job = JobListing(
                                title=title,
                                company=company,
                                location=location,
                                description="",
                                requirements=[],
                                url=job_url,
                                source="jobstreet"
                            )
                            jobs.append(job)
                    except:
                        continue
                
                if jobs:
                    print(f"[OK] Found {len(jobs)} jobs from JobStreet")
            else:
                print(f"[WARNING] JobStreet returned status code {response.status_code}")
        
        except Exception as e:
            print(f"[WARNING] Error searching JobStreet: {e}")
        
        return jobs
    
    def search_manual_jobs(self, job_listings: List[Dict]) -> List[JobListing]:
        """Add manually provided job listings"""
        jobs = []
        for job_data in job_listings:
            job = JobListing(
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
            jobs.append(job)
        return jobs
    
    def search_all_sources(self, keywords: List[str], location: str = "Singapore",
                          max_results_per_source: int = 20) -> List[JobListing]:
        """Search all available job sources"""
        all_jobs = []
        
        print("\n[INFO] Starting job search across multiple sources...")
        print("[INFO] Note: Some sources require manual access or API keys.\n")
        
        # Search Indeed (web scraping)
        try:
            indeed_jobs = self.search_indeed(keywords, location, max_results_per_source)
            all_jobs.extend(indeed_jobs)
            if indeed_jobs:
                print(f"[OK] Indeed: {len(indeed_jobs)} jobs found\n")
        except Exception as e:
            print(f"[WARNING] Error searching Indeed: {e}\n")
        
        # Search JobStreet (for Singapore/SE Asia)
        if "singapore" in location.lower() or "asia" in location.lower():
            try:
                jobstreet_jobs = self.search_jobstreet(keywords, location, max_results_per_source)
                all_jobs.extend(jobstreet_jobs)
                if jobstreet_jobs:
                    print(f"[OK] JobStreet: {len(jobstreet_jobs)} jobs found\n")
            except Exception as e:
                print(f"[WARNING] Error searching JobStreet: {e}\n")
        
        # Search LinkedIn (URL generation only - requires API for automation)
        try:
            linkedin_jobs = self.search_linkedin(keywords, location, max_results_per_source)
            all_jobs.extend(linkedin_jobs)
        except Exception as e:
            print(f"[WARNING] Error with LinkedIn: {e}\n")
        
        # Search Glassdoor (URL generation only)
        try:
            glassdoor_jobs = self.search_glassdoor(keywords, location, max_results_per_source)
            all_jobs.extend(glassdoor_jobs)
        except Exception as e:
            print(f"[WARNING] Error with Glassdoor: {e}\n")
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            key = (job.title.lower(), job.company.lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        if len(all_jobs) > len(unique_jobs):
            print(f"[INFO] Removed {len(all_jobs) - len(unique_jobs)} duplicate jobs")
        
        self.jobs = unique_jobs
        return unique_jobs
    
    def save_jobs(self, filename: str = "jobs.json"):
        """Save found jobs to JSON file"""
        jobs_data = []
        for job in self.jobs:
            jobs_data.append({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "requirements": job.requirements,
                "url": job.url,
                "salary": job.salary,
                "job_type": job.job_type,
                "posted_date": job.posted_date,
                "source": job.source,
                "match_score": job.match_score
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
    
    def load_jobs(self, filename: str = "jobs.json") -> List[JobListing]:
        """Load jobs from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
                jobs = []
                for job_data in jobs_data:
                    jobs.append(JobListing(**job_data))
                self.jobs = jobs
                return jobs
        except FileNotFoundError:
            return []
