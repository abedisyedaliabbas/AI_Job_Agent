"""
AI-Powered Job Discovery - Uses ML and NLP to intelligently find jobs
Uses AI to discover company websites, extract job postings, and find opportunities
"""
from typing import List, Dict, Optional
from job_search import JobListing
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
import time
import re

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("[AI DISCOVERY] ML libraries not available. Using rule-based discovery.")


class AIJobDiscovery:
    """
    AI-powered job discovery that:
    1. Uses ML to understand job requirements semantically
    2. Discovers company websites using intelligent search
    3. Extracts job postings from company career pages
    4. Uses NLP to find relevant opportunities
    """
    
    def __init__(self):
        self.model = None
        if AI_AVAILABLE:
            try:
                print("[AI DISCOVERY] Loading ML model for intelligent job discovery...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[AI DISCOVERY] Model loaded successfully!")
            except Exception as e:
                print(f"[AI DISCOVERY] Error loading model: {e}")
                self.model = None
    
    def discover_company_websites(self, keywords: List[str], location: str = "") -> List[str]:
        """
        Use AI to discover company websites that might have job openings
        Returns list of company website URLs
        """
        company_urls = []
        
        # Build intelligent search queries
        query_parts = []
        for keyword in keywords[:3]:  # Top 3 keywords
            # Create semantic variations
            query_parts.append(f'"{keyword}" company careers')
            query_parts.append(f'"{keyword}" company jobs')
            query_parts.append(f'"{keyword}" hiring')
        
        if location and location.lower() not in ['worldwide', '']:
            location_part = f" in {location}"
        else:
            location_part = ""
        
        # Search for company websites
        for query_part in query_parts[:5]:  # Limit to 5 queries
            try:
                search_query = f"{query_part}{location_part} -site:linkedin.com -site:indeed.com -site:glassdoor.com"
                query_encoded = quote(search_query)
                url = f"https://www.google.com/search?q={query_encoded}&num=10"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find all links
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        
                        # Clean Google redirect URLs
                        if href.startswith('/url?q='):
                            href = href.split('/url?q=')[1].split('&')[0]
                        
                        if not href.startswith('http'):
                            continue
                        
                        # Check if it's a company website (not job board)
                        href_lower = href.lower()
                        job_boards = ['linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com']
                        if any(board in href_lower for board in job_boards):
                            continue
                        
                        # Check if it looks like a company website with careers/jobs
                        if any(path in href_lower for path in ['/careers', '/jobs', '/opportunities', '/join-us']):
                            if href not in company_urls:
                                company_urls.append(href)
                                print(f"[AI DISCOVERY] Found company website: {href}")
                
                time.sleep(1)  # Be respectful
            except Exception as e:
                print(f"[AI DISCOVERY] Error in company discovery: {e}")
                continue
        
        return company_urls[:20]  # Limit to 20 companies
    
    def extract_jobs_from_company_website(self, company_url: str, keywords: List[str]) -> List[JobListing]:
        """
        Use AI to extract job postings from a company website
        """
        jobs = []
        
        try:
            # Try to find careers/jobs page
            base_url = '/'.join(company_url.split('/')[:3])  # Get domain
            
            # Common career page paths
            career_paths = [
                '/careers',
                '/jobs',
                '/opportunities',
                '/join-us',
                '/careers/jobs',
                '/careers/open-positions'
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            for path in career_paths:
                try:
                    career_url = base_url + path
                    response = requests.get(career_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Use AI to find job listings on the page
                        # Look for common job listing patterns
                        job_links = soup.find_all('a', href=True)
                        
                        for link in job_links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            
                            # Make absolute URL
                            if href.startswith('/'):
                                href = base_url + href
                            elif not href.startswith('http'):
                                continue
                            
                            # Check if link looks like a job posting
                            href_lower = href.lower()
                            text_lower = link_text.lower()
                            
                            # Use AI to determine if this is a job posting
                            is_job_posting = self._is_job_posting_ai(href, link_text, keywords)
                            
                            if is_job_posting:
                                # Extract job details
                                title = link_text if link_text else self._extract_title_from_url(href)
                                
                                # Extract company name from URL
                                company = self._extract_company_from_url(company_url)
                                
                                job = JobListing(
                                    title=title[:200],
                                    company=company[:100],
                                    location="",  # Will be extracted if available
                                    description=f"Job opportunity at {company}. Click to view details.",
                                    requirements=[],
                                    url=href,
                                    source="company_website"
                                )
                                jobs.append(job)
                        
                        if jobs:
                            print(f"[AI DISCOVERY] Found {len(jobs)} jobs on {career_url}")
                            break  # Found jobs, stop trying other paths
                
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"[AI DISCOVERY] Error extracting from {company_url}: {e}")
        
        return jobs
    
    def _is_job_posting_ai(self, url: str, text: str, keywords: List[str]) -> bool:
        """
        Use AI to determine if a URL/text represents a job posting
        """
        if not self.model:
            return self._is_job_posting_rule_based(url, text, keywords)
        
        try:
            # Combine URL and text
            combined_text = f"{url} {text}".lower()
            
            # Check for job-related keywords
            job_keywords = [
                'job', 'career', 'position', 'opening', 'vacancy', 'opportunity',
                'hiring', 'recruit', 'employment', 'role', 'scientist', 'researcher',
                'engineer', 'developer', 'analyst'
            ]
            
            has_job_keyword = any(kw in combined_text for kw in job_keywords)
            has_job_path = any(path in url.lower() for path in ['/job/', '/jobs/', '/careers/', '/position/'])
            
            # Use ML to check semantic similarity with keywords
            if keywords and has_job_keyword:
                keyword_text = " ".join(keywords)
                combined_embedding = self.model.encode(combined_text, convert_to_numpy=True)
                keyword_embedding = self.model.encode(keyword_text, convert_to_numpy=True)
                
                similarity = cosine_similarity(
                    combined_embedding.reshape(1, -1),
                    keyword_embedding.reshape(1, -1)
                )[0][0]
                
                # If similarity is high or has job path, it's likely a job posting
                return similarity > 0.3 or has_job_path
            
            return has_job_keyword or has_job_path
        except:
            return self._is_job_posting_rule_based(url, text, keywords)
    
    def _is_job_posting_rule_based(self, url: str, text: str, keywords: List[str]) -> bool:
        """Rule-based fallback"""
        combined = f"{url} {text}".lower()
        
        job_keywords = ['job', 'career', 'position', 'opening', 'vacancy', 'opportunity', 'hiring']
        has_job_keyword = any(kw in combined for kw in job_keywords)
        has_job_path = any(path in url.lower() for path in ['/job/', '/jobs/', '/careers/'])
        
        return has_job_keyword or has_job_path
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract job title from URL"""
        try:
            from urllib.parse import unquote
            parsed = urlparse(url)
            path = unquote(parsed.path)
            
            if '/jobs/' in path or '/job/' in path:
                title = path.split('/jobs/')[-1].split('/job/')[-1].split('/')[0]
                title = title.replace('-', ' ').title()
                if len(title) > 5:
                    return title
        except:
            pass
        return "Job Opportunity"
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '').split('.')[0]
            if domain and len(domain) > 2:
                return domain.title()
        except:
            pass
        return "Company"
    
    def discover_jobs_ai(self, keywords: List[str], location: str = "", max_results: int = 50) -> List[JobListing]:
        """
        Main AI-powered job discovery method
        Uses ML to intelligently find jobs from company websites
        """
        all_jobs = []
        
        print(f"[AI DISCOVERY] Using AI/ML to discover jobs for: {keywords}")
        print(f"[AI DISCOVERY] Location: {location or 'Worldwide'}")
        
        # Step 1: Discover company websites
        print("[AI DISCOVERY] Step 1: Discovering company websites...")
        company_urls = self.discover_company_websites(keywords, location)
        print(f"[AI DISCOVERY] Found {len(company_urls)} company websites")
        
        # Step 2: Extract jobs from each company website
        print("[AI DISCOVERY] Step 2: Extracting jobs from company websites...")
        for company_url in company_urls[:10]:  # Limit to 10 companies
            try:
                jobs = self.extract_jobs_from_company_website(company_url, keywords)
                all_jobs.extend(jobs)
                print(f"[AI DISCOVERY] Extracted {len(jobs)} jobs from {company_url}")
                time.sleep(1)  # Be respectful
            except Exception as e:
                print(f"[AI DISCOVERY] Error processing {company_url}: {e}")
                continue
        
        # Step 3: Use semantic search to find more opportunities
        print("[AI DISCOVERY] Step 3: Using semantic search for additional opportunities...")
        semantic_jobs = self._semantic_job_search(keywords, location, max_results - len(all_jobs))
        all_jobs.extend(semantic_jobs)
        
        print(f"[AI DISCOVERY] Total jobs discovered: {len(all_jobs)}")
        return all_jobs[:max_results]
    
    def _semantic_job_search(self, keywords: List[str], location: str, max_results: int) -> List[JobListing]:
        """
        Use semantic search to find jobs based on meaning, not just keywords
        """
        jobs = []
        
        if not self.model or max_results <= 0:
            return jobs
        
        try:
            # Create semantic query
            query = " ".join(keywords)
            if location and location.lower() not in ['worldwide', '']:
                query += f" {location}"
            
            # Search with semantic variations
            semantic_queries = [
                f"{query} careers opportunities",
                f"{query} hiring positions",
                f"{query} job openings",
                f"{query} employment opportunities"
            ]
            
            for sem_query in semantic_queries[:3]:  # Top 3 variations
                try:
                    query_encoded = quote(f"{sem_query} -site:linkedin.com -site:indeed.com")
                    url = f"https://www.google.com/search?q={query_encoded}&num=10"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract results
                        results = soup.find_all('div', class_='g') or soup.find_all('div', {'data-ved': True})
                        
                        for result in results[:10]:
                            try:
                                link = result.find('a', href=True)
                                if not link:
                                    continue
                                
                                href = link.get('href', '')
                                if href.startswith('/url?q='):
                                    href = href.split('/url?q=')[1].split('&')[0]
                                
                                if not href.startswith('http') or 'linkedin.com' in href.lower():
                                    continue
                                
                                title = link.get_text(strip=True)
                                if not title or len(title) < 5:
                                    continue
                                
                                # Use ML to check if this is relevant
                                if self._is_relevant_ai(title, href, keywords):
                                    company = self._extract_company_from_url(href)
                                    job = JobListing(
                                        title=title[:200],
                                        company=company[:100],
                                        location=location or "",
                                        description=f"Job opportunity found via AI semantic search.",
                                        requirements=[],
                                        url=href,
                                        source="ai_semantic_search"
                                    )
                                    jobs.append(job)
                                    
                                    if len(jobs) >= max_results:
                                        break
                            except:
                                continue
                        
                        if len(jobs) >= max_results:
                            break
                    
                    time.sleep(1)
                except:
                    continue
        
        except Exception as e:
            print(f"[AI DISCOVERY] Semantic search error: {e}")
        
        return jobs
    
    def _is_relevant_ai(self, title: str, url: str, keywords: List[str]) -> bool:
        """Use ML to check if a job is relevant to keywords"""
        if not self.model or not keywords:
            return True
        
        try:
            combined = f"{title} {url}".lower()
            keyword_text = " ".join(keywords).lower()
            
            combined_embedding = self.model.encode(combined, convert_to_numpy=True)
            keyword_embedding = self.model.encode(keyword_text, convert_to_numpy=True)
            
            similarity = cosine_similarity(
                combined_embedding.reshape(1, -1),
                keyword_embedding.reshape(1, -1)
            )[0][0]
            
            return similarity > 0.4  # Threshold for relevance
        except:
            return True  # Default to relevant if ML fails
