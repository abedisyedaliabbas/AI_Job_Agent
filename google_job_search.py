"""
Google Job Search - Free and accessible job search using Google
Searches Google for jobs across multiple job boards
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from job_search import JobListing
from urllib.parse import quote, urlparse
import time
import re


class GoogleJobSearch:
    """Search for jobs using Google - free and accessible"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def search(self, keywords: List[str], location: str = "", max_results: int = 20) -> List[JobListing]:
        """Search Google for jobs"""
        all_jobs = []
        query = " ".join(keywords[:3])  # Use top 3 keywords
        
        # Clean keywords - remove trailing commas and clean up
        query = query.replace(',', ' ').strip()
        
        # Build Google search query
        search_query = f"{query} jobs"
        if location and location.lower() not in ['worldwide', '']:
            search_query += f" in {location}"
        
        print(f"[GOOGLE] Searching: '{search_query}'")
        
        # Try multiple search strategies
        strategies = [
            self._search_google_direct,
            self._search_google_with_sites,
        ]
        
        for strategy in strategies:
            try:
                jobs = strategy(search_query, location, max_results)
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"[GOOGLE] Found {len(jobs)} jobs using {strategy.__name__}")
                    if len(all_jobs) >= max_results:
                        break
                time.sleep(1)  # Be respectful
            except Exception as e:
                print(f"[GOOGLE] {strategy.__name__} failed: {str(e)[:80]}")
                import traceback
                traceback.print_exc()
                continue
        
        # If no jobs found, try one more time with different query
        if len(all_jobs) == 0:
            print(f"[GOOGLE] No jobs found via scraping. Trying alternative search strategy...")
            # Try with simpler query
            simple_query = f"{query} hiring"
            try:
                alt_jobs = self._search_google_direct(simple_query, location, max_results)
                if alt_jobs:
                    all_jobs.extend(alt_jobs)
                    print(f"[GOOGLE] Found {len(alt_jobs)} jobs with alternative query")
            except:
                pass
        
        # DO NOT generate search URLs - only return actual jobs
        # If still no jobs, return empty list (user can search manually)
        if len(all_jobs) == 0:
            print(f"[GOOGLE] No actual jobs found. Returning empty list.")
        
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
    
    def _search_google_direct(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Direct Google search for jobs"""
        jobs = []
        try:
            # Build comprehensive job search query - prioritize company websites
            # Use "site:" operator to find jobs on company websites (not job boards)
            search_terms = f"{query} job opening position hiring"
            if location and location.lower() not in ['worldwide', '']:
                search_terms += f" {location}"
            
            # Exclude job boards to prioritize company websites
            exclude_boards = "-site:linkedin.com -site:indeed.com -site:glassdoor.com -site:monster.com"
            search_terms = f"{search_terms} {exclude_boards}"
            
            query_encoded = quote(search_terms)
            # Use regular web search (not news) for better job results
            url = f"https://www.google.com/search?q={query_encoded}&num=20"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors for Google search results - more comprehensive
                results = []
                # Try different selectors (avoid regex in dict for BeautifulSoup compatibility)
                selectors = [
                    ('div', {'class': 'g'}),
                    ('div', {'data-ved': True}),
                    ('div', {'class': 'tF2Cxc'}),
                    ('div', {'class': 'yuRUbf'}),
                    ('div', {'class': 'MjjYud'}),
                    ('div', {'class': 'hlcw0c'}),
                ]
                
                for tag, attrs in selectors:
                    try:
                        found = soup.find_all(tag, attrs)
                        if found:
                            results.extend(found)
                            print(f"[GOOGLE] Found {len(found)} results using selector: {tag}")
                            if len(results) >= 20:  # Enough results
                                break
                    except Exception as e:
                        print(f"[GOOGLE] Selector error: {e}")
                        continue
                
                # Remove duplicates
                seen = set()
                unique_results = []
                for r in results:
                    r_id = id(r)
                    if r_id not in seen:
                        seen.add(r_id)
                        unique_results.append(r)
                results = unique_results
                
                # If still no results, try finding any links that look like job postings
                if not results:
                    all_links = soup.find_all('a', href=True)
                    print(f"[GOOGLE] Fallback: Found {len(all_links)} total links, filtering for job boards...")
                    
                    # Filter to job board domains
                    job_board_domains = [
                        'indeed.com', 'linkedin.com/jobs', 'glassdoor.com', 'monster.com',
                        'ziprecruiter.com', 'jobstreet.com', 'mycareersfuture.gov.sg',
                        'reed.co.uk', 'adzuna.com', 'smartrecruiters.com', 'greenhouse.io',
                        'lever.co', 'workday.com'
                    ]
                    
                    # Process links directly and create JobListing objects
                    for link in all_links[:max_results * 2]:  # Check more links
                        try:
                            href = link.get('href', '')
                            # Clean Google redirect URLs
                            if href.startswith('/url?q='):
                                href = href.split('/url?q=')[1].split('&')[0]
                            elif href.startswith('/search?') or 'google.com' in href:
                                continue
                            
                            if not href.startswith('http'):
                                continue
                            
                            # Check if it's a job board link
                            href_lower = href.lower()
                            is_job_board = any(domain in href_lower for domain in job_board_domains)
                            has_job_path = '/job' in href_lower or '/jobs' in href_lower
                            
                            if is_job_board or has_job_path:
                                # Decode URL
                                try:
                                    from urllib.parse import unquote
                                    href = unquote(href)
                                except:
                                    pass
                                
                                # Extract title from link text or URL
                                link_text = link.get_text(strip=True)
                                title = link_text[:200] if link_text and len(link_text) > 5 else "Job Opportunity"
                                
                                # Try to extract from URL path
                                if title == "Job Opportunity" or len(title) < 10:
                                    try:
                                        from urllib.parse import urlparse, unquote
                                        parsed = urlparse(href)
                                        path = unquote(parsed.path)
                                        if '/jobs/' in path or '/job/' in path:
                                            title = path.split('/jobs/')[-1].split('/job/')[-1].split('/')[0].replace('-', ' ').title()
                                            if len(title) < 5:
                                                title = "Job Opportunity"
                                    except:
                                        pass
                                
                                # Extract company from URL domain
                                company = "Company"
                                try:
                                    from urllib.parse import urlparse
                                    parsed = urlparse(href)
                                    domain = parsed.netloc.replace('www.', '').split('.')[0]
                                    if domain and len(domain) > 2:
                                        company = domain.title()
                                except:
                                    pass
                                
                                # Extract location from query or use default
                                job_location = location or "Remote"
                                
                                # Create job listing directly
                                job = JobListing(
                                    title=title[:200],
                                    company=company[:100],
                                    location=job_location[:100],
                                    description=f"Job opportunity found on {company}. Click to view details.",
                                    requirements=[],
                                    url=href,
                                    source="google"
                                )
                                jobs.append(job)
                                
                                if len(jobs) >= max_results:
                                    break
                        except Exception as e:
                            continue
                    
                    if jobs:
                        print(f"[GOOGLE] Extracted {len(jobs)} jobs from job board links")
                        return jobs[:max_results]
                    
                    # If still no results, continue with empty results list
                    results = []
                
                for result in results[:max_results]:
                    try:
                        # Extract link - handle both result divs and direct links
                        link_elem = result.find('a', href=True) if hasattr(result, 'find') else result
                        if not link_elem:
                            # If result is already a link, use it directly
                            if hasattr(result, 'href'):
                                job_url = result.href
                                link_elem = result
                            else:
                                continue
                        else:
                            job_url = link_elem.get('href', '')
                        
                        # Clean Google redirect URLs
                        if job_url.startswith('/url?q='):
                            job_url = job_url.split('/url?q=')[1].split('&')[0]
                        elif job_url.startswith('/search?') or 'google.com/search' in job_url:
                            continue  # Skip internal Google links
                        
                        # Must be a valid URL
                        if not job_url.startswith('http'):
                            continue
                        
                        # Extract title - try multiple selectors
                        title_elem = None
                        if hasattr(result, 'find'):
                            title_elem = (
                                result.find('h3') or
                                result.find('h2') or
                                result.find('a', class_='LC20lb') or
                                result.find('span', class_='LC20lb')
                            )
                        
                        if not title_elem:
                            # Try getting text from link
                            if hasattr(link_elem, 'get_text'):
                                title = link_elem.get_text(strip=True)
                            elif hasattr(link_elem, 'text'):
                                title = link_elem.text.strip()
                            elif isinstance(link_elem, str):
                                title = link_elem.strip()
                            else:
                                title = str(link_elem).strip()
                        else:
                            title = title_elem.get_text(strip=True) if title_elem else ""
                        
                        if not title or len(title) < 5:
                            # Try extracting from URL as last resort
                            try:
                                from urllib.parse import urlparse, unquote
                                parsed = urlparse(job_url)
                                path = unquote(parsed.path)
                                # Extract job title from URL path (common pattern: /jobs/job-title)
                                if '/jobs/' in path or '/job/' in path:
                                    title = path.split('/jobs/')[-1].split('/job/')[-1].split('/')[0].replace('-', ' ').title()
                                    if len(title) < 5:
                                        title = "Job Opportunity"
                            except:
                                title = "Job Opportunity"
                        
                        if not title or len(title) < 5:
                            continue
                        
                        # Less strict filtering - accept results from job board domains even if title doesn't have job keywords
                        title_lower = title.lower()
                        url_lower = job_url.lower()
                        is_job_board = any(domain in url_lower for domain in [
                            'indeed.com', 'linkedin.com/jobs', 'glassdoor.com', 'monster.com', 
                            'ziprecruiter.com', 'jobstreet.com', 'mycareersfuture.gov.sg', 
                            'reed.co.uk', 'adzuna.com', 'smartrecruiters.com', 'greenhouse.io',
                            'lever.co', 'workday.com'
                        ])
                        
                        # Accept if: has job keywords OR is from job board OR URL contains /job
                        has_job_keyword = any(word in title_lower for word in [
                            'job', 'career', 'hiring', 'position', 'opening', 'vacancy', 
                            'opportunity', 'recruit', 'employment', 'role'
                        ])
                        
                        if not (has_job_keyword or is_job_board or '/job' in url_lower or '/jobs' in url_lower):
                            continue
                        
                        # Clean Google redirect URLs
                        if job_url.startswith('/url?q='):
                            job_url = job_url.split('/url?q=')[1].split('&')[0]
                        elif job_url.startswith('/search?'):
                            continue  # Skip internal Google links
                        
                        # Decode URL
                        try:
                            from urllib.parse import unquote
                            job_url = unquote(job_url)
                        except:
                            pass
                        
                        # Extract snippet/description
                        snippet_elem = (
                            result.find('span', class_='aCOpRe') or
                            result.find('div', class_='VwiC3b') or
                            result.find('span', class_='st') or
                            result.find('div', class_='s')
                        )
                        description = snippet_elem.get_text(strip=True)[:200] if snippet_elem else f"Job opportunity for {query}"
                        
                        # Extract company from title or URL
                        company = "Company"
                        # Try to extract from title
                        if ' - ' in title:
                            parts = title.split(' - ')
                            if len(parts) > 1:
                                company = parts[-1].strip()
                        elif ' at ' in title_lower:
                            parts = title_lower.split(' at ')
                            if len(parts) > 1:
                                company = parts[-1].strip().title()
                        elif ' | ' in title:
                            parts = title.split(' | ')
                            if len(parts) > 1:
                                company = parts[-1].strip()
                        
                        # Try to extract from URL domain
                        if company == "Company":
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(job_url)
                                domain = parsed.netloc.replace('www.', '').split('.')[0]
                                if domain and len(domain) > 2:
                                    company = domain.title()
                            except:
                                pass
                        
                        # Extract location
                        job_location = location or "Remote"
                        if snippet_elem:
                            snippet_text = snippet_elem.get_text(strip=True).lower()
                            # Look for location in snippet
                            common_locations = ['singapore', 'usa', 'uk', 'australia', 'canada', 'germany', 'france']
                            for loc in common_locations:
                                if loc in snippet_text:
                                    job_location = loc.title()
                                    break
                        
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=description,
                            requirements=[],
                            url=job_url,
                            source="google"
                        )
                        jobs.append(job)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Google direct search error: {str(e)[:100]}")
        
        return jobs
    
    def _search_google_with_sites(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Google search with site filters for job boards"""
        jobs = []
        try:
            # Search with site filters
            job_sites = ["indeed.com", "linkedin.com/jobs", "glassdoor.com"]
            
            for site in job_sites:
                try:
                    site_query = f"{query} site:{site}"
                    query_encoded = quote(site_query)
                    url = f"https://www.google.com/search?q={query_encoded}&num=10"
                    
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        results = soup.find_all('div', class_='g') or soup.find_all('div', {'data-ved': True})
                        
                        for result in results[:max_results // len(job_sites)]:
                            try:
                                title_elem = result.find('h3')
                                if not title_elem:
                                    continue
                                title = title_elem.get_text(strip=True)
                                
                                link_elem = result.find('a', href=True)
                                if not link_elem:
                                    continue
                                job_url = link_elem.get('href', '')
                                if job_url.startswith('/url?q='):
                                    job_url = job_url.split('/url?q=')[1].split('&')[0]
                                
                                snippet_elem = result.find('span', class_='aCOpRe') or result.find('div', class_='VwiC3b')
                                description = snippet_elem.get_text(strip=True)[:200] if snippet_elem else f"Job at {site}"
                                
                                # Extract company
                                company = site.split('.')[0].title()
                                if ' - ' in title:
                                    parts = title.split(' - ')
                                    if len(parts) > 1:
                                        company = parts[-1].strip()
                                
                                job = JobListing(
                                    title=title[:200],
                                    company=company[:100],
                                    location=location or "Remote",
                                    description=description,
                                    requirements=[],
                                    url=job_url,
                                    source=f"google-{site}"
                                )
                                jobs.append(job)
                            except:
                                continue
                    
                    time.sleep(0.5)  # Rate limiting
                except:
                    continue
        except Exception as e:
            print(f"Google site search error: {str(e)[:100]}")
        
        return jobs
    
    def _generate_search_urls(self, keywords: List[str], location: str, max_results: int) -> List[JobListing]:
        """Generate job search URLs when scraping fails - users can visit these manually"""
        jobs = []
        query = " ".join(keywords[:3])
        
        # Generate search URLs for popular job boards
        job_boards = [
            {
                'name': 'Indeed',
                'url': f"https://www.indeed.com/jobs?q={quote(query)}" + (f"&l={quote(location)}" if location and location.lower() != 'worldwide' else ""),
                'location': location or 'Worldwide'
            },
            {
                'name': 'LinkedIn Jobs',
                'url': f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}" + (f"&location={quote(location)}" if location and location.lower() != 'worldwide' else ""),
                'location': location or 'Worldwide'
            },
            {
                'name': 'Glassdoor',
                'url': f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={quote(query)}" + (f"&locT=C&locId={quote(location)}" if location and location.lower() != 'worldwide' else ""),
                'location': location or 'Worldwide'
            },
            {
                'name': 'Google Jobs',
                'url': f"https://www.google.com/search?q={quote(query + ' jobs')}" + (f"+{quote(location)}" if location and location.lower() != 'worldwide' else ""),
                'location': location or 'Worldwide'
            }
        ]
        
        # Add location-specific boards
        if location and 'singapore' in location.lower():
            job_boards.append({
                'name': 'JobStreet Singapore',
                'url': f"https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=3&key={quote(query)}",
                'location': 'Singapore'
            })
            job_boards.append({
                'name': 'MyCareersFuture',
                'url': f"https://www.mycareersfuture.gov.sg/search?search={quote(query)}",
                'location': 'Singapore'
            })
        
        # Create JobListing objects for these search URLs
        for i, board in enumerate(job_boards[:max_results]):
            job = JobListing(
                title=f"Search: {query}",
                company=board['name'],
                location=board['location'],
                description=f"Click to search for '{query}' jobs on {board['name']}. This is a search link - visit to see actual job listings.",
                requirements=[],
                url=board['url'],
                source=f"search-url-{board['name'].lower().replace(' ', '-')}"
            )
            jobs.append(job)
            print(f"[GOOGLE] Generated search URL: {board['name']}")
        
        return jobs
    
    def _extract_job_from_url(self, url: str) -> dict:
        """Try to extract job details from URL"""
        try:
            # Parse common job board URLs
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Indeed
            if 'indeed.com' in domain:
                if '/viewjob' in url or '/jobs/view' in url:
                    return {'source': 'indeed', 'url': url}
            
            # LinkedIn
            if 'linkedin.com' in domain and '/jobs/view' in url:
                return {'source': 'linkedin', 'url': url}
            
            # Glassdoor
            if 'glassdoor.com' in domain and '/Job/' in url:
                return {'source': 'glassdoor', 'url': url}
            
            return {'source': 'google', 'url': url}
        except:
            return {'source': 'google', 'url': url}
