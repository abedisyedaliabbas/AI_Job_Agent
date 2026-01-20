"""
ML-Powered Job Matcher - Uses AI/ML for intelligent job matching
Uses sentence transformers, embeddings, and ML models for better matching
"""
from typing import List, Dict, Optional
from job_search import JobListing
from profile_manager import ProfileManager
import numpy as np
from collections import Counter
import re

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("[ML MATCHER] Warning: sentence-transformers not installed. Install with: pip install sentence-transformers scikit-learn")


class MLJobMatcher:
    """
    Advanced ML-powered job matcher using:
    - Sentence Transformers for semantic similarity
    - Vector embeddings for job descriptions
    - ML-based scoring algorithms
    - Classification for job fit prediction
    """
    
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
        self.profile = profile_manager.profile
        
        # Initialize ML models
        self.model = None
        self.profile_embedding = None
        
        if ML_AVAILABLE:
            try:
                # Use a lightweight, fast model for embeddings
                # 'all-MiniLM-L6-v2' is fast and good for semantic similarity
                print("[ML MATCHER] Loading sentence transformer model...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[ML MATCHER] Model loaded successfully!")
                self._create_profile_embedding()
            except Exception as e:
                print(f"[ML MATCHER] Error loading model: {e}")
                print("[ML MATCHER] Falling back to keyword-based matching")
                self.model = None
        else:
            print("[ML MATCHER] ML libraries not available. Using keyword-based matching")
    
    def _create_profile_embedding(self):
        """Create a vector embedding of the user's profile"""
        if not self.model or not self.profile:
            return
        
        try:
            # Combine all profile information into a single text
            profile_text_parts = []
            
            # Add skills
            if self.profile.skills:
                for skill_cat in self.profile.skills:
                    if skill_cat.skills:
                        profile_text_parts.extend(skill_cat.skills)
            
            # Add experience
            if self.profile.experience:
                for exp in self.profile.experience:
                    if exp.title:
                        profile_text_parts.append(exp.title)
                    if exp.description:
                        profile_text_parts.append(exp.description)
            
            # Add education
            if self.profile.education:
                for edu in self.profile.education:
                    if edu.field:
                        profile_text_parts.append(edu.field)
                    if edu.degree:
                        profile_text_parts.append(edu.degree)
            
            # Combine into single text
            profile_text = " ".join(profile_text_parts)
            
            if profile_text:
                # Create embedding
                self.profile_embedding = self.model.encode(profile_text, convert_to_numpy=True)
                print("[ML MATCHER] Profile embedding created successfully")
        except Exception as e:
            print(f"[ML MATCHER] Error creating profile embedding: {e}")
            self.profile_embedding = None
    
    def calculate_ml_match_score(self, job: JobListing) -> float:
        """
        Calculate match score using ML/AI:
        1. Semantic similarity using sentence transformers (60%)
        2. Skill matching using embeddings (25%)
        3. Experience/Education matching (15%)
        """
        if not self.profile:
            return 0.0
        
        # Combine job information
        job_text = f"{job.title} {job.description} {' '.join(job.requirements)}"
        
        scores = {}
        
        # 1. SEMANTIC SIMILARITY (60% weight) - Using ML embeddings
        semantic_score = self._calculate_semantic_similarity(job_text)
        scores['semantic'] = semantic_score * 0.6
        
        # 2. SKILL MATCHING (25% weight) - Enhanced with embeddings
        skill_score = self._calculate_skill_match_ml(job_text, job.title)
        scores['skills'] = skill_score * 0.25
        
        # 3. EXPERIENCE/EDUCATION (15% weight)
        exp_edu_score = self._calculate_experience_education_match(job_text)
        scores['experience'] = exp_edu_score * 0.15
        
        # Total score
        total_score = sum(scores.values())
        
        return round(min(total_score, 1.0), 3)
    
    def _calculate_semantic_similarity(self, job_text: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        if not self.model or self.profile_embedding is None:
            # Fallback to keyword matching
            return self._fallback_keyword_match(job_text)
        
        try:
            # Create embedding for job
            job_embedding = self.model.encode(job_text, convert_to_numpy=True)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                self.profile_embedding.reshape(1, -1),
                job_embedding.reshape(1, -1)
            )[0][0]
            
            # Normalize to 0-1 range (cosine similarity is -1 to 1, but usually 0-1)
            normalized = max(0.0, similarity)
            
            return float(normalized)
        except Exception as e:
            print(f"[ML MATCHER] Error in semantic similarity: {e}")
            return self._fallback_keyword_match(job_text)
    
    def _calculate_skill_match_ml(self, job_text: str, job_title: str) -> float:
        """Enhanced skill matching using ML embeddings"""
        if not self.profile.skills or not self.model:
            return 0.0
        
        try:
            # Extract all skills from profile
            all_skills = []
            for skill_cat in self.profile.skills:
                if skill_cat.skills:
                    all_skills.extend(skill_cat.skills)
            
            if not all_skills:
                return 0.0
            
            # Create embeddings for skills
            skill_embeddings = self.model.encode(all_skills, convert_to_numpy=True)
            job_embedding = self.model.encode(job_text, convert_to_numpy=True)
            
            # Calculate similarities
            similarities = cosine_similarity(
                skill_embeddings,
                job_embedding.reshape(1, -1)
            ).flatten()
            
            # Get top matches (skills with highest similarity)
            top_similarities = np.sort(similarities)[-min(10, len(similarities)):]
            
            # Average of top matches
            avg_similarity = float(np.mean(top_similarities))
            
            # Also check title match (higher weight)
            title_embedding = self.model.encode(job_title, convert_to_numpy=True)
            title_similarity = cosine_similarity(
                skill_embeddings,
                title_embedding.reshape(1, -1)
            ).flatten()
            max_title_similarity = float(np.max(title_similarity))
            
            # Combine: 70% description, 30% title
            combined = (avg_similarity * 0.7) + (max_title_similarity * 0.3)
            
            return max(0.0, combined)
        except Exception as e:
            print(f"[ML MATCHER] Error in skill matching: {e}")
            return self._fallback_skill_match(job_text, job_title)
    
    def _calculate_experience_education_match(self, job_text: str) -> float:
        """Match experience and education using ML"""
        if not self.model:
            return self._fallback_exp_edu_match(job_text)
        
        try:
            # Create text from experience
            exp_texts = []
            if self.profile.experience:
                for exp in self.profile.experience:
                    exp_text = f"{exp.title} {exp.description or ''}"
                    exp_texts.append(exp_text)
            
            # Create text from education
            edu_texts = []
            if self.profile.education:
                for edu in self.profile.education:
                    edu_text = f"{edu.degree} {edu.field}"
                    edu_texts.append(edu_text)
            
            if not exp_texts and not edu_texts:
                return 0.0
            
            # Combine all experience/education
            profile_exp_edu = " ".join(exp_texts + edu_texts)
            
            # Create embeddings
            profile_embedding = self.model.encode(profile_exp_edu, convert_to_numpy=True)
            job_embedding = self.model.encode(job_text, convert_to_numpy=True)
            
            # Calculate similarity
            similarity = cosine_similarity(
                profile_embedding.reshape(1, -1),
                job_embedding.reshape(1, -1)
            )[0][0]
            
            return max(0.0, float(similarity))
        except Exception as e:
            print(f"[ML MATCHER] Error in experience/education matching: {e}")
            return self._fallback_exp_edu_match(job_text)
    
    def _fallback_keyword_match(self, job_text: str) -> float:
        """Fallback to keyword matching if ML is not available"""
        if not self.profile:
            return 0.0
        
        job_text_lower = job_text.lower()
        matches = 0
        total = 0
        
        # Check skills
        if self.profile.skills:
            for skill_cat in self.profile.skills:
                if skill_cat.skills:
                    for skill in skill_cat.skills:
                        skill_lower = skill.lower()
                        words = skill_lower.split()
                        for word in words:
                            if len(word) > 3:
                                total += 1
                                if word in job_text_lower:
                                    matches += 1
        
        return matches / max(total, 1)
    
    def _fallback_skill_match(self, job_text: str, job_title: str) -> float:
        """Fallback skill matching"""
        return self._fallback_keyword_match(job_text)
    
    def _fallback_exp_edu_match(self, job_text: str) -> float:
        """Fallback experience/education matching"""
        if not self.profile:
            return 0.0
        
        job_text_lower = job_text.lower()
        matches = 0
        
        # Check experience titles
        if self.profile.experience:
            for exp in self.profile.experience:
                if exp.title:
                    title_words = exp.title.lower().split()
                    for word in title_words:
                        if len(word) > 3 and word in job_text_lower:
                            matches += 1
        
        # Check education
        if self.profile.education:
            for edu in self.profile.education:
                if edu.field:
                    field_words = edu.field.lower().split()
                    for word in field_words:
                        if len(word) > 3 and word in job_text_lower:
                            matches += 1
        
        return min(matches / 10.0, 1.0)  # Normalize
    
    def match_jobs(self, jobs: List[JobListing], min_score: float = 0.3) -> List[JobListing]:
        """Match and score all jobs using ML"""
        print(f"[ML MATCHER] Matching {len(jobs)} jobs using AI/ML algorithms...")
        
        matched_jobs = []
        for job in jobs:
            score = self.calculate_ml_match_score(job)
            job.match_score = score
            
            if score >= min_score:
                matched_jobs.append(job)
        
        # Sort by match score (highest first)
        matched_jobs.sort(key=lambda x: x.match_score or 0.0, reverse=True)
        
        print(f"[ML MATCHER] Found {len(matched_jobs)} jobs with score >= {min_score}")
        
        return matched_jobs
    
    def get_match_explanation(self, job: JobListing) -> Dict:
        """Get detailed explanation of why a job matches (for transparency)"""
        if not self.profile:
            return {}
        
        job_text = f"{job.title} {job.description} {' '.join(job.requirements)}"
        
        explanation = {
            'overall_score': self.calculate_ml_match_score(job),
            'semantic_similarity': self._calculate_semantic_similarity(job_text),
            'skill_match': self._calculate_skill_match_ml(job_text, job.title),
            'experience_match': self._calculate_experience_education_match(job_text),
            'matched_skills': [],
            'matched_experience': []
        }
        
        # Find which specific skills matched
        if self.profile.skills and self.model:
            try:
                all_skills = []
                for skill_cat in self.profile.skills:
                    if skill_cat.skills:
                        all_skills.extend(skill_cat.skills)
                
                if all_skills:
                    skill_embeddings = self.model.encode(all_skills, convert_to_numpy=True)
                    job_embedding = self.model.encode(job_text, convert_to_numpy=True)
                    similarities = cosine_similarity(
                        skill_embeddings,
                        job_embedding.reshape(1, -1)
                    ).flatten()
                    
                    # Get top 5 matching skills
                    top_indices = np.argsort(similarities)[-5:][::-1]
                    explanation['matched_skills'] = [
                        {'skill': all_skills[i], 'similarity': float(similarities[i])}
                        for i in top_indices if similarities[i] > 0.3
                    ]
            except:
                pass
        
        return explanation
