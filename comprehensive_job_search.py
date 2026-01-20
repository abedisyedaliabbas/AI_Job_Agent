"""
Comprehensive Job Search - Aggregates jobs from multiple sources
Can handle 1000+ jobs by searching across all major job boards
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from job_search import JobListing
from urllib.parse import quote, urlparse, parse_qs
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import random


class ComprehensiveJobSearch:
    """
    Comprehensive job search that aggregates from multiple sources
    Can find 1000+ jobs by searching across all major job boards
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.max_workers = 5  # Parallel searches
        self.request_delay = 1  # Delay between requests
    
    def search(self, keywords: List[str], location: str = "", max_results: int = 1000) -> List[JobListing]:
        """
        Comprehensive search across all major job boards
        Returns up to max_results jobs (can be 1000+)
        """
        all_jobs = []
        query = " ".join(keywords[:5])  # Use top 5 keywords
        
        print(f"[COMPREHENSIVE] Searching for: '{query}' in '{location or 'Worldwide'}' (max: {max_results} jobs)")
        
        # Define all job board search functions
        search_functions = [
            ('indeed', self._search_indeed),
            ('linkedin', self._search_linkedin),
            ('glassdoor', self._search_glassdoor),
            ('monster', self._search_monster),
            ('ziprecruiter', self._search_ziprecruiter),
            ('jobstreet', self._search_jobstreet),
            ('reed', self._search_reed),
            ('adzuna', self._search_adzuna),
            ('mycareersfuture', self._search_mycareersfuture),
            ('jobsdb', self._search_jobsdb),
        ]
        
        # Search in parallel for speed
        # Calculate jobs per source - ensure we get enough from each source
        jobs_per_source = max(50, max_results // len(search_functions))  # At least 50 per source, or distribute evenly
        print(f"[COMPREHENSIVE] Searching {len(search_functions)} sources, requesting {jobs_per_source} jobs per source")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(func, query, location, jobs_per_source): source
                for source, func in search_functions
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    jobs = future.result()
                    if jobs:
                        all_jobs.extend(jobs)
                        print(f"[COMPREHENSIVE] {source.capitalize()}: Found {len(jobs)} jobs")
                    time.sleep(self.request_delay)  # Be respectful
                except Exception as e:
                    print(f"[COMPREHENSIVE] {source.capitalize()} error: {str(e)[:80]}")
                    continue
        
        # Remove duplicates based on title + company
        unique_jobs = self._remove_duplicates(all_jobs)
        
        # PRIORITIZE: Sort to prefer company website jobs over LinkedIn
        # Company website jobs are easier to apply to and more direct
        def job_priority(job):
            url_lower = (job.url or "").lower()
            # Higher priority for company websites (not job boards)
            if 'linkedin.com' in url_lower:
                return 1  # Lower priority
            elif any(board in url_lower for board in ['indeed.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com']):
                return 2  # Medium priority
            else:
                return 3  # Highest priority (company websites, direct links)
        
        # Sort by priority (highest first), then by source diversity
        unique_jobs.sort(key=lambda j: (job_priority(j), j.source or ""), reverse=True)
        
        # Limit results
        unique_jobs = unique_jobs[:max_results]
        
        # Count by source
        source_counts = {}
        for job in unique_jobs:
            source = job.source or "unknown"
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"[COMPREHENSIVE] Total unique jobs found: {len(unique_jobs)}")
        print(f"[COMPREHENSIVE] Jobs by source: {source_counts}")
        print(f"[COMPREHENSIVE] Prioritized company website jobs over LinkedIn")
        return unique_jobs
    
    def _remove_duplicates(self, jobs: List[JobListing]) -> List[JobListing]:
        """Remove duplicate jobs based on title + company + URL"""
        seen = set()
        unique = []
        skipped = 0
        for job in jobs:
            if not job.title or not job.company:
                skipped += 1
                continue
            # Use URL as part of key to avoid false duplicates
            title_clean = job.title.lower().strip()
            company_clean = job.company.lower().strip()
            url_clean = job.url.lower().strip() if job.url else ""
            
            # Create key from title + company (URL optional for better matching)
            key = (title_clean, company_clean)
            url_key = url_clean[:50] if url_clean else ""  # Use first 50 chars of URL
            
            # Check if we've seen this exact job
            if key in seen:
                # If URL is different, might be same job on different sites - still count as unique
                if url_key and url_key not in [u[:50] for u in [j.url.lower()[:50] for j in unique if j.url]]:
                    # Different URL, might be different posting - include it
                    pass
                else:
                    skipped += 1
                    continue
            
            seen.add(key)
            unique.append(job)
        
        if skipped > 0:
            print(f"[COMPREHENSIVE] Removed {skipped} duplicates, kept {len(unique)} unique jobs")
        return unique
    
    def _search_indeed(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Indeed.com"""
        jobs = []
        try:
            # Indeed search URL
            location_param = f"&l={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.indeed.com/jobs?q={quote(query)}{location_param}&limit=50"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('div', {'data-jk': True})
                
                for card in job_cards[:max_results]:
                    try:
                        # Extract job ID
                        job_id = card.get('data-jk', '')
                        if not job_id:
                            continue
                        
                        # Extract title
                        title_elem = card.find('h2', class_='jobTitle') or card.find('a', {'data-jk': True})
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        # Extract company
                        company_elem = card.find('span', class_='companyName') or card.find('a', class_='companyName')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        # Extract location
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        # Extract description/snippet
                        snippet_elem = card.find('div', class_='job-snippet')
                        description = snippet_elem.get_text(strip=True)[:300] if snippet_elem else ""
                        
                        # Build URL
                        job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
                        
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
            print(f"[INDEED] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_linkedin(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search LinkedIn Jobs - with pagination to get more results"""
        jobs = []
        try:
            # LinkedIn search URL (public search) - try multiple pages
            location_param = f"&location={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            
            # Paginate through LinkedIn results to get more jobs
            pages_to_check = min(5, (max_results // 25) + 1)  # LinkedIn shows ~25 jobs per page
            print(f"[LINKEDIN] Checking {pages_to_check} pages for up to {max_results} jobs")
            
            for page_num in range(pages_to_check):
                if len(jobs) >= max_results:
                    break
                    
                url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}{location_param}&position=1&pageNum={page_num}"
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try multiple selectors for LinkedIn job cards
                        job_cards = (
                            soup.find_all('div', class_='job-search-card') or
                            soup.find_all('li', class_='job-result-card') or
                            soup.find_all('div', class_='base-card') or
                            soup.find_all('div', {'data-entity-urn': True}) or
                            soup.find_all('li', {'data-entity-urn': True}) or
                            soup.find_all('div', class_='jobs-search-results__list-item')
                        )
                        
                        if page_num == 0:
                            print(f"[LINKEDIN] Page {page_num + 1}: Found {len(job_cards)} potential job cards")
                        
                        if not job_cards:
                            # No more jobs on this page, stop paginating
                            break
                        
                        for card in job_cards:
                            if len(jobs) >= max_results:
                                break
                            
                            try:
                                # Extract title - try multiple selectors
                                title_elem = (
                                    card.find('h3', class_='base-search-card__title') or
                                    card.find('a', class_='job-result-card__listings-item') or
                                    card.find('h3', class_='base-search-card__full-link') or
                                    card.find('span', class_='sr-only') or
                                    card.find('h2') or
                                    card.find('h3') or
                                    card.find('a', {'data-tracking-control-name': True})
                                )
                                title = title_elem.get_text(strip=True) if title_elem else ""
                                
                                # If no title, try getting from link text
                                if not title or len(title) < 5:
                                    link_elem = card.find('a', href=True)
                                    if link_elem:
                                        title = link_elem.get_text(strip=True)
                                
                                if not title or len(title) < 5 or title.lower() in ['job title', 'company']:
                                    continue
                                
                                # Extract company - try multiple selectors
                                company_elem = (
                                    card.find('h4', class_='base-search-card__subtitle') or
                                    card.find('a', class_='job-result-card__company-name') or
                                    card.find('span', class_='job-result-card__company-name') or
                                    card.find('div', class_='job-result-card__company') or
                                    card.find('span', class_='job-result-card__company')
                                )
                                company = company_elem.get_text(strip=True) if company_elem else "Company"
                                
                                if company == "Company" or len(company) < 2:
                                    continue
                                
                                # Extract location - try multiple selectors
                                location_elem = (
                                    card.find('span', class_='job-search-card__location') or
                                    card.find('span', class_='job-result-card__location') or
                                    card.find('div', class_='job-result-card__location') or
                                    card.find('span', class_='job-result-card__metadata-item')
                                )
                                job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                                
                                # Extract URL - try multiple selectors
                                link_elem = card.find('a', href=True)
                                job_url = ""
                                if link_elem:
                                    href = link_elem.get('href', '')
                                    if href.startswith('/'):
                                        job_url = f"https://www.linkedin.com{href}"
                                    elif href.startswith('http'):
                                        job_url = href
                                
                                if not job_url or 'linkedin.com/jobs' not in job_url:
                                    continue
                                
                                # Extract description/snippet
                                snippet_elem = (
                                    card.find('p', class_='job-search-card__snippet') or
                                    card.find('div', class_='job-result-card__snippet') or
                                    card.find('p', class_='base-search-card__metadata')
                                )
                                description = snippet_elem.get_text(strip=True)[:300] if snippet_elem else f"Job opportunity at {company}. Click to view details."
                                
                                job = JobListing(
                                    title=title[:200],
                                    company=company[:100],
                                    location=job_location[:100],
                                    description=description,
                                    requirements=[],
                                    url=job_url,
                                    source="linkedin"
                                )
                                jobs.append(job)
                            except Exception as e:
                                print(f"[LINKEDIN] Error extracting job: {str(e)[:50]}")
                                continue
                        
                        # Small delay between pages to be respectful
                        if page_num < pages_to_check - 1:
                            time.sleep(1)
                        
                        print(f"[LINKEDIN] Page {page_num + 1}: Extracted {len(jobs)} total jobs so far")
                except Exception as e:
                    print(f"[LINKEDIN] Error on page {page_num + 1}: {str(e)[:50]}")
                    continue
                
                print(f"[LINKEDIN] Successfully extracted {len(jobs)} jobs from {pages_to_check} page(s)")
        except Exception as e:
            print(f"[LINKEDIN] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_glassdoor(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Glassdoor"""
        jobs = []
        try:
            location_param = f"&locT=C&locId={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={quote(query)}{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('li', class_='react-job-listing') or soup.find_all('div', {'data-test': 'job-listing'})
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('a', class_='jobLink') or card.find('h3')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('div', class_='employerName') or card.find('span', class_='employer')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('span', class_='location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = ""
                        if link_elem:
                            href = link_elem.get('href', '')
                            if href.startswith('/'):
                                job_url = f"https://www.glassdoor.com{href}"
                            else:
                                job_url = href
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="glassdoor"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[GLASSDOOR] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_monster(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Monster.com"""
        jobs = []
        try:
            location_param = f"&where={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.monster.com/jobs/search/?q={quote(query)}{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('section', class_='card-content') or soup.find_all('div', class_='card-apply-content')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='title') or card.find('a', class_='jobTitle')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('div', class_='company') or card.find('span', class_='company')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('div', class_='location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://www.monster.com{job_url}"
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="monster"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[MONSTER] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_ziprecruiter(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search ZipRecruiter"""
        jobs = []
        try:
            location_param = f"&location={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.ziprecruiter.com/jobs-search?search={quote(query)}{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('article', class_='job_result') or soup.find_all('div', class_='job_content')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='job_title') or card.find('a', class_='job_link')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('a', class_='company_name')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('div', class_='job_location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="ziprecruiter"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[ZIPRECRUITER] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_jobstreet(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search JobStreet (Asia)"""
        jobs = []
        try:
            location_param = f"&location={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=3&key={quote(query)}{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('article', class_='sx2jih0') or soup.find_all('div', class_='job-card')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h1', class_='sx2jih0') or card.find('a', class_='job-title')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('span', class_='sx2jih0') or card.find('a', class_='company-name')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('span', class_='location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://www.jobstreet.com.sg{job_url}"
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="jobstreet"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[JOBSTREET] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_reed(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Reed.co.uk (UK)"""
        jobs = []
        try:
            location_param = f"&location={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.reed.co.uk/jobs/{quote(query)}-jobs{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('article', class_='job-result') or soup.find_all('div', class_='job-result')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='job-result-heading') or card.find('a', class_='job-title')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('a', class_='gtmJobListingPostedBy')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('li', class_='job-location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://www.reed.co.uk{job_url}"
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="reed"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[REED] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_adzuna(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search Adzuna (Global)"""
        jobs = []
        try:
            location_param = f"&where={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.adzuna.com/search?q={quote(query)}{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job-result') or soup.find_all('article', class_='job-listing')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='job-title') or card.find('a', class_='job-link')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('span', class_='company')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('span', class_='location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="adzuna"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[ADZUNA] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_mycareersfuture(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search MyCareersFuture (Singapore)"""
        jobs = []
        try:
            url = f"https://www.mycareersfuture.gov.sg/search?search={quote(query)}&sortBy=relevancy&page=0"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('article', class_='card') or soup.find_all('div', class_='job-card')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h1', class_='card-title') or card.find('a', class_='job-title')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('p', class_='card-company') or card.find('span', class_='company')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('p', class_='card-location')
                        job_location = location_elem.get_text(strip=True) if location_elem else "Singapore"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://www.mycareersfuture.gov.sg{job_url}"
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="mycareersfuture"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[MYCAREERSFUTURE] Error: {str(e)[:80]}")
        
        return jobs
    
    def _search_jobsdb(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Search JobsDB (Asia)"""
        jobs = []
        try:
            location_param = f"&location={quote(location)}" if location and location.lower() not in ['worldwide', ''] else ""
            url = f"https://www.jobsdb.com/en-sg/search-jobs/{quote(query)}{location_param}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('article', class_='jobCard') or soup.find_all('div', class_='job-card')
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h1', class_='jobTitle') or card.find('a', class_='job-link')
                        title = title_elem.get_text(strip=True) if title_elem else "Job Title"
                        
                        company_elem = card.find('span', class_='company-name')
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        location_elem = card.find('span', class_='job-location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                        
                        link_elem = card.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""
                        if job_url and not job_url.startswith('http'):
                            job_url = f"https://www.jobsdb.com{job_url}"
                        
                        if not job_url:
                            continue
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Job at {company}",
                            requirements=[],
                            url=job_url,
                            source="jobsdb"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"[JOBSDB] Error: {str(e)[:80]}")
        
        return jobs
