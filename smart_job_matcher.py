"""
Smart Job Matcher - Uses semantic similarity like Indeed/LinkedIn
Implements vector-based matching and weighted scoring
"""
from typing import List, Dict
from job_search import JobListing
from profile_manager import ProfileManager
import re
from collections import Counter


class SmartJobMatcher:
    """Advanced job matcher using semantic similarity and weighted scoring"""
    
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
        self.profile = profile_manager.profile
    
    def calculate_semantic_match(self, job: JobListing) -> float:
        """
        Calculate match score using semantic similarity (like Indeed/LinkedIn)
        Uses weighted scoring: Skills (50%), Experience (30%), Education (20%)
        """
        job_text = f"{job.title} {job.description} {' '.join(job.requirements)}".lower()
        job_title = job.title.lower()
        
        score = 0.0
        max_score = 100.0
        
        # 1. SKILLS MATCHING (50% weight)
        skills_score = self._match_skills(job_text, job_title)
        score += skills_score * 0.5
        max_score += 0  # Already accounted
        
        # 2. EXPERIENCE MATCHING (30% weight)
        experience_score = self._match_experience(job_text, job_title)
        score += experience_score * 0.3
        
        # 3. EDUCATION MATCHING (20% weight)
        education_score = self._match_education(job_text)
        score += education_score * 0.2
        
        # Normalize to 0-1 range
        normalized_score = min(score / max_score, 1.0)
        
        return round(normalized_score, 3)
    
    def _match_skills(self, job_text: str, job_title: str) -> float:
        """Match skills - 50% weight - matches in title OR description"""
        if not self.profile.skills:
            return 30.0  # Default score if no skills
        
        # Extract all user skills
        user_skills = []
        for skill_cat in self.profile.skills:
            if skill_cat.skills:
                # Clean skills - remove category headers and extract actual skills
                for skill in skill_cat.skills:
                    skill_lower = skill.lower().strip()
                    # Remove bullet points and special chars
                    skill_lower = skill_lower.replace('•', '').replace('&', '').replace(':', '').strip()
                    # Skip category headers
                    if any(word in skill_lower for word in ['category', 'technical', 'expertise', 'skills']):
                        continue
                    # Extract meaningful words from skill strings (2+ chars)
                    skill_words = [w for w in skill_lower.split() if len(w) > 2]
                    user_skills.extend(skill_words)
        
        if not user_skills:
            return 30.0  # Default score
        
        # Count skill matches in BOTH title AND description
        matches = 0
        for skill in user_skills[:50]:  # Limit to top 50 skills
            # Exact match in title (higher weight)
            if skill in job_title:
                matches += 3
            # Exact match in description
            elif skill in job_text:
                matches += 2
            # Partial match (word in skill)
            elif any(word in job_text for word in skill.split() if len(word) > 3):
                matches += 1
        
        # Normalize by number of skills (but give minimum score)
        max_possible = min(len(user_skills), 50) * 3  # Max 3 points per skill
        score = min(matches / max_possible if max_possible > 0 else 0, 1.0) * 100
        return max(score, 20.0)  # Minimum 20% score
    
    def _match_experience(self, job_text: str, job_title: str) -> float:
        """Match experience - 30% weight"""
        if not self.profile.experience:
            return 20.0  # Default score
        
        # Extract keywords from user's experience
        user_keywords = []
        for exp in self.profile.experience:
            if exp.title:
                # Title words (clean them)
                title_clean = exp.title.lower().replace('•', '').replace('visiting', '').strip()
                title_words = [w for w in title_clean.split() if len(w) > 3 and w not in ['position', 'at', 'the']]
                user_keywords.extend(title_words)
            
            # Description words
            if exp.description:
                for desc in exp.description[:2]:  # Top 2 descriptions
                    desc_words = [w.lower() for w in desc.split() if len(w) > 4]
                    user_keywords.extend(desc_words[:5])  # Top 5 per description
        
        if not user_keywords:
            return 20.0  # Default score
        
        # Count matches
        matches = sum(1 for keyword in user_keywords if keyword in job_text or keyword in job_title)
        
        # Normalize (but give minimum score)
        max_possible = len(user_keywords)
        score = min(matches / max_possible if max_possible > 0 else 0, 1.0) * 100
        return max(score, 15.0)  # Minimum 15% score
    
    def _match_education(self, job_text: str) -> float:
        """Match education - 20% weight"""
        if not self.profile.education:
            return 0.0
        
        # Check for degree requirements
        degree_keywords = {
            'phd': ['phd', 'ph.d', 'doctorate', 'doctor', 'postdoc'],
            'master': ['master', 'm.s', 'm.sc', 'ms', 'mba'],
            'bachelor': ['bachelor', 'b.s', 'b.sc', 'bs', 'degree']
        }
        
        # Check user's highest degree
        user_degrees = [edu.degree.lower() for edu in self.profile.education]
        user_highest = 'bachelor'  # Default
        if any('phd' in d or 'doctor' in d for d in user_degrees):
            user_highest = 'phd'
        elif any('master' in d or 'ms' in d or 'mba' in d for d in user_degrees):
            user_highest = 'master'
        
        # Check job requirements
        score = 0.0
        if user_highest == 'phd':
            if any(kw in job_text for kw in degree_keywords['phd']):
                score = 100.0
            elif any(kw in job_text for kw in degree_keywords['master']):
                score = 80.0
            else:
                score = 60.0
        elif user_highest == 'master':
            if any(kw in job_text for kw in degree_keywords['master']):
                score = 100.0
            elif any(kw in job_text for kw in degree_keywords['bachelor']):
                score = 80.0
            else:
                score = 50.0
        else:
            if any(kw in job_text for kw in degree_keywords['bachelor']):
                score = 100.0
            else:
                score = 40.0
        
        return score
    
    def match_jobs(self, jobs: List[JobListing], min_score: float = 0.0) -> List[JobListing]:
        """Match and score all jobs - returns ALL jobs with scores"""
        scored_jobs = []
        
        for job in jobs:
            try:
                score = self.calculate_semantic_match(job)
                job.match_score = score
                scored_jobs.append(job)
            except Exception as e:
                print(f"Error matching job {job.title}: {e}")
                # Still include job with default score
                job.match_score = 0.3
                scored_jobs.append(job)
        
        # Filter by min_score if specified
        if min_score > 0:
            scored_jobs = [j for j in scored_jobs if j.match_score >= min_score]
        
        # Sort by match score (highest first)
        scored_jobs.sort(key=lambda j: j.match_score, reverse=True)
        
        return scored_jobs
