"""
Skill Extractor - Extracts and normalizes skills from resume
Fixes issues like "TECHNICAL EXPERTISE" and "ics" being treated as skills
"""
import re
from typing import List, Dict, Set
from profile_manager import ProfileManager


class SkillExtractor:
    """Extracts and normalizes skills from profile"""
    
    # Common skill category headers to ignore
    SKILL_CATEGORY_HEADERS = {
        'technical expertise', 'technical skills', 'technical', 'expertise',
        'skills', 'competencies', 'proficiencies', 'capabilities',
        'programming', 'languages', 'software', 'tools', 'technologies',
        'frameworks', 'libraries', 'platforms', 'databases',
        'methodologies', 'practices', 'concepts', 'domains'
    }
    
    # Common non-skill words to filter (sentence fragments, verbs, adverbs, etc.)
    FILTER_WORDS = {
        'and', 'or', 'the', 'a', 'an', 'with', 'using', 'via', 'for', 'to', 'in', 'on', 'at', 'by',
        'ics', 'ing', 'tion', 'sion', 'ment', 'ness', 'ity',
        'experience', 'knowledge', 'familiarity', 'understanding',
        'proficient', 'skilled', 'expert', 'advanced', 'intermediate',
        # Sentence fragments and verbs
        'actively', 'guided', 'utilising', 'utilizing', 'performed', 'conducted', 'led', 'organized',
        'employing', 'leveraging', 'developing', 'creating', 'designing', 'implementing',
        # Adverbs and common words
        'also', 'including', 'especially', 'particularly', 'specifically', 'primarily',
        # Institution names (not skills)
        'ntu', 'sutd', 'nus', 'ucl', 'mit', 'stanford', 'harvard', 'oxford', 'cambridge',
        # Generic terms
        'density', 'photostability', 'stability', 'methodology', 'approach', 'technique',
        # Common sentence words
        'this', 'that', 'these', 'those', 'from', 'into', 'onto', 'upon', 'within', 'without'
    }
    
    # Minimum skill length
    MIN_SKILL_LENGTH = 3
    
    def __init__(self, profile_manager: ProfileManager):
        self.profile_manager = profile_manager
    
    def extract_clean_skills(self) -> List[Dict[str, any]]:
        """
        Extract clean, normalized skills from profile
        Returns list of dicts with: {'skill': str, 'category': str, 'confidence': float}
        """
        if not self.profile_manager or not self.profile_manager.profile:
            return []
        
        profile = self.profile_manager.profile
        all_skills = []
        
        # Extract from skills section - be less strict, accept more skills
        if profile.skills:
            for skill_obj in profile.skills:
                category = skill_obj.category.strip() if skill_obj.category else "General"
                
                # Skip if category is a generic header
                if category.lower() in self.SKILL_CATEGORY_HEADERS:
                    category = "Technical Skills"  # Use generic category
                
                # Process individual skills - be more lenient
                for skill in skill_obj.skills:
                    cleaned = self._clean_skill(skill)
                    # Less strict validation - if it's from the skills section, trust it more
                    if cleaned and len(cleaned) >= 3:
                        # Only filter out obvious non-skills
                        cleaned_lower = cleaned.lower()
                        if cleaned_lower not in self.FILTER_WORDS and cleaned_lower not in self.SKILL_CATEGORY_HEADERS:
                            all_skills.append({
                                'skill': cleaned,
                                'category': self._normalize_category(category),
                                'confidence': 1.0
                            })
        
        # Extract from experience descriptions - but be very conservative
        # Only extract known technical terms, not sentence fragments
        if profile.experience:
            for exp in profile.experience:
                if exp.description:
                    for desc in exp.description:
                        # Only extract if we find known technical terms
                        skills_found = self._extract_skills_from_text(desc)
                        for skill in skills_found:
                            # Double-check it's a valid skill (not a sentence fragment)
                            if self._is_valid_skill(skill) and skill.lower() not in self.FILTER_WORDS:
                                all_skills.append({
                                    'skill': skill,
                                    'category': 'Work Experience',
                                    'confidence': 0.7  # Lower confidence for extracted skills
                                })
        
        # Extract from education
        if profile.education:
            for edu in profile.education:
                if edu.field:
                    field_skills = self._extract_skills_from_text(edu.field)
                    for skill in field_skills:
                        all_skills.append({
                            'skill': skill,
                            'category': 'Education',
                            'confidence': 0.7
                        })
        
        # Remove duplicates, keeping highest confidence
        unique_skills = {}
        for skill_data in all_skills:
            skill_lower = skill_data['skill'].lower()
            if skill_lower not in unique_skills or unique_skills[skill_lower]['confidence'] < skill_data['confidence']:
                unique_skills[skill_lower] = skill_data
        
        return list(unique_skills.values())
    
    def _clean_skill(self, skill: str) -> str:
        """Clean and normalize a skill string"""
        if not skill:
            return ""
        
        # Remove extra whitespace
        skill = ' '.join(skill.split())
        
        # Remove common prefixes/suffixes
        skill = re.sub(r'^(proficient in|skilled in|experience with|knowledge of|familiar with)\s+', '', skill, flags=re.IGNORECASE)
        skill = skill.strip('.,;:()[]{}')
        
        # Fix common OCR/parsing errors
        skill = skill.replace('rn', 'm').replace('corn', 'com')
        
        # Capitalize properly (title case for multi-word, uppercase for acronyms)
        if skill.isupper() and len(skill) <= 5:
            # Likely an acronym, keep uppercase
            pass
        elif len(skill.split()) == 1:
            # Single word - capitalize first letter
            skill = skill.capitalize()
        else:
            # Multiple words - title case
            skill = skill.title()
        
        return skill.strip()
    
    def _is_valid_skill(self, skill: str) -> bool:
        """Check if a string is a valid skill - filters out sentence fragments"""
        if not skill or len(skill) < self.MIN_SKILL_LENGTH:
            return False
        
        skill_lower = skill.lower().strip()
        
        # Filter out category headers
        if skill_lower in self.SKILL_CATEGORY_HEADERS:
            return False
        
        # Filter out common non-skill words
        if skill_lower in self.FILTER_WORDS:
            return False
        
        # Filter out very short fragments
        if len(skill) < 3:
            return False
        
        # Filter out words that are just suffixes
        if skill_lower in ['ics', 'ing', 'tion', 'sion', 'ment']:
            return False
        
        # Filter out generic words
        generic_words = ['data', 'system', 'software', 'application', 'technology', 'method', 'approach']
        if skill_lower in generic_words:
            return False
        
        # Filter out sentence fragments (words ending in -ly are usually adverbs)
        if skill_lower.endswith('ly') and len(skill_lower) < 8:
            return False
        
        # Filter out common verbs in -ing form (unless they're actual skills like "Programming")
        if skill_lower.endswith('ing') and skill_lower not in ['programming', 'engineering', 'marketing', 'designing']:
            # Check if it's a verb by common patterns
            if skill_lower in ['utilising', 'utilizing', 'employing', 'leveraging', 'developing', 'creating']:
                return False
        
        # Filter out institution names (NTU, SUTD, etc.)
        institution_patterns = [r'^[a-z]{2,4}$', r'^[a-z]+university$', r'^[a-z]+institute$', r'^[a-z]+college$']
        for pattern in institution_patterns:
            if re.match(pattern, skill_lower) and len(skill_lower) <= 6:
                return False
        
        # Filter out words that look like sentence fragments (single common words)
        if len(skill.split()) == 1:
            # Check if it's a common word that shouldn't be a skill
            common_words = ['density', 'stability', 'photostability', 'methodology', 'technique']
            if skill_lower in common_words:
                return False
        
        # Must contain at least one letter
        if not re.search(r'[a-zA-Z]', skill):
            return False
        
        # Skills should be recognizable technical terms, tools, languages, or frameworks
        # If it's a single word and doesn't look like a technical term, be more strict
        if len(skill.split()) == 1:
            # Single words should be: acronyms (all caps, 2-5 chars), or proper nouns (capitalized)
            # Or common technical terms
            if not (skill.isupper() and 2 <= len(skill) <= 5) and not skill[0].isupper():
                # Check if it's a known technical term
                known_tech_terms = ['python', 'java', 'c++', 'javascript', 'sql', 'html', 'css', 
                                   'dft', 'tddft', 'gaussian', 'orca', 'vasp', 'materials', 'studio',
                                   'matlab', 'r', 'linux', 'unix', 'windows', 'macos']
                if skill_lower not in known_tech_terms:
                    # If it's lowercase and not a known term, it's probably a sentence fragment
                    if skill.islower() and len(skill) > 4:
                        return False
        
        return True
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category name"""
        if not category:
            return "General"
        
        category = category.strip()
        
        # Map common variations
        category_map = {
            'technical expertise': 'Technical Skills',
            'technical skills': 'Technical Skills',
            'programming': 'Programming Languages',
            'languages': 'Programming Languages',
            'software': 'Software & Tools',
            'tools': 'Software & Tools',
            'frameworks': 'Frameworks & Libraries',
            'libraries': 'Frameworks & Libraries',
            'databases': 'Databases',
            'methodologies': 'Methodologies',
            'cloud': 'Cloud & DevOps',
            'devops': 'Cloud & DevOps'
        }
        
        category_lower = category.lower()
        if category_lower in category_map:
            return category_map[category_lower]
        
        # Title case for display
        return category.title()
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract potential skills from text - only actual technical terms, not sentence fragments"""
        if not text:
            return []
        
        skills = []
        
        # Known technical terms and tools to look for
        known_tech_terms = [
            'python', 'java', 'javascript', 'c++', 'c#', 'sql', 'html', 'css', 'r', 'matlab',
            'dft', 'tddft', 'gaussian', 'orca', 'vasp', 'materials studio', 'gromacs', 'amber',
            'linux', 'unix', 'windows', 'macos', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express'
        ]
        
        text_lower = text.lower()
        # Look for known technical terms
        for term in known_tech_terms:
            if term in text_lower:
                skills.append(term.title() if ' ' not in term else term)
        
        # Look for common skill patterns (but be more strict)
        # Pattern 1: Acronyms (2-5 uppercase letters) - likely technical terms
        acronyms = re.findall(r'\b([A-Z]{2,5})\b', text)
        institution_names = ['ntu', 'sutd', 'nus', 'ucl', 'mit', 'usa', 'uk', 'sg', 'phd', 'ms', 'bsc']
        for acro in acronyms:
            if acro.lower() not in institution_names:  # Skip institution names
                skills.append(acro)
        
        # Pattern 2: Proper nouns that might be tools/software (capitalized, 3+ chars)
        # BUT: Only extract if it's a known technical term - don't extract random capitalized words
        # This prevents extracting sentence fragments like "Actively", "Guided", "Utilising"
        proper_nouns = re.findall(r'\b([A-Z][a-z]{2,})\b', text)
        for noun in proper_nouns:
            noun_lower = noun.lower()
            # ONLY include if it's a known technical term - be very conservative
            if noun_lower in known_tech_terms:
                skills.append(noun)
            # Skip all other proper nouns - they're likely sentence fragments or institution names
        
        # Clean and validate all extracted skills
        cleaned_skills = []
        for s in skills:
            cleaned = self._clean_skill(s)
            if cleaned and self._is_valid_skill(cleaned):
                cleaned_skills.append(cleaned)
        
        return cleaned_skills
    
    def get_top_skills(self, limit: int = 20) -> List[str]:
        """Get top skills sorted by confidence"""
        skills = self.extract_clean_skills()
        skills.sort(key=lambda x: x['confidence'], reverse=True)
        return [s['skill'] for s in skills[:limit]]
    
    def get_skills_by_category(self) -> Dict[str, List[str]]:
        """Get skills grouped by category"""
        skills = self.extract_clean_skills()
        categorized = {}
        
        for skill_data in skills:
            category = skill_data['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill_data['skill'])
        
        return categorized
