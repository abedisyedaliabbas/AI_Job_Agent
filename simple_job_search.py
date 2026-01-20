"""
Simple, Reliable Job Search - Actually works!
Uses direct job board APIs and reliable scraping
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from job_search import JobListing
from urllib.parse import quote
import time
import re


class SimpleJobSearch:
    """Simple, reliable job search that actually works"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def search(self, keywords: List[str], location: str = "", max_results: int = 20) -> List[JobListing]:
        """Search for jobs - simple and reliable"""
        all_jobs = []
        query = " ".join(keywords[:3])  # Use top 3 keywords
        
        # Try multiple sources
        sources = [
            self._search_indeed_simple,
            self._search_jobstreet_simple,
        ]
        
        for search_func in sources:
            try:
                jobs = search_func(query, location, max_results // len(sources) + 5)
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"[OK] Found {len(jobs)} jobs from {search_func.__name__}")
                time.sleep(1)
            except Exception as e:
                print(f"[WARNING] {search_func.__name__} failed: {str(e)[:80]}")
                continue
        
        # Remove duplicates
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            if not job.title or not job.company:
                continue
            key = (job.title.lower().strip(), job.company.lower().strip())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs[:max_results]
    
    def _search_indeed_simple(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Simple Indeed search"""
        jobs = []
        try:
            query_encoded = quote(query)
            domain = 'www.indeed.com'
            
            if location and location.lower() not in ['worldwide', '']:
                url = f"https://{domain}/jobs?q={query_encoded}&l={quote(location)}"
            else:
                url = f"https://{domain}/jobs?q={query_encoded}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all job cards
                job_cards = soup.find_all(['div', 'a'], {'data-jk': True})
                
                if not job_cards:
                    # Try alternative selectors
                    job_cards = soup.find_all('div', class_=re.compile(r'job|card', re.I))
                
                for card in job_cards[:max_results]:
                    try:
                        # Get job ID
                        job_id = card.get('data-jk', '')
                        if not job_id:
                            continue
                        
                        # Build job URL
                        job_url = f"https://{domain}/viewjob?jk={job_id}"
                        
                        # Extract title
                        title_elem = card.find(['h2', 'a', 'span'], class_=re.compile(r'title|job', re.I))
                        if not title_elem:
                            title_elem = card.find('a')
                        title = title_elem.get_text(strip=True) if title_elem else f"Job {job_id[:8]}"
                        
                        if len(title) < 5:
                            continue
                        
                        # Extract company
                        company_elem = card.find(['span', 'div'], class_=re.compile(r'company', re.I))
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        # Extract location
                        loc_elem = card.find(['div', 'span'], class_=re.compile(r'location', re.I))
                        job_location = loc_elem.get_text(strip=True) if loc_elem else location or "Remote"
                        
                        # Extract description snippet
                        desc_elem = card.find(['div', 'span'], class_=re.compile(r'summary|snippet', re.I))
                        description = desc_elem.get_text(strip=True)[:200] if desc_elem else f"Position for {query}"
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=description,
                            requirements=[],
                            url=job_url,
                            source="indeed"
                        )
                        jobs.append(job)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Indeed search error: {str(e)[:100]}")
        
        return jobs
    
    def _search_jobstreet_simple(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Simple JobStreet search (for Singapore/SE Asia)"""
        jobs = []
        try:
            if 'singapore' not in location.lower() and location.lower() not in ['', 'worldwide']:
                return jobs  # JobStreet is mainly for SE Asia
            
            query_encoded = quote(query)
            url = f"https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=3&key={query_encoded}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings
                job_cards = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'job', re.I))
                
                for card in job_cards[:max_results]:
                    try:
                        # Extract title
                        title_elem = card.find(['h1', 'h2', 'h3', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else None
                        
                        if not title or len(title) < 5:
                            continue
                        
                        # Extract company
                        company_elem = card.find(['span', 'div'], class_=re.compile(r'company', re.I))
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        # Extract location
                        loc_elem = card.find(['span', 'div'], class_=re.compile(r'location', re.I))
                        job_location = loc_elem.get_text(strip=True) if loc_elem else "Singapore"
                        
                        # Get URL
                        link = card.find('a', href=True)
                        job_url = ""
                        if link:
                            job_url = link.get('href', '')
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://www.jobstreet.com.sg{job_url}"
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Position for {query}",
                            requirements=[],
                            url=job_url or url,
                            source="jobstreet"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"JobStreet search error: {str(e)[:100]}")
        
        return jobs
