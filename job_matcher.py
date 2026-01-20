"""
Job Matcher - Scores and ranks jobs based on profile match
"""
from typing import List, Dict
from job_search import JobListing
from profile_manager import ProfileManager
import re


class JobMatcher:
    """Matches jobs to user profile and calculates match scores"""
    
    def __init__(self, profile: ProfileManager):
        self.profile = profile
    
    def calculate_match_score(self, job: JobListing) -> float:
        """
        Calculate how well a job matches the user's profile
        Returns a score from 0.0 to 1.0
        """
        if not self.profile.profile:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        # Extract keywords from job description and requirements
        job_text = (job.description + " " + " ".join(job.requirements)).lower()
        job_title = job.title.lower()
        
        # Get profile data
        profile_skills = [skill.lower() for skill in self.profile.get_key_skills()]
        experience_summary = self.profile.get_experience_summary().lower()
        education_summary = self.profile.get_education_summary().lower()
        
        # 1. Skill matching (40% weight)
        max_score += 40
        skill_matches = 0
        total_skill_mentions = 0
        
        for skill in profile_skills:
            # Extract individual skills from skill strings
            skill_keywords = re.findall(r'\b\w+\b', skill)
            for keyword in skill_keywords:
                if len(keyword) > 3:  # Ignore short words
                    total_skill_mentions += 1
                    if keyword in job_text or keyword in job_title:
                        skill_matches += 1
        
        if total_skill_mentions > 0:
            skill_score = (skill_matches / total_skill_mentions) * 40
            score += skill_score
        
        # 2. Experience matching (30% weight) - generic approach
        max_score += 30
        # Extract keywords from user's experience and skills dynamically
        user_skills = self.profile.get_key_skills()
        user_exp_text = self.profile.get_experience_summary().lower()
        
        # Build dynamic keyword list from user's profile
        experience_keywords = []
        for skill in user_skills[:20]:  # Top 20 skills
            experience_keywords.append(skill.lower())
        
        # Add common professional keywords
        common_keywords = ["research", "development", "analysis", "management", "design", 
                          "implementation", "strategy", "optimization", "leadership", "collaboration"]
        experience_keywords.extend(common_keywords)
        
        # Match against job description
        exp_matches = sum(1 for keyword in experience_keywords if keyword in job_text)
        exp_score = min((exp_matches / max(len(experience_keywords), 1)) * 30, 30)
        score += exp_score
        
        # 3. Education level matching (15% weight)
        max_score += 15
        if "phd" in job_text or "doctorate" in job_text or "postdoc" in job_text:
            if "phd" in education_summary or "doctor" in education_summary:
                score += 15
        elif "master" in job_text or "ms" in job_text:
            if "phd" in education_summary or "master" in education_summary or "ms" in education_summary:
                score += 12
        else:
            score += 8  # Basic match
        
        # 4. Title/role matching (10% weight) - generic
        max_score += 10
        # Extract role keywords from user's experience titles
        user_titles = [exp.title.lower() for exp in self.profile.profile.experience]
        role_keywords = []
        for title in user_titles:
            # Extract key words from titles (skip common words)
            words = [w for w in title.split() if w not in ['the', 'a', 'an', 'at', 'in', 'of', 'for', 'and', 'or']]
            role_keywords.extend(words[:3])  # Top 3 words per title
        
        # Add common professional role keywords
        common_roles = ["researcher", "scientist", "engineer", "manager", "director", 
                       "analyst", "specialist", "coordinator", "developer", "consultant"]
        role_keywords.extend(common_roles)
        
        title_match = any(keyword in job_title for keyword in role_keywords)
        if title_match:
            score += 10
        
        # 5. Location matching (5% weight)
        max_score += 5
        profile_location = self.profile.profile.location.lower()
        job_location = job.location.lower()
        
        if profile_location in job_location or job_location in profile_location:
            score += 5
        elif "remote" in job_location or "singapore" in job_location:
            score += 3
        
        # Normalize score to 0-1 range
        normalized_score = score / max_score if max_score > 0 else 0.0
        
        return round(normalized_score, 3)
    
    def match_jobs(self, jobs: List[JobListing], min_score: float = 0.3) -> List[JobListing]:
        """
        Match and score all jobs, return sorted by match score
        """
        matched_jobs = []
        
        for job in jobs:
            score = self.calculate_match_score(job)
            job.match_score = score
            
            if score >= min_score:
                matched_jobs.append(job)
        
        # Sort by match score (highest first)
        matched_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        return matched_jobs
    
    def get_match_analysis(self, job: JobListing) -> Dict:
        """Get detailed analysis of why a job matches"""
        if not self.profile.profile:
            return {}
        
        analysis = {
            "match_score": job.match_score,
            "matched_skills": [],
            "matched_experience": [],
            "education_match": False,
            "location_match": False
        }
        
        job_text = (job.description + " " + " ".join(job.requirements)).lower()
        profile_skills = [skill.lower() for skill in self.profile.get_key_skills()]
        
        # Find matched skills
        for skill in profile_skills:
            skill_keywords = re.findall(r'\b\w+\b', skill)
            for keyword in skill_keywords:
                if len(keyword) > 3 and keyword in job_text:
                    if keyword not in analysis["matched_skills"]:
                        analysis["matched_skills"].append(keyword)
        
        # Check education match
        education_summary = self.profile.get_education_summary().lower()
        if "phd" in job_text or "doctorate" in job_text:
            analysis["education_match"] = "phd" in education_summary or "doctor" in education_summary
        
        # Check location match
        profile_location = self.profile.profile.location.lower()
        job_location = job.location.lower()
        analysis["location_match"] = (
            profile_location in job_location or 
            job_location in profile_location or
            "remote" in job_location
        )
        
        return analysis
