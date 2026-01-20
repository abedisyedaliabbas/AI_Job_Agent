"""
Profile Manager - Extracts and manages CV/profile data
"""
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Education:
    degree: str
    institution: str
    field: str
    graduation_date: str
    thesis: Optional[str] = None


@dataclass
class Experience:
    title: str
    company: str
    location: str
    start_date: str
    end_date: str
    description: List[str]


@dataclass
class Publication:
    title: str
    authors: str
    journal: str
    year: int
    doi: Optional[str] = None
    co_first: Optional[bool] = None
    status: Optional[str] = None  # e.g., "under review", "revised submission"
    manuscript: Optional[str] = None
    institution: Optional[str] = None  # For dissertations
    supervisor: Optional[str] = None  # For dissertations


@dataclass
class Skill:
    category: str
    skills: List[str]


@dataclass
class Profile:
    name: str
    email: str
    phone: str
    location: str
    date_of_birth: Optional[str] = None
    website: Optional[str] = None
    orcid: Optional[str] = None
    education: List[Education] = None
    experience: List[Experience] = None
    publications: List[Publication] = None
    skills: List[Skill] = None
    awards: List[str] = None
    presentations: List[str] = None
    metrics: Optional[Dict] = None
    research_interests: List[str] = None
    research_summary: Optional[str] = None
    job_keywords: List[str] = None  # Custom job search keywords
    
    def __post_init__(self):
        if self.education is None:
            self.education = []
        if self.experience is None:
            self.experience = []
        if self.publications is None:
            self.publications = []
        if self.skills is None:
            self.skills = []
        if self.awards is None:
            self.awards = []
        if self.presentations is None:
            self.presentations = []
        if self.research_interests is None:
            self.research_interests = []
        if self.job_keywords is None:
            self.job_keywords = []


class ProfileManager:
    """Manages user profile data extracted from CV"""
    
    def __init__(self, profile_file: str = "profile.json"):
        self.profile_file = profile_file
        self.profile: Optional[Profile] = None
    
    def load_from_cv_data(self, cv_data: Dict) -> Profile:
        """Load profile from structured CV data"""
        # Extract basic info
        profile = Profile(
            name=cv_data.get("name", ""),
            email=cv_data.get("email", ""),
            phone=cv_data.get("phone", ""),
            location=cv_data.get("location", ""),
            date_of_birth=cv_data.get("date_of_birth"),
            website=cv_data.get("website"),
            orcid=cv_data.get("orcid")
        )
        
        # Extract education
        for edu in cv_data.get("education", []):
            profile.education.append(Education(**edu))
        
        # Extract experience
        for exp in cv_data.get("experience", []):
            profile.experience.append(Experience(**exp))
        
        # Extract publications
        for pub in cv_data.get("publications", []):
            profile.publications.append(Publication(**pub))
        
        # Extract skills
        for skill in cv_data.get("skills", []):
            profile.skills.append(Skill(**skill))
        
        profile.awards = cv_data.get("awards", [])
        profile.presentations = cv_data.get("presentations", [])
        profile.metrics = cv_data.get("metrics")
        profile.research_interests = cv_data.get("research_interests", [])
        profile.research_summary = cv_data.get("research_summary")
        
        self.profile = profile
        return profile
    
    def load_from_file(self) -> Profile:
        """Load profile from JSON file"""
        try:
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profile_dict = {
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "phone": data.get("phone"),
                    "location": data.get("location"),
                    "date_of_birth": data.get("date_of_birth"),
                    "website": data.get("website"),
                    "orcid": data.get("orcid"),
                    "education": [Education(**e) for e in data.get("education", [])],
                    "experience": [Experience(**e) for e in data.get("experience", [])],
                    "publications": [Publication(**p) for p in data.get("publications", [])],
                    "skills": [Skill(**s) for s in data.get("skills", [])],
                    "awards": data.get("awards", []),
                    "presentations": data.get("presentations", []),
                    "metrics": data.get("metrics"),
                    "research_interests": data.get("research_interests", []),
                    "research_summary": data.get("research_summary")
                }
                self.profile = Profile(**profile_dict)
                return self.profile
        except FileNotFoundError:
            raise FileNotFoundError(f"Profile file {self.profile_file} not found. Please create it first.")
    
    def save_to_file(self):
        """Save profile to JSON file"""
        if not self.profile:
            raise ValueError("No profile loaded. Load a profile first.")
        
        profile_dict = asdict(self.profile)
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_dict, f, indent=2, ensure_ascii=False)
    
    def get_key_skills(self) -> List[str]:
        """Extract all skills as a flat list"""
        all_skills = []
        for skill_category in self.profile.skills:
            all_skills.extend(skill_category.skills)
        return all_skills
    
    def get_experience_summary(self) -> str:
        """Get a summary of work experience"""
        summary_parts = []
        for exp in self.profile.experience:
            summary_parts.append(f"{exp.title} at {exp.company} ({exp.start_date} - {exp.end_date})")
        return " | ".join(summary_parts)
    
    def get_education_summary(self) -> str:
        """Get a summary of education"""
        summary_parts = []
        for edu in self.profile.education:
            summary_parts.append(f"{edu.degree} in {edu.field} from {edu.institution}")
        return " | ".join(summary_parts)
