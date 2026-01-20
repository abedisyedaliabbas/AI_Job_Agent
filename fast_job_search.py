"""
Fast Job Search - Quick and reliable job search with fallbacks
"""
from typing import List, Dict
from job_search import JobListing
import time
import re
from urllib.parse import quote


class FastJobSearch:
    """Fast job search with multiple strategies and fallbacks"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        }
    
    def search_jobs(self, keywords: List[str], location: str = "", max_results: int = 20) -> List[JobListing]:
        """Fast job search with multiple fallback strategies"""
        all_jobs = []
        query = " ".join(keywords[:3])  # Use top 3 keywords
        
        # Strategy 1: Try Indeed (fast, most reliable)
        try:
            jobs = self._search_indeed_fast(query, location, max_results)
            if jobs:
                all_jobs.extend(jobs)
                print(f"[FAST] Indeed: {len(jobs)} jobs")
        except Exception as e:
            print(f"[FAST] Indeed failed: {str(e)[:50]}")
        
        # Strategy 2: Only generate sample jobs if NO real jobs found (and only for testing)
        # REMOVED: Sample job generation - users should get real jobs or clear message
        # If no jobs found, return empty list - let users know they need to search manually
        if len(all_jobs) == 0:
            print(f"[FAST] No jobs found. Job boards may be blocking automated scraping.")
            print(f"[FAST] Users should search manually on job boards or use job URL extraction.")
        
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
    
    def _search_indeed_fast(self, query: str, location: str, max_results: int) -> List[JobListing]:
        """Fast Indeed search with minimal delay"""
        import requests
        from bs4 import BeautifulSoup
        import re
        
        jobs = []
        try:
            query_encoded = quote(query)
            domain = 'www.indeed.com'
            
            if location and location.lower() not in ['worldwide', '']:
                url = f"https://{domain}/jobs?q={query_encoded}&l={quote(location)}"
            else:
                url = f"https://{domain}/jobs?q={query_encoded}"
            
            # Fast request with shorter timeout
            response = requests.get(url, headers=self.headers, timeout=8, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find job listings
                job_elements = (
                    soup.find_all('div', {'data-jk': True}) or
                    soup.find_all('a', {'data-jk': True}) or
                    soup.find_all('div', class_=re.compile(r'job|card', re.I))
                )
                
                for elem in job_elements[:max_results]:
                    try:
                        # Extract title
                        title_elem = elem.find(['h2', 'a', 'span'], class_=re.compile(r'title|job', re.I))
                        title = title_elem.get_text(strip=True) if title_elem else None
                        
                        if not title:
                            title = elem.get('aria-label', '') or elem.get_text(strip=True)[:80]
                        
                        if not title or len(title) < 5:
                            continue
                        
                        # Extract company
                        company_elem = elem.find(['span', 'div', 'a'], class_=re.compile(r'company', re.I))
                        company = company_elem.get_text(strip=True) if company_elem else "Company"
                        
                        # Extract location
                        loc_elem = elem.find(['div', 'span'], class_=re.compile(r'location', re.I))
                        job_location = loc_elem.get_text(strip=True) if loc_elem else location or "Remote"
                        
                        # Extract URL
                        link = elem.find('a', href=True)
                        job_url = ""
                        if link:
                            job_url = link.get('href', '')
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://{domain}{job_url}"
                        
                        # Create job listing
                        job = JobListing(
                            title=title[:200],
                            company=company[:100],
                            location=job_location[:100],
                            description=f"Position for {query} in {job_location}",
                            requirements=[],
                            url=job_url or url,
                            source="indeed-fast"
                        )
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"Indeed fast search error: {str(e)[:100]}")
        
        return jobs
    
    def _generate_sample_jobs(self, keywords: List[str], location: str, count: int) -> List[JobListing]:
        """
        DEPRECATED: Sample job generation removed.
        This function is kept for backward compatibility but should not be called.
        Users should search manually or use real job URLs.
        """
        return []  # Return empty - no sample jobs
        
        # Clean keywords - remove empty, short, and generic ones
        generic_words = {'data', 'system', 'software', 'application', 'technology', 'service', 'work', 'experience', 'skills'}
        clean_keywords = [k for k in keywords if k and len(k) > 3 and k.lower() not in generic_words]
        
        if not clean_keywords:
            clean_keywords = ["researcher", "scientist"]
        
        primary_keyword = clean_keywords[0]
        
        # Use more natural job titles - avoid "Data Researcher" style titles
        # If keyword is technical, use it in title; otherwise use generic professional titles
        if len(primary_keyword) > 5 and primary_keyword.lower() not in generic_words:
            # Technical keyword - use it
            job_titles = [
                f"{primary_keyword.title()} Researcher",
                f"Senior {primary_keyword.title()} Scientist",
                f"{primary_keyword.title()} Specialist",
                f"{primary_keyword.title()} Engineer",
                f"Research Scientist - {primary_keyword.title()}",
            ]
        else:
            # Generic keyword - use professional titles with keyword in description
            job_titles = [
                "Research Scientist",
                "Senior Research Scientist",
                "Research Specialist",
                "Computational Scientist",
                "Research Engineer",  # Fixed: was "Research Enginer"
            ]
        
        companies = [
            "Tech Solutions Inc",
            "Global Innovations",
            "Digital Systems",
            "Advanced Technologies",
            "Innovative Solutions",
            "TechCorp",
            "Data Systems",
            "Cloud Services",
        ]
        
        locations_list = [location] if location and location != "Worldwide" else [
            "Singapore", "Remote", "United States", "United Kingdom"
        ]
        
        # Create more realistic job descriptions that include keywords
        for i in range(min(count, len(job_titles) * 2)):
            title = job_titles[i % len(job_titles)]
            # Clean title: fix common issues like "Programmingpython" -> "Python Programming"
            title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)  # Add space between camelCase
            title = re.sub(r'(\w+)\1+', r'\1', title)  # Remove duplicate words
            title = ' '.join(title.split())  # Normalize whitespace
            # Fix common malformed patterns
            title = title.replace('Programmingpython', 'Python Programming')
            title = title.replace('Programming Python', 'Python Programming')
            title = title.replace('Pythonpython', 'Python')
            title = title.replace('Enginer', 'Engineer')  # Fix typo
            
            company = companies[i % len(companies)]
            job_location = locations_list[i % len(locations_list)]
            
            # Create description that includes keywords naturally
            # Use all keywords, not just primary
            meaningful_keywords = [k for k in clean_keywords if len(k) > 3 and k.lower() not in generic_words]
            if meaningful_keywords:
                keyword_phrase = ", ".join(meaningful_keywords[:3])
                if len(meaningful_keywords) > 1:
                    description = f"We are seeking a {title.lower()} with expertise in {keyword_phrase}. The ideal candidate will have strong background in {', '.join(meaningful_keywords[:2])} and related technologies. This position offers excellent opportunities for professional growth and development."
                else:
                    description = f"We are seeking a {title.lower()} with expertise in {keyword_phrase}. The ideal candidate will have strong background in this field and related technologies. This position offers excellent opportunities for professional growth and development."
            else:
                description = f"We are seeking a {title.lower()} with relevant experience and expertise. The ideal candidate will have strong background in research and related technologies. This position offers excellent opportunities for professional growth and development."
            
            requirements = []
            if meaningful_keywords:
                requirements.append(f"Experience with {', '.join(meaningful_keywords[:2])}")
                if len(meaningful_keywords) > 1:
                    requirements.append(f"Strong background in {keyword_phrase}")
            requirements.append("Excellent communication skills")
            requirements.append("PhD or equivalent experience")
            
            # For sample jobs, use a placeholder URL that won't confuse users
            # Use a data URI or mark as sample
            job = JobListing(
                title=title,
                company=company,
                location=job_location,
                description=description,
                requirements=requirements,
                url=f"#sample-job-{i+1}",  # Use hash link instead of example.com
                source="sample-generated"
            )
            jobs.append(job)
        
        return jobs
