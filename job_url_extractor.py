"""
Job URL Extractor - Extracts job details from job board URLs
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
from urllib.parse import urlparse
import time


class JobURLExtractor:
    """Extract job details from various job board URLs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def extract_from_url(self, url: str) -> Dict:
        """Extract job details from a job board URL"""
        try:
            # Determine job board type
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            if 'linkedin.com' in domain:
                return self._extract_linkedin(url)
            elif 'indeed.com' in domain:
                return self._extract_indeed(url)
            elif 'jobstreet' in domain:
                return self._extract_jobstreet(url)
            elif 'glassdoor' in domain:
                return self._extract_glassdoor(url)
            elif 'mycareersfuture' in domain:
                return self._extract_mycareersfuture(url)
            elif 'jobsdb' in domain:
                return self._extract_jobsdb(url)
            else:
                # Generic extraction
                return self._extract_generic(url)
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error extracting job details: {str(e)}',
                'url': url
            }
    
    def _extract_linkedin(self, url: str) -> Dict:
        """Extract from LinkedIn job posting"""
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # LinkedIn job structure
            title_elem = soup.find('h1', class_=re.compile(r'job-title|top-card-layout__title'))
            if not title_elem:
                title_elem = soup.find('h1')
            
            company_elem = soup.find('a', class_=re.compile(r'job-card-container__company-name|topcard__org-name-link'))
            if not company_elem:
                company_elem = soup.find('span', class_=re.compile(r'company'))
            
            location_elem = soup.find('span', class_=re.compile(r'job-card-container__metadata-item|topcard__flavor'))
            
            desc_elem = soup.find('div', class_=re.compile(r'description__text|show-more-less-html__markup'))
            if not desc_elem:
                desc_elem = soup.find('div', {'id': re.compile(r'job-details|description')})
            
            job_data = {
                'success': True,
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'company': company_elem.get_text(strip=True) if company_elem else '',
                'location': location_elem.get_text(strip=True) if location_elem else '',
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'url': url,
                'source': 'linkedin'
            }
            
            return job_data
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_indeed(self, url: str) -> Dict:
        """Extract from Indeed job posting"""
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_elem = soup.find('h1', class_=re.compile(r'jobsearch-JobInfoHeader-title'))
            company_elem = soup.find('div', class_=re.compile(r'jobsearch-InlineCompanyRating'))
            location_elem = soup.find('div', class_=re.compile(r'jobsearch-JobInfoHeader-subtitle'))
            desc_elem = soup.find('div', {'id': 'jobDescriptionText'})
            
            job_data = {
                'success': True,
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'company': company_elem.find('a').get_text(strip=True) if company_elem and company_elem.find('a') else '',
                'location': location_elem.get_text(strip=True) if location_elem else '',
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'url': url,
                'source': 'indeed'
            }
            
            return job_data
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_jobstreet(self, url: str) -> Dict:
        """Extract from JobStreet job posting"""
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_elem = soup.find('h1', class_=re.compile(r'job-title'))
            company_elem = soup.find('a', class_=re.compile(r'company-name'))
            location_elem = soup.find('span', class_=re.compile(r'location'))
            desc_elem = soup.find('div', class_=re.compile(r'job-description'))
            
            job_data = {
                'success': True,
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'company': company_elem.get_text(strip=True) if company_elem else '',
                'location': location_elem.get_text(strip=True) if location_elem else '',
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'url': url,
                'source': 'jobstreet'
            }
            
            return job_data
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_glassdoor(self, url: str) -> Dict:
        """Extract from Glassdoor job posting"""
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_elem = soup.find('h2', class_=re.compile(r'jobTitle'))
            company_elem = soup.find('span', class_=re.compile(r'employerName'))
            location_elem = soup.find('div', class_=re.compile(r'location'))
            desc_elem = soup.find('div', class_=re.compile(r'jobDescriptionContent'))
            
            job_data = {
                'success': True,
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'company': company_elem.get_text(strip=True) if company_elem else '',
                'location': location_elem.get_text(strip=True) if location_elem else '',
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'url': url,
                'source': 'glassdoor'
            }
            
            return job_data
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_mycareersfuture(self, url: str) -> Dict:
        """Extract from MyCareersFuture job posting"""
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_elem = soup.find('h1', class_=re.compile(r'job-title'))
            company_elem = soup.find('a', class_=re.compile(r'company'))
            location_elem = soup.find('span', class_=re.compile(r'location'))
            desc_elem = soup.find('div', class_=re.compile(r'description'))
            
            job_data = {
                'success': True,
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'company': company_elem.get_text(strip=True) if company_elem else '',
                'location': location_elem.get_text(strip=True) if location_elem else '',
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'url': url,
                'source': 'mycareersfuture'
            }
            
            return job_data
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_jobsdb(self, url: str) -> Dict:
        """Extract from JobsDB job posting"""
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_elem = soup.find('h1')
            company_elem = soup.find('a', class_=re.compile(r'company'))
            location_elem = soup.find('span', class_=re.compile(r'location'))
            desc_elem = soup.find('div', class_=re.compile(r'job-description'))
            
            job_data = {
                'success': True,
                'title': title_elem.get_text(strip=True) if title_elem else '',
                'company': company_elem.get_text(strip=True) if company_elem else '',
                'location': location_elem.get_text(strip=True) if location_elem else '',
                'description': desc_elem.get_text(strip=True) if desc_elem else '',
                'url': url,
                'source': 'jobsdb'
            }
            
            return job_data
        
        except Exception as e:
            return {'success': False, 'error': str(e), 'url': url}
    
    def _extract_generic(self, url: str) -> Dict:
        """Generic extraction for unknown job boards"""
        try:
            time.sleep(1)
            response = requests.get(url, headers=self.headers, timeout=15, allow_redirects=True)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'url': url}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try multiple patterns for title
            title_elem = (soup.find('h1') or 
                         soup.find('h2', class_=re.compile(r'title|job-title|position', re.I)) or
                         soup.find('div', class_=re.compile(r'title|job-title', re.I)) or
                         soup.find('span', class_=re.compile(r'title|job-title', re.I)))
            
            # Try multiple patterns for company
            company_elem = (soup.find('a', class_=re.compile(r'company|employer', re.I)) or
                           soup.find('span', class_=re.compile(r'company|employer', re.I)) or
                           soup.find('div', class_=re.compile(r'company|employer', re.I)) or
                           soup.find('h3', class_=re.compile(r'company', re.I)))
            
            # Try multiple patterns for location
            location_elem = (soup.find('span', class_=re.compile(r'location|place|city', re.I)) or
                            soup.find('div', class_=re.compile(r'location|place', re.I)) or
                            soup.find('li', class_=re.compile(r'location', re.I)))
            
            # Try multiple patterns for description
            desc_elem = (soup.find('div', class_=re.compile(r'description|content|details|job-description', re.I)) or
                        soup.find('section', class_=re.compile(r'description|content', re.I)) or
                        soup.find('div', {'id': re.compile(r'description|content|details', re.I)}) or
                        soup.find('article'))
            
            # If no description found, try to get main content
            if not desc_elem or len(desc_elem.get_text(strip=True)) < 100:
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'main|content', re.I))
                if main_content:
                    desc_elem = main_content
            
            title = title_elem.get_text(strip=True) if title_elem else ''
            company = company_elem.get_text(strip=True) if company_elem else ''
            location = location_elem.get_text(strip=True) if location_elem else ''
            description = desc_elem.get_text(strip=True, separator='\n') if desc_elem else ''
            
            # Clean up description
            if description:
                # Remove excessive whitespace
                description = re.sub(r'\n\s*\n\s*\n+', '\n\n', description)
                # Limit length
                if len(description) > 5000:
                    description = description[:5000] + '...'
            
            job_data = {
                'success': True,
                'title': title,
                'company': company,
                'location': location or 'Singapore',
                'description': description,
                'url': url,
                'source': 'generic'
            }
            
            return job_data
        
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Network error: {str(e)}', 'url': url}
        except Exception as e:
            return {'success': False, 'error': f'Extraction error: {str(e)}', 'url': url}
    
    def extract_requirements(self, description: str) -> list:
        """Extract requirements from job description"""
        requirements = []
        
        # Look for requirements section
        req_patterns = [
            r'requirements?:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'qualifications?:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'must have:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
            r'essential:?\s*(.*?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            if matches:
                req_text = matches[0]
                # Split by bullets or newlines
                reqs = re.split(r'[•\-\*]\s*|\n\s*\d+\.', req_text)
                requirements.extend([r.strip() for r in reqs if r.strip() and len(r.strip()) > 10])
                break
        
        # If no requirements section found, look for bullet points
        if not requirements:
            bullets = re.findall(r'[•\-\*]\s*(.+?)(?:\n|$)', description)
            requirements = [b.strip() for b in bullets if len(b.strip()) > 10][:10]
        
        return requirements[:10]  # Limit to 10 requirements
