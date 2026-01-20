"""
Worldwide Job Search - Searches jobs from multiple sources globally
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from urllib.parse import quote, urlencode
import time
from job_search import JobListing


class WorldwideJobSearch:
    """Search jobs from multiple sources worldwide"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def search_all_sources(self, keywords: List[str], location: str = "", max_results: int = 50) -> List[JobListing]:
        """Search all available job sources"""
        all_jobs = []
        query = " ".join(keywords)
        
        # Search multiple sources with better error handling
        sources = [
            ('Indeed', self._search_indeed_global),
            ('JobStreet', self._search_jobstreet_global),
            ('Reed', self._search_reed),
        ]
        
        for source_name, search_func in sources:
            try:
                jobs = search_func(query, location, max_results // len(sources) + 5)
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"[OK] {source_name}: Found {len(jobs)} jobs")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"[WARNING] {source_name} error: {str(e)[:100]}")
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
    
    def _search_linkedin_jobs(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search LinkedIn jobs"""
        jobs = []
        try:
            query_encoded = quote(query)
            location_encoded = quote(location) if location else ""
            
            # LinkedIn job search URL
            if location:
                url = f"https://www.linkedin.com/jobs/search/?keywords={query_encoded}&location={location_encoded}"
            else:
                url = f"https://www.linkedin.com/jobs/search/?keywords={query_encoded}"
            
            # Note: LinkedIn requires authentication for API access
            # This returns search URLs that can be scraped or accessed via API
            print(f"LinkedIn search: {url}")
            
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        
        return jobs
    
    def _search_indeed_global(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Indeed globally"""
        jobs = []
        try:
            query_encoded = quote(query)
            
            # Determine which Indeed domain to use based on location
            domain_map = {
                'singapore': 'sg.indeed.com',
                'malaysia': 'my.indeed.com',
                'united states': 'www.indeed.com',
                'usa': 'www.indeed.com',
                'united kingdom': 'uk.indeed.com',
                'uk': 'uk.indeed.com',
                'australia': 'au.indeed.com',
                'canada': 'ca.indeed.com',
                'india': 'in.indeed.com',
            }
            
            # Select domain
            location_lower = location.lower() if location else ''
            domain = 'www.indeed.com'  # Default
            for key, dom in domain_map.items():
                if key in location_lower:
                    domain = dom
                    break
            
            # Build URL
            if location and location.lower() != 'worldwide':
                url = f"https://{domain}/jobs?q={query_encoded}&l={quote(location)}"
            else:
                url = f"https://{domain}/jobs?q={query_encoded}"
            
            try:
                time.sleep(2)
                response = requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try multiple selectors for Indeed's changing HTML
                    job_cards = (
                        soup.find_all('div', class_=re.compile(r'job_seen_beacon|jobsearch-SerpJobCard|slider_item')) or
                        soup.find_all('div', {'data-jk': True}) or
                        soup.find_all('a', {'data-jk': True})
                    )
                    
                    for card in job_cards[:max_results]:
                        try:
                            # Try multiple ways to find title
                            title_elem = (
                                card.find('h2', class_=re.compile(r'jobTitle|title')) or
                                card.find('a', class_=re.compile(r'jobTitle')) or
                                card.find('span', class_=re.compile(r'title'))
                            )
                            
                            if not title_elem:
                                # Try data attribute
                                title_text = card.get('aria-label', '') or card.get_text(strip=True)[:100]
                                if not title_text or len(title_text) < 5:
                                    continue
                                title = title_text
                            else:
                                title = title_elem.get_text(strip=True)
                            
                            if not title or len(title) < 3:
                                continue
                            
                            # Find company
                            company_elem = (
                                card.find('span', class_=re.compile(r'companyName|company')) or
                                card.find('a', class_=re.compile(r'company'))
                            )
                            company = company_elem.get_text(strip=True) if company_elem else "Company Not Specified"
                            
                            # Find location
                            location_elem = (
                                card.find('div', class_=re.compile(r'companyLocation|location')) or
                                card.find('span', class_=re.compile(r'location'))
                            )
                            job_location = location_elem.get_text(strip=True) if location_elem else location or "Location Not Specified"
                            
                            # Find URL
                            link_elem = card.find('a', href=True) or card
                            job_url = ""
                            if link_elem:
                                job_url = link_elem.get('href', '')
                                if job_url:
                                    if not job_url.startswith('http'):
                                        job_url = f"https://{domain}{job_url}"
                                else:
                                    # Try data attribute
                                    job_id = card.get('data-jk', '')
                                    if job_id:
                                        job_url = f"https://{domain}/viewjob?jk={job_id}"
                            
                            # Find description
                            desc_elem = card.find('div', class_=re.compile(r'summary|job-snippet|description'))
                            description = desc_elem.get_text(strip=True) if desc_elem else ""
                            
                            job = JobListing(
                                title=title,
                                company=company,
                                location=job_location,
                                description=description,
                                requirements=[],
                                url=job_url or url,
                                source=f"indeed-{domain.split('.')[0]}"
                            )
                            jobs.append(job)
                        except Exception as e:
                            continue
                else:
                    print(f"Indeed returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Network error searching Indeed: {str(e)[:100]}")
            except Exception as e:
                print(f"Error parsing Indeed: {str(e)[:100]}")
        except Exception as e:
            print(f"Indeed search error: {str(e)[:100]}")
        
        return jobs
    
    def _search_jobstreet_global(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search JobStreet (SE Asia)"""
        jobs = []
        try:
            query_encoded = quote(query)
            location_encoded = quote(location) if location else ""
            
            domains = [
                ('sg', 'Singapore'),
                ('my', 'Malaysia'),
                ('ph', 'Philippines'),
                ('id', 'Indonesia'),
                ('th', 'Thailand'),
                ('vn', 'Vietnam'),
            ]
            
            for code, country in domains[:3]:
                try:
                    url = f"https://www.jobstreet.com.{code}/en/job-search/job-vacancy.php?ojs=3&key={query_encoded}"
                    if location_encoded:
                        url += f"&location={location_encoded}"
                    
                    time.sleep(2)
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # JobStreet HTML parsing
                        job_cards = soup.find_all('article', class_=re.compile(r'job|card'))
                        
                        for card in job_cards[:5]:
                            try:
                                title_elem = card.find('h1') or card.find('h2') or card.find('a', class_=re.compile(r'title'))
                                if not title_elem:
                                    continue
                                
                                title = title_elem.get_text(strip=True)
                                company_elem = card.find('span', class_=re.compile(r'company'))
                                company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                                
                                link_elem = card.find('a', href=True)
                                job_url = link_elem['href'] if link_elem else ""
                                if job_url and not job_url.startswith('http'):
                                    job_url = f"https://www.jobstreet.com.{code}{job_url}"
                                
                                job = JobListing(
                                    title=title,
                                    company=company,
                                    location=location or country,
                                    description="",
                                    requirements=[],
                                    url=job_url,
                                    source=f"jobstreet-{code}"
                                )
                                jobs.append(job)
                            except:
                                continue
                        
                        if len(jobs) >= max_results:
                            break
                except:
                    continue
        except Exception as e:
            print(f"JobStreet search error: {e}")
        
        return jobs
    
    def _search_glassdoor_global(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Glassdoor"""
        jobs = []
        # Glassdoor requires API partnership
        return jobs
    
    def _search_adzuna(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Adzuna (global job aggregator)"""
        jobs = []
        try:
            # Adzuna has an API but requires key
            # For now, return empty - can be implemented with API key
            pass
        except:
            pass
        return jobs
    
    def _search_reed(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Reed (UK job board)"""
        jobs = []
        try:
            query_encoded = quote(query)
            if location:
                url = f"https://www.reed.co.uk/jobs/{query_encoded}-jobs-in-{quote(location)}"
            else:
                url = f"https://www.reed.co.uk/jobs/{query_encoded}-jobs"
            
            time.sleep(2)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('article', class_=re.compile(r'job-result'))
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h3', class_=re.compile(r'title'))
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        company_elem = card.find('a', class_=re.compile(r'gtmJobListingPostedBy'))
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        location_elem = card.find('li', class_=re.compile(r'location'))
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "UK"
                        
                        link_elem = card.find('a', href=True)
                        job_url = ""
                        if link_elem:
                            job_url = link_elem['href']
                            if not job_url.startswith('http'):
                                job_url = f"https://www.reed.co.uk{job_url}"
                        
                        job = JobListing(
                            title=title,
                            company=company,
                            location=job_location,
                            description="",
                            requirements=[],
                            url=job_url,
                            source="reed"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"Reed search error: {e}")
        
        return jobs
