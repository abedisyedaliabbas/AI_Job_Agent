"""
Enhanced Skill Parser - Comprehensive skill extraction from resumes
Extracts skills from multiple sources with intelligent categorization
"""
import re
from typing import List, Dict, Set, Tuple
from collections import Counter


class EnhancedSkillParser:
    """
    Comprehensive skill parser that extracts skills from:
    1. Explicit skills sections
    2. Experience descriptions
    3. Education fields
    4. Publications and research areas
    5. Technical terms throughout the document
    """
    
    # Comprehensive list of known technical skills by category
    KNOWN_SKILLS = {
        'Programming Languages': {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'r', 'matlab', 'scala', 
            'go', 'rust', 'swift', 'kotlin', 'php', 'ruby', 'perl', 'bash', 'shell', 'powershell',
            'sql', 'html', 'css', 'sass', 'less', 'xml', 'json', 'yaml'
        },
        'Computational Chemistry': {
            'dft', 'tddft', 'gaussian', 'orca', 'vasp', 'materials studio', 'gromacs', 'amber',
            'charmm', 'namd', 'lammps', 'cp2k', 'quantum espresso', 'molpro', 'molcas', 'turbomole',
            'psi4', 'qchem', 'gamess', 'nwchem', 'crystal', 'cpmd', 'ab initio', 'density functional',
            'molecular dynamics', 'md', 'monte carlo', 'mc', 'quantum mechanics', 'qm', 'mm', 'qm/mm',
            'semi-empirical', 'hartree-fock', 'hf', 'mp2', 'ccsd', 'ccsd(t)', 'caspt2', 'mrcisd',
            'excited states', 'tddft', 'cis', 'casci', 'caspt2', 'eom-ccsd', 'adc', 'bet-sol',
            'pcm', 'cosmo', 'smd', 'solvation', 'basis sets', 'pople', 'dunning', 'aug-cc-pvdz',
            'sto-3g', '6-31g', 'lanl2dz', 'def2', 'sadlej', 'pseudopotentials', 'ecp'
        },
        'Machine Learning & AI': {
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 
            'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop', 'scala', 'xgboost', 'lightgbm',
            'catboost', 'neural networks', 'deep learning', 'cnn', 'rnn', 'lstm', 'transformer',
            'bert', 'gpt', 'nlp', 'computer vision', 'opencv', 'pytorch', 'tensorflow', 'keras'
        },
        'Software & Tools': {
            'linux', 'unix', 'windows', 'macos', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'git', 'svn', 'mercurial', 'jira', 'confluence', 'slack', 'trello', 'asana',
            'vscode', 'pycharm', 'intellij', 'eclipse', 'vim', 'emacs', 'sublime', 'atom'
        },
        'Databases': {
            'mongodb', 'postgresql', 'mysql', 'sqlite', 'oracle', 'sql server', 'redis', 
            'elasticsearch', 'cassandra', 'dynamodb', 'neo4j', 'influxdb', 'couchdb'
        },
        'Web Technologies': {
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
            'fastapi', 'laravel', 'rails', 'asp.net', 'next.js', 'nuxt.js', 'gatsby',
            'webpack', 'babel', 'npm', 'yarn', 'grunt', 'gulp'
        },
        'Data Science': {
            'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'bokeh',
            'jupyter', 'rstudio', 'tableau', 'power bi', 'qlik', 'sas', 'spss', 'stata',
            'excel', 'vba', 'sql', 'hive', 'pig', 'spark', 'hadoop'
        },
        'Cloud & DevOps': {
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'prometheus', 'grafana',
            'elk stack', 'splunk', 'datadog', 'new relic'
        },
        'Scientific Computing': {
            'matlab', 'mathematica', 'maple', 'r', 'python', 'julia', 'fortran', 'idl',
            'origin', 'igor pro', 'labview', 'comsol', 'ansys', 'abaqus', 'fluent'
        },
        'Visualization': {
            'matplotlib', 'seaborn', 'plotly', 'bokeh', 'd3.js', 'ggplot2', 'tableau',
            'power bi', 'qlik', 'vega', 'vega-lite', 'observable', 'rawgraphs'
        }
    }
    
    # Common skill patterns to extract
    SKILL_PATTERNS = [
        # Acronyms (2-5 uppercase letters) - likely technical terms
        r'\b([A-Z]{2,5})\b',
        # Software names (capitalized, 3+ chars, not common words)
        r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)*)\b',
        # Technical terms with numbers/versions
        r'\b([A-Za-z]+\s*\d+\.?\d*)\b',
        # Compound technical terms
        r'\b([a-z]+-[a-z]+(?:-[a-z]+)?)\b',
        # File extensions (indicate software knowledge)
        r'\.([a-z]{2,4})\b'
    ]
    
    # Words to filter out (not skills)
    FILTER_WORDS = {
        'the', 'and', 'or', 'for', 'with', 'from', 'that', 'this', 'are', 'was', 'in', 'at', 'on',
        'to', 'of', 'a', 'an', 'by', 'as', 'is', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall',
        'experience', 'knowledge', 'familiarity', 'understanding', 'proficient', 'skilled',
        'expert', 'advanced', 'intermediate', 'beginner', 'novice', 'using', 'utilizing',
        'employing', 'leveraging', 'developing', 'creating', 'designing', 'implementing',
        'conducting', 'performing', 'leading', 'managing', 'organizing', 'coordinating',
        'actively', 'primarily', 'especially', 'particularly', 'specifically', 'including',
        'also', 'additionally', 'furthermore', 'moreover', 'however', 'therefore', 'thus',
        'density', 'stability', 'photostability', 'methodology', 'technique', 'approach',
        'method', 'system', 'application', 'software', 'technology', 'data', 'information',
        'research', 'study', 'analysis', 'development', 'project', 'work', 'position', 'role',
        'university', 'college', 'institute', 'department', 'laboratory', 'lab', 'center',
        'ntu', 'sutd', 'nus', 'ucl', 'mit', 'stanford', 'harvard', 'oxford', 'cambridge',
        'usa', 'uk', 'sg', 'phd', 'ms', 'bsc', 'masters', 'bachelor', 'doctorate'
    }
    
    # Category headers to ignore
    CATEGORY_HEADERS = {
        'technical expertise', 'technical skills', 'technical', 'expertise', 'skills',
        'competencies', 'proficiencies', 'capabilities', 'programming', 'languages',
        'software', 'tools', 'technologies', 'frameworks', 'libraries', 'platforms',
        'databases', 'methodologies', 'practices', 'concepts', 'domains', 'ics'
    }
    
    def __init__(self):
        self.all_skills = set()
        self.skill_categories = {}
    
    def parse_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Comprehensive skill extraction from resume text
        Returns dict with categories as keys and lists of skills as values
        """
        if not text:
            return {}
        
        text_lower = text.lower()
        skills_by_category = {cat: [] for cat in self.KNOWN_SKILLS.keys()}
        skills_by_category['Other'] = []
        
        # Method 1: Extract from known skills list
        for category, known_skills in self.KNOWN_SKILLS.items():
            for skill in known_skills:
                # Check for exact match or word boundary match
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    skills_by_category[category].append(skill.title() if ' ' not in skill else skill)
        
        # Method 2: Extract acronyms (2-5 uppercase letters)
        acronyms = re.findall(r'\b([A-Z]{2,5})\b', text)
        for acro in acronyms:
            acro_lower = acro.lower()
            # Filter out common non-skill acronyms
            if acro_lower not in self.FILTER_WORDS and len(acro) >= 2:
                # Try to categorize
                categorized = False
                for category, known_skills in self.KNOWN_SKILLS.items():
                    if any(acro_lower in skill.lower() for skill in known_skills):
                        skills_by_category[category].append(acro)
                        categorized = True
                        break
                if not categorized:
                    skills_by_category['Other'].append(acro)
        
        # Method 3: Extract capitalized technical terms (likely software/tools)
        # Look for capitalized words that appear multiple times or are in technical contexts
        capitalized_terms = re.findall(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)*)\b', text)
        term_counts = Counter(capitalized_terms)
        
        for term, count in term_counts.items():
            term_lower = term.lower()
            # Skip if it's a filter word or category header
            if term_lower in self.FILTER_WORDS or term_lower in self.CATEGORY_HEADERS:
                continue
            
            # Skip if it's too generic
            if term_lower in ['software', 'system', 'application', 'technology', 'method', 'approach']:
                continue
            
            # Skip if it looks like a sentence (has common sentence words)
            if any(word in term_lower for word in ['the', 'and', 'or', 'for', 'with', 'from']):
                continue
            
            # Check if it's a known skill
            categorized = False
            for category, known_skills in self.KNOWN_SKILLS.items():
                if any(term_lower in skill.lower() or skill.lower() in term_lower for skill in known_skills):
                    if term not in skills_by_category[category]:
                        skills_by_category[category].append(term)
                    categorized = True
                    break
            
            # If not categorized but appears multiple times or is in technical context, add to Other
            if not categorized and (count >= 2 or self._is_technical_context(term, text)):
                if term not in skills_by_category['Other']:
                    skills_by_category['Other'].append(term)
        
        # Method 4: Extract compound technical terms (e.g., "machine-learning", "deep-learning")
        compound_terms = re.findall(r'\b([a-z]+-[a-z]+(?:-[a-z]+)?)\b', text_lower)
        for term in compound_terms:
            # Check if it's a known skill
            for category, known_skills in self.KNOWN_SKILLS.items():
                if any(term in skill.lower() or skill.lower() in term for skill in known_skills):
                    skill_formatted = term.replace('-', ' ').title()
                    if skill_formatted not in skills_by_category[category]:
                        skills_by_category[category].append(skill_formatted)
                    break
        
        # Method 5: Extract from explicit skills section
        skills_section = self._extract_skills_section(text)
        if skills_section:
            section_skills = self._parse_skills_section(skills_section)
            for skill in section_skills:
                # Categorize the skill
                categorized = False
                for category, known_skills in self.KNOWN_SKILLS.items():
                    skill_lower = skill.lower()
                    if any(skill_lower in known_skill.lower() or known_skill.lower() in skill_lower 
                           for known_skill in known_skills):
                        if skill not in skills_by_category[category]:
                            skills_by_category[category].append(skill)
                        categorized = True
                        break
                if not categorized:
                    if skill not in skills_by_category['Other']:
                        skills_by_category['Other'].append(skill)
        
        # Remove duplicates and empty categories
        result = {}
        for category, skills in skills_by_category.items():
            unique_skills = list(dict.fromkeys(skills))  # Preserve order, remove duplicates
            if unique_skills:
                result[category] = unique_skills
        
        return result
    
    def _extract_skills_section(self, text: str) -> str:
        """Extract the skills section from resume text"""
        lines = text.split('\n')
        skills_start = None
        skills_end = None
        
        # Find skills section header
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(header in line_lower for header in [
                'skills', 'technical skills', 'technical expertise', 'competencies',
                'proficiencies', 'capabilities', 'expertise', 'qualifications'
            ]):
                skills_start = i
                break
        
        if skills_start is None:
            return ""
        
        # Find end of skills section (next major section)
        section_headers = ['experience', 'education', 'publications', 'awards', 'research', 'projects']
        for i in range(skills_start + 1, len(lines)):
            line_lower = lines[i].lower().strip()
            if any(header in line_lower for header in section_headers):
                if len(line_lower) < 50:  # Likely a section header
                    skills_end = i
                    break
        
        if skills_end is None:
            skills_end = min(skills_start + 30, len(lines))  # Limit to 30 lines
        
        return '\n'.join(lines[skills_start:skills_end])
    
    def _parse_skills_section(self, section_text: str) -> List[str]:
        """Parse skills from a skills section"""
        skills = []
        lines = section_text.split('\n')
        
        for line in lines[1:]:  # Skip header
            line = line.strip()
            if not line or len(line) < 2:
                continue
            
            # Remove bullet points and markers
            line = re.sub(r'^[-•*]\s*', '', line)
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            
            # Skip category headers
            line_lower = line.lower()
            if line_lower in self.CATEGORY_HEADERS:
                continue
            
            # Split by common delimiters
            line_skills = re.split(r'[,;|•]', line)
            for skill in line_skills:
                skill = skill.strip()
                if skill and len(skill) >= 2:
                    # Clean skill
                    skill = re.sub(r'^(proficient in|skilled in|experience with|knowledge of|familiar with)\s+', '', skill, flags=re.IGNORECASE)
                    skill = skill.strip('.,;:()[]{}')
                    
                    # Filter out non-skills
                    if skill.lower() not in self.FILTER_WORDS and skill.lower() not in self.CATEGORY_HEADERS:
                        if len(skill) >= 2:
                            skills.append(skill)
        
        return skills
    
    def _is_technical_context(self, term: str, text: str) -> bool:
        """Check if a term appears in a technical context"""
        # Look for technical keywords near the term
        technical_keywords = [
            'software', 'tool', 'framework', 'library', 'platform', 'language', 'technology',
            'using', 'utilizing', 'implementing', 'developing', 'programming', 'coding',
            'experience with', 'proficient in', 'skilled in', 'knowledge of'
        ]
        
        # Find positions of the term
        term_lower = term.lower()
        text_lower = text.lower()
        
        for match in re.finditer(re.escape(term_lower), text_lower):
            start, end = match.span()
            context = text_lower[max(0, start-50):min(len(text_lower), end+50)]
            
            if any(keyword in context for keyword in technical_keywords):
                return True
        
        return False
    
    def get_all_skills_flat(self, skills_by_category: Dict[str, List[str]]) -> List[str]:
        """Get all skills as a flat list"""
        all_skills = []
        for skills in skills_by_category.values():
            all_skills.extend(skills)
        return list(dict.fromkeys(all_skills))  # Remove duplicates, preserve order
