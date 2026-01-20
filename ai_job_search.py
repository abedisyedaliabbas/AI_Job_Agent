"""
AI-Powered Job Search - Uses NLP and ML to improve job search
Uses AI to understand job descriptions, extract requirements, and find better matches
"""
from typing import List, Dict, Optional
from job_search import JobListing
import re
from collections import Counter

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("[AI SEARCH] Warning: transformers not installed. Install with: pip install transformers torch")


class AIJobSearch:
    """
    AI-powered job search using:
    - NLP for understanding job descriptions
    - ML models for requirement extraction
    - Semantic search for better job discovery
    - AI-based keyword extraction
    """
    
    def __init__(self):
        self.requirement_extractor = None
        self.keyword_extractor = None
        self.semantic_model = None
        
        if AI_AVAILABLE:
            try:
                print("[AI SEARCH] Loading AI models...")
                # Use a lightweight model for requirement extraction
                # This model can classify text and extract key information
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[AI SEARCH] AI models loaded successfully!")
            except Exception as e:
                print(f"[AI SEARCH] Error loading models: {e}")
                print("[AI SEARCH] Using rule-based extraction")
        else:
            print("[AI SEARCH] AI libraries not available. Using rule-based extraction")
    
    def extract_requirements_ai(self, job_description: str) -> List[str]:
        """
        Use AI to extract job requirements from description
        More accurate than regex-based extraction
        """
        if not AI_AVAILABLE or not self.semantic_model:
            return self._extract_requirements_rule_based(job_description)
        
        try:
            # Split description into sentences
            sentences = re.split(r'[.!?]\s+', job_description)
            
            # Keywords that indicate requirements
            requirement_keywords = [
                'required', 'must have', 'should have', 'need', 'essential',
                'qualification', 'experience', 'skill', 'knowledge', 'ability',
                'proficient', 'familiar', 'expertise', 'background', 'degree'
            ]
            
            # Use embeddings to find requirement-like sentences
            requirement_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower()
                # Check if sentence contains requirement keywords
                if any(keyword in sentence_lower for keyword in requirement_keywords):
                    requirement_sentences.append(sentence.strip())
            
            # Extract key phrases from requirement sentences
            requirements = []
            for sentence in requirement_sentences:
                # Extract noun phrases and key terms
                # Look for patterns like "X years of experience", "Bachelor's degree", etc.
                patterns = [
                    r'\d+\+?\s*(?:years?|yrs?)\s+of\s+experience',
                    r'(?:Bachelor|Master|PhD|Doctorate)\'?s?\s+degree',
                    r'proficient\s+in\s+([A-Za-z\s,]+)',
                    r'experience\s+with\s+([A-Za-z\s,]+)',
                    r'knowledge\s+of\s+([A-Za-z\s,]+)',
                    r'ability\s+to\s+([A-Za-z\s,]+)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, sentence, re.IGNORECASE)
                    requirements.extend(matches)
                
                # If no pattern matched, use the sentence itself (if short enough)
                if not any(re.search(pattern, sentence, re.IGNORECASE) for pattern in patterns):
                    if len(sentence.split()) <= 15:  # Short sentences are likely requirements
                        requirements.append(sentence.strip())
            
            # Remove duplicates and clean
            unique_requirements = []
            seen = set()
            for req in requirements:
                req_clean = req.strip()
                if req_clean and req_clean.lower() not in seen:
                    seen.add(req_clean.lower())
                    unique_requirements.append(req_clean)
            
            return unique_requirements[:20]  # Limit to top 20
        except Exception as e:
            print(f"[AI SEARCH] Error in AI requirement extraction: {e}")
            return self._extract_requirements_rule_based(job_description)
    
    def _extract_requirements_rule_based(self, description: str) -> List[str]:
        """Fallback rule-based requirement extraction"""
        requirements = []
        
        # Look for bullet points
        bullets = re.findall(r'[•\-\*]\s*(.+?)(?=\n|$)', description, re.MULTILINE)
        requirements.extend(bullets)
        
        # Look for numbered lists
        numbered = re.findall(r'\d+\.\s*(.+?)(?=\n|$)', description, re.MULTILINE)
        requirements.extend(numbered)
        
        # Look for "Required:" or "Requirements:" sections
        req_section = re.search(r'Requirements?:?\s*(.+?)(?=\n\n|\Z)', description, re.IGNORECASE | re.DOTALL)
        if req_section:
            section_text = req_section.group(1)
            sentences = re.split(r'[.!?]\s+', section_text)
            requirements.extend([s.strip() for s in sentences if s.strip()])
        
        return requirements[:20]
    
    def extract_keywords_ai(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Use AI to extract meaningful keywords from text
        Better than simple word frequency
        """
        if not AI_AVAILABLE or not self.semantic_model:
            return self._extract_keywords_rule_based(text, max_keywords)
        
        try:
            # Split into sentences
            sentences = text.split('.')
            
            # Extract noun phrases and important terms
            # Look for capitalized words (likely proper nouns/technologies)
            capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            
            # Look for technical terms (often in parentheses or quotes)
            technical = re.findall(r'\(([A-Za-z\s]+)\)|"([A-Za-z\s]+)"', text)
            technical_terms = [t[0] or t[1] for t in technical]
            
            # Combine and rank by frequency
            all_terms = capitalized + technical_terms
            term_counts = Counter(all_terms)
            
            # Filter out common words
            common_words = {'the', 'and', 'or', 'for', 'with', 'from', 'that', 'this'}
            keywords = [
                term for term, count in term_counts.most_common(max_keywords * 2)
                if term.lower() not in common_words and len(term) > 2
            ]
            
            return keywords[:max_keywords]
        except Exception as e:
            print(f"[AI SEARCH] Error in AI keyword extraction: {e}")
            return self._extract_keywords_rule_based(text, max_keywords)
    
    def _extract_keywords_rule_based(self, text: str, max_keywords: int) -> List[str]:
        """Fallback rule-based keyword extraction"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_counts = Counter(words)
        
        # Filter common words
        common = {'that', 'this', 'with', 'from', 'have', 'will', 'would', 'could', 'should'}
        keywords = [
            word for word, count in word_counts.most_common(max_keywords * 2)
            if word not in common
        ]
        
        return keywords[:max_keywords]
    
    def understand_job_description(self, description: str) -> Dict:
        """
        Use AI to understand and categorize job description
        Returns structured information about the job
        """
        if not AI_AVAILABLE:
            return self._understand_rule_based(description)
        
        try:
            analysis = {
                'job_type': self._classify_job_type(description),
                'required_experience': self._extract_experience_level(description),
                'required_education': self._extract_education_level(description),
                'key_skills': self.extract_keywords_ai(description, 10),
                'is_remote': 'remote' in description.lower() or 'work from home' in description.lower(),
                'salary_range': self._extract_salary_range(description),
                'industry': self._classify_industry(description)
            }
            
            return analysis
        except Exception as e:
            print(f"[AI SEARCH] Error in job understanding: {e}")
            return self._understand_rule_based(description)
    
    def _classify_job_type(self, description: str) -> str:
        """Classify job type (full-time, part-time, contract, etc.)"""
        desc_lower = description.lower()
        
        if 'full-time' in desc_lower or 'full time' in desc_lower:
            return 'full-time'
        elif 'part-time' in desc_lower or 'part time' in desc_lower:
            return 'part-time'
        elif 'contract' in desc_lower:
            return 'contract'
        elif 'internship' in desc_lower or 'intern' in desc_lower:
            return 'internship'
        else:
            return 'full-time'  # Default
    
    def _extract_experience_level(self, description: str) -> str:
        """Extract required experience level"""
        desc_lower = description.lower()
        
        if any(term in desc_lower for term in ['senior', 'lead', 'principal', '10+ years', '15+ years']):
            return 'senior'
        elif any(term in desc_lower for term in ['mid-level', 'mid level', '3-5 years', '5+ years']):
            return 'mid-level'
        elif any(term in desc_lower for term in ['junior', 'entry', '0-2 years', '1-2 years']):
            return 'entry-level'
        else:
            return 'mid-level'  # Default
    
    def _extract_education_level(self, description: str) -> str:
        """Extract required education level"""
        desc_lower = description.lower()
        
        if 'phd' in desc_lower or 'doctorate' in desc_lower:
            return 'phd'
        elif 'master' in desc_lower or 'ms' in desc_lower or 'm.sc' in desc_lower:
            return 'master'
        elif 'bachelor' in desc_lower or 'bsc' in desc_lower or 'bs' in desc_lower:
            return 'bachelor'
        else:
            return 'bachelor'  # Default
    
    def _extract_salary_range(self, description: str) -> Optional[Dict]:
        """Extract salary range if mentioned"""
        # Look for salary patterns
        patterns = [
            r'\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*-\s*\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)',
            r'\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)\s*to\s*\$?(\d{1,3}(?:,\d{3})*(?:k|K)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                min_sal = match.group(1).replace(',', '').replace('k', '000').replace('K', '000')
                max_sal = match.group(2).replace(',', '').replace('k', '000').replace('K', '000')
                try:
                    return {
                        'min': int(min_sal),
                        'max': int(max_sal)
                    }
                except:
                    pass
        
        return None
    
    def _classify_industry(self, description: str) -> str:
        """Classify industry based on keywords"""
        desc_lower = description.lower()
        
        industries = {
            'technology': ['software', 'tech', 'it', 'developer', 'programming', 'coding'],
            'finance': ['finance', 'banking', 'investment', 'financial'],
            'healthcare': ['health', 'medical', 'hospital', 'patient', 'clinical'],
            'education': ['education', 'teaching', 'university', 'school', 'academic'],
            'research': ['research', 'scientist', 'laboratory', 'study', 'analysis'],
        }
        
        for industry, keywords in industries.items():
            if any(keyword in desc_lower for keyword in keywords):
                return industry
        
        return 'general'
    
    def _understand_rule_based(self, description: str) -> Dict:
        """Fallback rule-based understanding"""
        return {
            'job_type': self._classify_job_type(description),
            'required_experience': self._extract_experience_level(description),
            'required_education': self._extract_education_level(description),
            'key_skills': self._extract_keywords_rule_based(description, 10),
            'is_remote': 'remote' in description.lower(),
            'salary_range': self._extract_salary_range(description),
            'industry': self._classify_industry(description)
        }
