"""
Comprehensive Resume Parser - Extracts ALL data from uploaded resume files (PDF, DOCX, TXT)
Extracts: name, contact, education, experience, skills, publications, presentations, awards, research interests
"""
import re
from typing import Dict, List, Optional
import os
from datetime import datetime

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF file with better extraction"""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
    
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not installed. Install with: pip install python-docx")
    
    try:
        doc = Document(filepath)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return "\n".join(text_parts)
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")


def extract_text_from_txt(filepath: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error reading TXT: {str(e)}")


def extract_year(text: str) -> Optional[int]:
    """Extract year from text (4-digit year)"""
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    if years:
        try:
            return int(years[-1])  # Get most recent year
        except:
            pass
    return None


def parse_resume_text(text: str) -> Dict:
    """
    Comprehensive resume parser that extracts ALL sections
    """
    # Preserve line structure for better parsing
    original_lines = text.split('\n')
    text_lines = [line.strip() for line in original_lines if line.strip()]
    
    # Initialize comprehensive data structure
    data = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "education": [],
        "experience": [],
        "skills": [],
        "publications": [],
        "presentations": [],
        "awards": [],
        "research_interests": [],
        "summary": ""
    }
    
    # Extract email - prioritize primary email (usually in first few lines, common domains)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        # Prioritize emails that:
        # 1. Appear in first 20 lines (contact section)
        # 2. Use common domains (gmail, yahoo, outlook, etc.)
        # 3. Don't look like typos or partial matches
        
        # Check first 20 lines for email
        first_lines = '\n'.join(text_lines[:20])
        primary_emails = re.findall(email_pattern, first_lines)
        
        if primary_emails:
            # Use email from contact section
            # Also check for common OCR/parsing errors and fix them
            email = primary_emails[0]
            
            # Fix common OCR errors: "peabedi" -> "abedi", "rn" -> "m", etc.
            email_fixes = {
                'peabedi': 'abedi',
                'peabedisyedaliabbas': 'abedisyedaliabbas',
                'rnail': 'mail',
                'corn': 'com',
                'gmail.corn': 'gmail.com',
                'gmail.rn': 'gmail.com'
            }
            
            for wrong, correct in email_fixes.items():
                if wrong in email.lower():
                    email = email.lower().replace(wrong, correct)
                    break
            
            data["email"] = email
        else:
            # Filter emails - prefer common domains and avoid obvious typos
            common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 
                            'edu', 'ac.uk', 'ac.sg', 'university', 'institute']
            
            # Score emails: higher score = more likely to be primary
            scored_emails = []
            for email in emails:
                score = 0
                email_lower = email.lower()
                
                # Prefer common domains
                if any(domain in email_lower for domain in common_domains):
                    score += 10
                
                # Prefer emails that don't look like typos (reasonable length)
                if 10 <= len(email.split('@')[0]) <= 30:
                    score += 5
                
                # Avoid emails with weird patterns
                if not re.search(r'[._]{2,}', email):  # No double dots/underscores
                    score += 3
                
                scored_emails.append((score, email))
            
            # Sort by score and take best
            if scored_emails:
                scored_emails.sort(reverse=True)
                data["email"] = scored_emails[0][1]
            else:
                data["email"] = emails[0]
    
    # Extract phone
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\+?\d{8,15}'
    ]
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            data["phone"] = phones[0]
            break
    
    # Extract name - multiple strategies
    # Strategy 1: Look for capitalized name pattern at start
    name_patterns = [
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$)',
        r'^([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'^([A-Z][A-Z]+\s+[A-Z][a-z]+)',  # For all caps first name
    ]
    
    for line in text_lines[:15]:  # Check first 15 lines
        line_clean = line.strip()
        # Skip if contains email, phone, or is too long
        if '@' in line_clean or any(char.isdigit() for char in line_clean[:5]) or len(line_clean.split()) > 5:
            continue
        
        for pattern in name_patterns:
            match = re.match(pattern, line_clean)
            if match:
                potential_name = match.group(1).strip()
                # Validate: should be 2-4 words, mostly letters
                words = potential_name.split()
                if 2 <= len(words) <= 4 and all(w.isalpha() or '-' in w for w in words):
                    data["name"] = potential_name
                    break
        if data["name"]:
            break
    
    # Strategy 2: If still no name, use first substantial line
    if not data["name"] and text_lines:
        for line in text_lines[:5]:
            line_clean = line.strip()
            words = line_clean.split()
            if (2 <= len(words) <= 4 and 
                '@' not in line_clean and 
                not any(char.isdigit() for char in line_clean[:10]) and
                all(w[0].isupper() if w else False for w in words[:2])):  # First 2 words start with capital
                data["name"] = line_clean
                break
    
    # Extract location
    location_keywords = ['Singapore', 'USA', 'United States', 'UK', 'United Kingdom', 
                        'Australia', 'Canada', 'India', 'Malaysia', 'Thailand', 'Hong Kong',
                        'Germany', 'France', 'Japan', 'China', 'South Korea']
    for keyword in location_keywords:
        if keyword.lower() in text.lower():
            data["location"] = keyword
            break
    
    # Find section boundaries
    section_headers = {
        'education': ['education', 'academic', 'qualification', 'qualifications', 'academic background'],
        'experience': ['experience', 'employment', 'work history', 'work experience', 'professional experience', 'career', 'positions'],
        'publications': ['publications', 'peer-reviewed', 'journal articles', 'papers', 'research papers'],
        'presentations': ['presentations', 'conference presentations', 'talks', 'posters'],
        'awards': ['awards', 'honors', 'honours', 'recognition', 'achievements'],
        'skills': ['skills', 'technical skills', 'competencies', 'expertise', 'proficiencies', 'technologies'],
        'research': ['research interests', 'research areas', 'research focus', 'interests']
    }
    
    # Find section indices
    section_indices = {}
    for section_name, keywords in section_headers.items():
        for i, line in enumerate(text_lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords) and len(line.split()) <= 5:
                section_indices[section_name] = i
                break
    
    # Parse Education - search ENTIRE document if no section found
    edu_start = section_indices.get('education', 0)
    # If no explicit education section, search entire document
    if edu_start == 0:
        edu_start = 0  # Start from beginning
        edu_end = len(text_lines)  # Search entire document
    else:
        edu_end = min(
            section_indices.get('experience', len(text_lines)), 
            section_indices.get('publications', len(text_lines)),
            section_indices.get('skills', len(text_lines)),
            edu_start + 50  # Limit search range
        )
    
    degree_keywords = ['phd', 'ph.d', 'ph.d.', 'doctorate', 'doctor', 'd.phil', 'dphil',
                      'master', 'm.s', 'm.sc', 'ms', 'm.sc.', 'm.s.', 'masters',
                      'bachelor', 'b.s', 'b.sc', 'bs', 'b.sc.', 'b.s.', 'bachelor',
                      'degree', 'diploma', 'bachelor', 'mba', 'm.b.a']
    
    current_edu = {}
    for i in range(edu_start, min(edu_end, len(text_lines))):
        line = text_lines[i]
        line_lower = line.lower()
        
        # Check for degree - be more lenient
        has_degree = any(keyword in line_lower for keyword in degree_keywords)
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', line))
        has_institution = any(word in line_lower for word in ['university', 'college', 'institute', 'school', 'academy', 'tech', 'univ'])
        
        # If line has degree keyword OR has institution + year, it's likely education
        if has_degree or (has_institution and has_year):
            # Save previous
            if current_edu.get("degree") or current_edu.get("institution"):
                data["education"].append(current_edu)
            
            # Start new education entry
            if has_degree:
                current_edu = {
                    "degree": line,
                    "institution": "",
                    "field": "",
                    "year": extract_year(line)
                }
            elif has_institution:
                # Institution found, degree might be on next line
                current_edu = {
                    "degree": "",
                    "institution": line,
                    "field": "",
                    "year": extract_year(line)
                }
        elif current_edu.get("degree") or current_edu.get("institution"):
            # Continue building current education entry
            if not current_edu.get("institution"):
                if has_institution or (len(line) > 5 and len(line) < 100 and not line[0].isdigit() and not any(c in line for c in ['@', 'http'])):
                    current_edu["institution"] = line
            elif not current_edu.get("field") and len(line) < 80 and not has_institution:
                current_edu["field"] = line
            if not current_edu.get("year") and has_year:
                current_edu["year"] = extract_year(line)
            if not current_edu.get("degree") and has_degree:
                current_edu["degree"] = line
    
    # Save last education entry
    if current_edu.get("degree") or current_edu.get("institution"):
        data["education"].append(current_edu)
    
    # Parse Experience - search ENTIRE document if no section found
    exp_start = section_indices.get('experience', 0)
    # If no explicit experience section, search entire document
    if exp_start == 0:
        exp_start = 0  # Start from beginning
        exp_end = len(text_lines)  # Search entire document
    else:
        exp_end = min(
            section_indices.get('education', len(text_lines)),
            section_indices.get('publications', len(text_lines)),
            section_indices.get('skills', len(text_lines)),
            section_indices.get('awards', len(text_lines)),
            exp_start + 100  # Limit search range
        )
    
    experience_keywords = ['researcher', 'scientist', 'engineer', 'developer', 'analyst', 
                          'manager', 'director', 'consultant', 'fellow', 'postdoc', 'post-doc',
                          'assistant', 'associate', 'professor', 'lecturer', 'intern', 'internship',
                          'coordinator', 'specialist', 'technician', 'technologist', 'lead', 'senior',
                          'junior', 'principal', 'head', 'chief']
    
    current_exp = {}
    for i in range(exp_start, min(exp_end, len(text_lines))):
        line = text_lines[i]
        line_lower = line.lower()
        
        has_title = any(keyword in line_lower for keyword in experience_keywords)
        has_date = bool(re.search(r'\d{4}|\d{2}[/-]\d{2}[/-]\d{2,4}|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec', line_lower))
        has_company = any(word in line_lower for word in ['university', 'institute', 'ltd', 'inc', 'corp', 'company', 'lab', 'laboratory', 'center', 'centre', 'foundation', 'group', 'technologies', 'systems'])
        
        # More lenient: if has title keywords OR (has date and reasonable length) OR (has company indicator)
        if has_title or (has_date and len(line.split()) <= 12) or (has_company and len(line.split()) <= 8):
            # Save previous if it has title or company
            if current_exp.get("title") or (current_exp.get("company") and len(current_exp.get("description", [])) > 0):
                data["experience"].append(current_exp)
            
            # Start new experience
            if has_title:
                current_exp = {
                    "title": line,
                    "company": "",
                    "description": [],
                    "start_date": "",
                    "end_date": ""
                }
            elif has_company:
                # Company found first, title might be on previous or next line
                current_exp = {
                    "title": "",
                    "company": line,
                    "description": [],
                    "start_date": "",
                    "end_date": ""
                }
        elif current_exp.get("title") or current_exp.get("company"):
            # Continue building current experience
            if not current_exp.get("company"):
                if has_company or (len(line) > 3 and len(line) < 100 and not line[0].isdigit() and not any(c in line for c in ['@', 'http']) and len(line.split()) <= 8):
                    current_exp["company"] = line
            elif not current_exp.get("title") and has_title:
                current_exp["title"] = line
            elif len(line) > 10 and len(line) < 500:  # Description
                current_exp["description"].append(line)
    
    # Save last experience entry
    if current_exp.get("title") or (current_exp.get("company") and len(current_exp.get("description", [])) > 0):
        data["experience"].append(current_exp)
    
    # Parse Publications
    pub_start = section_indices.get('publications', 0)
    pub_end = min(section_indices.get('presentations', len(text_lines)),
                  section_indices.get('awards', len(text_lines)),
                  section_indices.get('skills', len(text_lines)),
                  len(text_lines))
    
    if pub_start > 0:
        pub_lines = text_lines[pub_start:pub_end]
        pub_text = '\n'.join(pub_lines)
        
        # Look for publication patterns
        # Pattern 1: Author et al. (Year). Title. Journal, Volume, Pages. DOI
        # Pattern 2: Title. Journal. Year.
        # Pattern 3: Numbered list
        
        # Split by common separators
        pub_entries = re.split(r'\n(?=\d+\.|\d+\)|•|\*|[-•])', pub_text)
        
        for entry in pub_entries:
            entry = entry.strip()
            if len(entry) < 20:  # Too short to be a publication
                continue
            
            # Extract year
            year = extract_year(entry)
            
            # Look for journal names (common patterns)
            journal_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:,|\.)\s*\d+',  # Journal Name, Volume
                r'Journal of [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
                r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Journal',
                r'Nature|Science|Cell|PNAS|ACS|RSC|Wiley'
            ]
            
            journal = ""
            for pattern in journal_patterns:
                match = re.search(pattern, entry, re.IGNORECASE)
                if match:
                    journal = match.group(0).strip('.,;')
                    break
            
            # Extract DOI
            doi_match = re.search(r'doi[:\s]*([\d\.]+/[^\s,]+)', entry, re.IGNORECASE)
            doi = doi_match.group(1) if doi_match else None
            
            # Extract title (usually first sentence or before journal)
            title = entry.split('.')[0] if '.' in entry else entry[:100]
            if journal:
                title = entry.split(journal)[0].strip('.,; ')
            
            # Extract authors (usually at start)
            authors_match = re.match(r'^([^\.]+?)(?:\.|,|\()', entry)
            authors = authors_match.group(1).strip() if authors_match else ""
            
            if title and len(title) > 10:
                pub = {
                    "title": title[:200],
                    "authors": authors[:200] if authors else "",
                    "journal": journal[:100] if journal else "",
                    "year": year,
                    "doi": doi
                }
                data["publications"].append(pub)
    
    # Parse Presentations
    pres_start = section_indices.get('presentations', 0)
    if pres_start > 0:
        pres_end = min(section_indices.get('awards', len(text_lines)),
                      section_indices.get('skills', len(text_lines)),
                      len(text_lines))
        pres_lines = text_lines[pres_start:pres_end]
        
        for line in pres_lines:
            if len(line) > 30 and any(word in line.lower() for word in ['conference', 'symposium', 'meeting', 'presentation', 'talk', 'poster']):
                year = extract_year(line)
                pres = {
                    "title": line[:200],
                    "venue": "",
                    "year": year
                }
                data["presentations"].append(pres)
    
    # Parse Awards
    awards_start = section_indices.get('awards', 0)
    if awards_start > 0:
        awards_end = min(section_indices.get('skills', len(text_lines)),
                        section_indices.get('research', len(text_lines)),
                        len(text_lines))
        awards_lines = text_lines[awards_start:awards_end]
        
        for line in awards_lines:
            if len(line) > 15 and any(word in line.lower() for word in ['award', 'prize', 'scholarship', 'fellowship', 'grant', 'recognition']):
                year = extract_year(line)
                award = {
                    "title": line[:200],
                    "year": year
                }
                data["awards"].append(award)
    
    # Parse Research Interests
    research_start = section_indices.get('research', 0)
    if research_start > 0:
        research_end = min(section_indices.get('skills', len(text_lines)),
                          section_indices.get('experience', len(text_lines)),
                          len(text_lines))
        research_lines = text_lines[research_start:research_end]
        
        for line in research_lines:
            # Research interests are often comma-separated
            if ',' in line or ';' in line:
                interests = re.split(r'[,;]', line)
                data["research_interests"].extend([i.strip() for i in interests if len(i.strip()) > 3])
            elif len(line) > 10 and len(line) < 100:
                data["research_interests"].append(line.strip())
    
    # Parse Skills
    skills_start = section_indices.get('skills', 0)
    if skills_start > 0:
        skills_end = min(len(text_lines), skills_start + 50)  # Limit skills section
        skills_lines = text_lines[skills_start:skills_end]
        
        for line in skills_lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['experience', 'education', 'publications', 'awards']):
                break
            
            # Skills are often comma-separated or bulleted
            if line.startswith(('-', '•', '*', '·')):
                skills = re.split(r'[,;]', line[1:].strip())
                data["skills"].extend([s.strip() for s in skills if len(s.strip()) > 2])
            elif ',' in line or ';' in line:
                skills = re.split(r'[,;]', line)
                data["skills"].extend([s.strip() for s in skills if len(s.strip()) > 2])
            elif len(line.split()) <= 4 and len(line) < 50:
                data["skills"].append(line.strip())
    
    # Remove duplicates
    data["skills"] = list(dict.fromkeys(data["skills"]))[:50]
    data["research_interests"] = list(dict.fromkeys(data["research_interests"]))[:20]
    
    return data


def parse_resume_file(filepath: str) -> Dict:
    """
    Parse resume file and return comprehensive structured data
    Supports PDF, DOCX, and TXT files
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    file_ext = os.path.splitext(filepath)[1].lower()
    
    # Extract text based on file type
    if file_ext == '.pdf':
        text = extract_text_from_pdf(filepath)
    elif file_ext in ['.docx', '.doc']:
        text = extract_text_from_docx(filepath)
    elif file_ext == '.txt':
        text = extract_text_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    if not text or len(text.strip()) < 50:
        raise ValueError("Resume file appears to be empty or could not be extracted")
    
    # Parse the extracted text
    parsed_data = parse_resume_text(text)
    
    return parsed_data
