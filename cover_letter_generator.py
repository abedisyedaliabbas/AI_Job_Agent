"""
Cover Letter Generator - Creates personalized, natural-sounding cover letters
Uses templates and variations to avoid AI detection
"""
import random
from typing import Dict, List
from job_search import JobListing
from profile_manager import ProfileManager
import re


class CoverLetterGenerator:
    """Generates personalized cover letters that sound natural and human-written"""
    
    def __init__(self, profile: ProfileManager):
        self.profile = profile
        
        # Opening variations - natural, conversational starts
        self.openings = [
            "I am writing to express my strong interest in the {title} position at {company}.",
            "I was excited to come across the {title} opening at {company} and would like to submit my application.",
            "With great enthusiasm, I am applying for the {title} role at {company}.",
            "I am reaching out regarding the {title} position at {company}, which aligns perfectly with my background.",
            "After reviewing the {title} opportunity at {company}, I am confident that my experience makes me an ideal candidate.",
        ]
        
        # Transition phrases - natural connectors
        self.transitions = [
            "In my current role",
            "Throughout my career",
            "My experience has equipped me with",
            "What particularly excites me about this opportunity is",
            "I bring to the table",
            "My background includes",
            "Having worked extensively in",
        ]
        
        # Closing variations
        self.closings = [
            "I would welcome the opportunity to discuss how my skills and experience can contribute to {company}'s continued success.",
            "I am eager to bring my expertise to {company} and would be delighted to discuss this opportunity further.",
            "Thank you for considering my application. I look forward to the possibility of contributing to your team.",
            "I am confident that my background in {field} would make me a valuable addition to {company}, and I would appreciate the chance to discuss this further.",
            "I would be thrilled to join {company} and contribute to your innovative work. Thank you for your time and consideration.",
        ]
    
    def extract_key_requirements(self, job: JobListing) -> List[str]:
        """Extract key requirements from job description"""
        requirements = []
        job_text = job.description.lower() + " " + " ".join(job.requirements).lower()
        
        # Common requirement patterns
        requirement_patterns = [
            r"(?:required|must have|essential|qualifications?)[:\s]+([^\.]+)",
            r"(?:experience|proficiency|knowledge|skills?)[:\s]+([^\.]+)",
            r"(?:degree|education|phd|master)[:\s]+([^\.]+)",
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            requirements.extend(matches)
        
        return requirements[:5]  # Top 5 requirements
    
    def find_relevant_experience(self, job: JobListing) -> List[str]:
        """Find most relevant experience points from profile"""
        if not self.profile.profile:
            return []
        
        relevant_points = []
        job_text = (job.description + " " + " ".join(job.requirements)).lower()
        
        # Score each experience based on relevance
        experience_scores = []
        for exp in self.profile.profile.experience:
            score = 0
            exp_text = " ".join(exp.description).lower() + " " + exp.title.lower()
            
            # Check for keyword matches - use dynamic keywords from user's skills
            user_skills = [s.lower() for s in self.profile.get_key_skills()]
            # Extract keywords from job description
            job_words = set(job_text.split())
            exp_words = set(exp_text.split())
            
            # Match skills and common professional terms
            matches = len(job_words.intersection(exp_words))
            matches += sum(1 for skill in user_skills if skill in job_text and skill in exp_text)
            score += matches
            
            experience_scores.append((exp, score))
        
        # Sort by relevance and take top 2-3
        experience_scores.sort(key=lambda x: x[1], reverse=True)
        top_experiences = [exp for exp, score in experience_scores[:3] if score > 0]
        
        # Extract key points from top experiences
        for exp in top_experiences:
            for desc in exp.description[:2]:  # Top 2 description points
                # Clean up description - ensure it starts with lowercase if it's a continuation
                desc_clean = desc.strip()
                # If it starts with a capital letter and is not a complete sentence, make it lowercase
                if desc_clean and desc_clean[0].isupper() and not desc_clean.endswith('.'):
                    # Check if it's a verb that should start lowercase in a sentence
                    if desc_clean.split()[0].lower() in ['guided', 'organized', 'performed', 'led', 'conducted', 'utilized', 'leveraged']:
                        desc_clean = desc_clean[0].lower() + desc_clean[1:]
                relevant_points.append(desc_clean)
        
        return relevant_points
    
    def find_relevant_skills(self, job: JobListing) -> List[str]:
        """Find skills that match job requirements - returns cleaned, readable skills"""
        if not self.profile.profile:
            return []
        
        relevant_skills = []
        job_text = (job.description + " " + " ".join(job.requirements)).lower()
        
        # Extract and clean skills from profile
        all_skills_cleaned = []
        for skill_cat in self.profile.profile.skills:
            if skill_cat.skills:
                for skill in skill_cat.skills:
                    # Clean skill: remove category headers, bullet points, special chars
                    skill_clean = skill.strip()
                    # Remove bullet points
                    skill_clean = skill_clean.replace('•', '').strip()
                    # Remove category headers (e.g., "TECHNICAL EXPERTISE, " or "Computational Chemistry:")
                    skill_clean = re.sub(r'^[A-Z\s]+,?\s*', '', skill_clean)  # Remove leading caps words
                    skill_clean = re.sub(r'^[^:]+:\s*', '', skill_clean)  # Remove "Category: " prefix
                    # Skip if it's just a category name
                    if any(word in skill_clean.lower() for word in ['category', 'technical', 'expertise', 'skills']):
                        continue
                    if skill_clean and len(skill_clean) > 2:
                        all_skills_cleaned.append(skill_clean)
        
        # Match skills to job requirements
        for skill in all_skills_cleaned:
            skill_lower = skill.lower()
            # Extract key terms from skill (words 4+ chars)
            skill_terms = re.findall(r'\b\w{4,}\b', skill_lower)
            
            # Check if any term matches job text
            for term in skill_terms:
                if term in job_text and skill not in relevant_skills:
                    relevant_skills.append(skill)
                    break
        
        return relevant_skills[:5]  # Top 5 relevant skills
    
    def generate_paragraph(self, sentences: List[str], style: str = "natural") -> str:
        """Generate a natural paragraph from sentences"""
        if not sentences:
            return ""
        
        # Clean and format sentences
        cleaned_sentences = []
        for idx, sent in enumerate(sentences):
            sent = sent.strip()
            # Remove trailing periods (we'll add them back)
            if sent.endswith("."):
                sent = sent[:-1]
            # Ensure proper capitalization (only if it doesn't start with a capital)
            if sent and not sent[0].isupper():
                sent = sent[0].upper() + sent[1:] if len(sent) > 1 else sent.upper()
            # Fix common issues: "With" at start should be lowercase if it's mid-sentence
            if sent.startswith("With ") and idx > 0:
                sent = "with " + sent[5:]
            cleaned_sentences.append(sent)
        
        if not cleaned_sentences:
            return ""
        
        # Start with first sentence
        paragraph = cleaned_sentences[0]
        if not paragraph.endswith("."):
            paragraph += "."
        
        # Add remaining sentences with connectors
        for i, sentence in enumerate(cleaned_sentences[1:], 1):
            # Vary connectors
            connectors = [". ", " Additionally, ", " Moreover, ", " Furthermore, ", " In addition, "]
            connector = random.choice(connectors)
            # Ensure sentence doesn't already have period
            if sentence.endswith("."):
                sentence = sentence[:-1]
            # If sentence starts with a connector word, lowercase it (e.g., "Currently" -> "currently")
            first_word = sentence.split()[0] if sentence.split() else ""
            if first_word.lower() in ["currently", "additionally", "moreover", "furthermore", "in", "with"]:
                sentence = first_word.lower() + sentence[len(first_word):]
            paragraph += connector + sentence + "."
        
        # Clean up any double periods
        paragraph = paragraph.replace("..", ".")
        
        return paragraph
    
    def generate_cover_letter(self, job: JobListing, style: str = "professional") -> str:
        """
        Generate a personalized cover letter for a job
        style: 'professional', 'enthusiastic', 'technical'
        """
        if not self.profile.profile:
            return ""
        
        profile = self.profile.profile
        
        # Clean job title (fix malformed titles like "Programmingpython")
        job_title_clean = job.title
        # Fix common issues: remove duplicate words, fix spacing
        job_title_clean = re.sub(r'(\w+)\1+', r'\1', job_title_clean)  # Remove duplicate words
        job_title_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', job_title_clean)  # Add space between camelCase
        job_title_clean = ' '.join(job_title_clean.split())  # Normalize whitespace
        
        # Select opening
        opening = random.choice(self.openings).format(
            title=job_title_clean,
            company=job.company
        )
        
        # Build body paragraphs
        paragraphs = [opening]
        
        # Paragraph 1: Why interested + relevant background - IMPROVED
        relevant_experience = self.find_relevant_experience(job)
        relevant_skills = self.find_relevant_skills(job)
        
        if relevant_experience and profile.experience:
            # Get current/most recent experience
            current_exp = profile.experience[0]
            exp_title_clean = current_exp.title.replace('•', '').strip()
            # Remove common prefixes
            exp_title_clean = re.sub(r'^(Visiting|Postdoctoral|Senior|Junior|Lead|Principal|Assistant|Associate)\s+', '', exp_title_clean, flags=re.IGNORECASE)
            
            # Build a more natural, specific paragraph
            exp_sentences = []
            
            # Start with why interested (more specific)
            job_keywords = []
            job_text_lower = (job.description + " " + " ".join(job.requirements)).lower()
            if relevant_skills:
                job_keywords = [s.split('(')[0].strip().lower() for s in relevant_skills[:2]]
            
            if job_keywords:
                keyword_phrase = " and ".join(job_keywords)
                exp_sentences.append(f"I am particularly drawn to this opportunity because it combines my expertise in {keyword_phrase} with the innovative work at {job.company}")
            else:
                exp_sentences.append(f"I am excited about this opportunity at {job.company} and believe my background aligns perfectly with your requirements")
            
            # Add specific, relevant experience
            if relevant_experience:
                exp_point = relevant_experience[0].strip()
                # Clean and format the experience point
                if not exp_point.endswith('.'):
                    exp_point += '.'
                # Ensure proper capitalization
                if exp_point and not exp_point[0].isupper():
                    exp_point = exp_point[0].upper() + exp_point[1:]
                
                # Make it flow naturally
                if current_exp.company:
                    exp_sentences.append(f"Currently, as {exp_title_clean} at {current_exp.company}, {exp_point.lower()}")
                else:
                    exp_sentences.append(f"As {exp_title_clean}, {exp_point.lower()}")
            
            # Add second experience point if available (more specific)
            if len(relevant_experience) > 1:
                exp_point2 = relevant_experience[1].strip()
                if not exp_point2.endswith('.'):
                    exp_point2 += '.'
                if exp_point2 and not exp_point2[0].isupper():
                    exp_point2 = exp_point2[0].upper() + exp_point2[1:]
                # Use natural connector
                exp_sentences.append(f"Additionally, {exp_point2.lower()}")
            
            para = self.generate_paragraph(exp_sentences)
            paragraphs.append(para)
        elif profile.experience:
            # Fallback - but make it more specific
            current_exp = profile.experience[0]
            exp_title_clean = current_exp.title.replace('•', '').strip()
            exp_title_clean = re.sub(r'^(Visiting|Postdoctoral|Senior|Junior|Lead|Principal|Assistant|Associate)\s+', '', exp_title_clean, flags=re.IGNORECASE)
            
            exp_sentences = [
                f"I am excited to apply for the {job_title_clean} position at {job.company}",
            ]
            if current_exp.company:
                exp_sentences.append(f"In my current role as {exp_title_clean} at {current_exp.company}, I have developed strong expertise that directly applies to this position")
            else:
                exp_sentences.append(f"As {exp_title_clean}, I have developed strong expertise that directly applies to this position")
            para = self.generate_paragraph(exp_sentences)
            paragraphs.append(para)
        
        # Paragraph 2: Specific skills and achievements - IMPROVED
        if relevant_skills:
            # Format skills naturally (remove acronyms in parentheses for readability)
            skills_clean = [s.split('(')[0].strip() for s in relevant_skills]
            if len(skills_clean) == 1:
                skill_text = skills_clean[0]
            elif len(skills_clean) == 2:
                skill_text = f"{skills_clean[0]} and {skills_clean[1]}"
            else:
                skill_text = f"{', '.join(skills_clean[:-1])}, and {skills_clean[-1]}"
            
            skill_sentences = [
                f"My technical expertise spans {skill_text}, which I have applied extensively in my research and professional work",
            ]
            
            # Add specific achievement if available (more natural)
            if profile.publications:
                # Count only published (not under review/preprint)
                published_count = sum(1 for p in profile.publications 
                                    if not p.status and p.journal != "SSRN Preprint" and p.journal != "Doctoral Dissertation")
                if published_count > 0:
                    skill_sentences.append(
                        f"This expertise is demonstrated through my {published_count} peer-reviewed publications, which showcase both my theoretical understanding and practical application of these methods"
                    )
                elif len(profile.publications) > 0:
                    skill_sentences.append(
                        f"My research experience, including {len(profile.publications)} publications, demonstrates my ability to apply these skills in real-world research contexts"
                    )
            
            # Add experience years if available
            if profile.experience:
                total_years = len(profile.experience)  # Rough estimate
                if total_years >= 3:
                    skill_sentences.append(
                        f"With over {total_years} years of experience in research and development, I have consistently delivered results and contributed to innovative projects"
                    )
            
            para = self.generate_paragraph(skill_sentences)
            paragraphs.append(para)
        
        # Paragraph 3: Why this company/role - IMPROVED (more specific and natural)
        field = self._extract_field(job)
        # Get top skills for this paragraph
        top_skill_mentions = []
        if relevant_skills:
            top_skill_mentions = [s.split('(')[0].strip() for s in relevant_skills[:2]]  # Get skill names without acronyms
        
        if top_skill_mentions:
            skill_phrase = " and ".join(top_skill_mentions)
            why_sentences = [
                f"What excites me most about the {job_title_clean} role is the opportunity to leverage my expertise in {skill_phrase} to address the challenges outlined in this position",
                f"I am particularly impressed by {job.company}'s commitment to innovation and believe my background would enable me to make immediate contributions to your team's objectives",
            ]
        else:
            why_sentences = [
                f"I am particularly excited about this role because it represents an opportunity to apply my research background and technical expertise to meaningful challenges",
                f"{job.company}'s reputation for innovation and excellence aligns with my career goals, and I am eager to contribute to your team's continued success",
            ]
        para = self.generate_paragraph(why_sentences)
        paragraphs.append(para)
        
        # Closing - use more specific field
        if relevant_skills:
            field_mention = relevant_skills[0].split('(')[0].strip()  # Use first skill as field
        else:
            field_mention = self._extract_field(job)
        
        closing = random.choice(self.closings).format(
            company=job.company,
            field=field_mention
        )
        paragraphs.append(closing)
        
        # Signature
        signature = f"\n\nSincerely,\n{profile.name}\n{profile.email}\n{profile.phone}"
        
        cover_letter = "\n\n".join(paragraphs) + signature
        
        return cover_letter
    
    def _extract_field(self, job: JobListing) -> str:
        """Extract the main field from job description - generic approach"""
        job_text = job.description.lower()
        job_title = job.title.lower()
        combined_text = f"{job_title} {job_text}"
        
        # Generic field detection based on common job categories
        field_keywords = {
            "technology": ["software", "developer", "engineer", "programming", "coding", "tech"],
            "data": ["data science", "data analyst", "data engineer", "analytics", "big data"],
            "ai/ml": ["machine learning", "ai", "artificial intelligence", "deep learning", "neural"],
            "research": ["research", "researcher", "scientist", "phd", "postdoc"],
            "business": ["business", "strategy", "consulting", "management", "operations"],
            "marketing": ["marketing", "digital marketing", "social media", "branding"],
            "sales": ["sales", "account manager", "business development", "revenue"],
            "finance": ["finance", "accounting", "financial", "analyst", "investment"],
            "design": ["design", "designer", "ui/ux", "graphic", "creative"],
            "product": ["product manager", "product", "pm", "product development"]
        }
        
        # Find the best matching field
        best_match = "professional"
        max_matches = 0
        
        for field, keywords in field_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in combined_text)
            if matches > max_matches:
                max_matches = matches
                best_match = field
        
        return best_match if max_matches > 0 else "professional"
    
    def add_personal_touches(self, cover_letter: str, job: JobListing) -> str:
        """Add subtle personal touches to make it less AI-like"""
        # Add slight variations in formatting
        variations = [
            ("I am", "I'm"),  # Occasionally use contractions
            ("cannot", "can't"),
            ("will not", "won't"),
        ]
        
        # Randomly apply some variations (sparingly)
        for formal, casual in variations:
            if random.random() < 0.2:  # 20% chance
                cover_letter = cover_letter.replace(formal, casual, 1)
        
        return cover_letter
    
    def save_cover_letter(self, cover_letter: str, job: JobListing, filename: str = None):
        """Save cover letter to file"""
        if filename is None:
            # Create filename from job title and company
            safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"cover_letter_{safe_company}_{safe_title}.txt"
            filename = filename.replace(" ", "_").lower()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        return filename
