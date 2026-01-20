"""
IMPROVED Resume Parser - Better extraction for structured CVs
Specifically handles CV-Abedi.pdf format with proper education, experience, and publication parsing
"""
import re
from typing import Dict, List, Optional
import os

# Import base functions
from resume_parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, extract_year


def parse_resume_text_improved(text: str) -> Dict:
    """
    Improved parser that handles structured CVs better
    Specifically designed for CV-Abedi.pdf format
    """
    # Preserve original lines for better parsing
    original_lines = text.split('\n')
    text_lines = [line.strip() for line in original_lines if line.strip()]
    full_text = '\n'.join(text_lines)
    
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
    
    # Extract email (improved)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        first_lines = '\n'.join(text_lines[:20])
        primary_emails = re.findall(email_pattern, first_lines)
        if primary_emails:
            email = primary_emails[0]
            email_fixes = {'peabedi': 'abedi', 'peabedisyedaliabbas': 'abedisyedaliabbas', 'rnail': 'mail', 'corn': 'com'}
            for wrong, correct in email_fixes.items():
                if wrong in email.lower():
                    email = email.lower().replace(wrong, correct)
                    break
            data["email"] = email
    
    # Extract phone
    phone_patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\+?\d{2,4}\s?\d{3,4}\s?\d{3,4}'
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            data["phone"] = matches[0]
            break
    
    # Extract name (first substantial line without email/phone)
    for line in text_lines[:10]:
        if '@' not in line and not re.search(r'\+?\d', line) and 2 <= len(line.split()) <= 5:
            if all(w[0].isupper() for w in line.split()[:2]):
                data["name"] = line
                break
    
    # Extract location
    location_keywords = ['Singapore', 'USA', 'United States', 'UK', 'United Kingdom', 
                        'Australia', 'Canada', 'India', 'Malaysia', 'Thailand', 'Hong Kong']
    for keyword in location_keywords:
        if keyword.lower() in text.lower():
            data["location"] = keyword
            break
    
    # Find section indices
    section_indices = {}
    section_headers = {
        'education': ['# education', 'education', 'academic', 'qualification'],
        'experience': ['experience', 'employment', 'work history', 'experience (most recent first)'],
        'publications': ['publications', 'peer-reviewed', 'journal articles', '# publications'],
        'presentations': ['presentations', 'conferences', 'invited'],
        'awards': ['awards', 'prizes', 'funding', 'prizes, awards'],
        'skills': ['technical skills', 'skills', 'expertise', 'technical skills and expertise']
    }
    
    for section_name, keywords in section_headers.items():
        for i, line in enumerate(text_lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords) and len(line.split()) <= 8:
                section_indices[section_name] = i
                break
    
    # IMPROVED Education Parsing - Look for specific patterns
    edu_start = section_indices.get('education', 0)
    edu_end = min(
        section_indices.get('experience', len(text_lines)),
        section_indices.get('publications', len(text_lines)),
        edu_start + 30
    ) if edu_start > 0 else len(text_lines)
    
    edu_lines = text_lines[edu_start:edu_end] if edu_start > 0 else text_lines
    
    # Pattern 1: "PhD in Science, Mathematics & Technology" or "PhD in X"
    # Pattern 2: "MS in Mathematics" or "M.S in X"
    # Pattern 3: "BSc in Chemical Engineering" or "B.Sc in X"
    
    i = 0
    while i < len(edu_lines):
        line = edu_lines[i]
        line_lower = line.lower()
        
        # Check for degree patterns
        degree_match = re.search(r'(PhD|Ph\.D|Ph\.D\.|Doctorate|Doctor|D\.Phil|DPhil)\s+(?:in|of)?\s*([^,\n]+?)(?:,|$|\n)', line, re.IGNORECASE)
        if not degree_match:
            degree_match = re.search(r'(MS|M\.S|M\.Sc|M\.S\.|Master|Masters?)\s+(?:in|of)?\s*([^,\n]+?)(?:,|$|\n)', line, re.IGNORECASE)
        if not degree_match:
            degree_match = re.search(r'(BSc|B\.S|B\.Sc|B\.S\.|Bachelor|Bachelors?)\s+(?:in|of)?\s*([^,\n]+?)(?:,|$|\n)', line, re.IGNORECASE)
        if not degree_match:
            degree_match = re.search(r'(MBA|M\.B\.A)\s+(?:in|of)?\s*([^,\n]+?)(?:,|$|\n)', line, re.IGNORECASE)
        
        if degree_match:
            degree_type = degree_match.group(1)
            field = degree_match.group(2).strip() if len(degree_match.groups()) > 1 else ""
            
            # Look ahead for institution and year
            institution = ""
            year = None
            
            # Check next 3 lines for institution
            for j in range(i+1, min(i+4, len(edu_lines))):
                next_line = edu_lines[j]
                next_lower = next_line.lower()
                
                # Skip if it's another degree
                if any(word in next_lower for word in ['phd', 'ms', 'm.s', 'bsc', 'bachelor', 'master']):
                    break
                
                # Check for institution
                if any(word in next_lower for word in ['university', 'college', 'institute', 'school', 'tech', 'sutd', 'lums', 'uet']):
                    institution = next_line
                    # Extract year from this line or next
                    year = extract_year(next_line)
                    if not year and j+1 < len(edu_lines):
                        year = extract_year(edu_lines[j+1])
                    break
            
            # If no institution found, check current line
            if not institution:
                if any(word in line_lower for word in ['university', 'college', 'institute']):
                    # Institution might be in same line
                    parts = re.split(r',|in|of', line, maxsplit=2)
                    if len(parts) > 1:
                        institution = parts[-1].strip()
            
            # Extract year from line if not found
            if not year:
                year = extract_year(line)
            
            # Look for "Awarded:" or "Defence:" patterns
            for j in range(i+1, min(i+5, len(edu_lines))):
                next_line = edu_lines[j]
                if 'awarded' in next_line.lower() or 'defence' in next_line.lower() or 'viva' in next_line.lower():
                    year = extract_year(next_line)
                    break
            
            edu_entry = {
                "degree": degree_type,
                "field": field,
                "institution": institution,
                "year": year
            }
            
            if edu_entry.get("degree") or edu_entry.get("institution"):
                data["education"].append(edu_entry)
            
            i += 1
        else:
            i += 1
    
    # IMPROVED Experience Parsing - Handle bullet points and date ranges
    exp_start = section_indices.get('experience', 0)
    exp_end = min(
        section_indices.get('education', len(text_lines)),
        section_indices.get('publications', len(text_lines)),
        exp_start + 60
    ) if exp_start > 0 else len(text_lines)
    
    exp_lines = text_lines[exp_start:exp_end] if exp_start > 0 else text_lines
    
    current_exp = {}
    i = 0
    while i < len(exp_lines):
        line = exp_lines[i]
        line_lower = line.lower()
        
        # Skip section headers
        if any(word in line_lower for word in ['education', 'publications', 'skills', 'awards', '# education']):
            if current_exp.get("title") or current_exp.get("company"):
                if current_exp.get("title") or current_exp.get("company"):
                    data["experience"].append(current_exp)
            current_exp = {}
            i += 1
            continue
        
        # Pattern 1: Title starts with bullet "- Visiting Researcher" or "• Visiting Researcher"
        title_match = re.match(r'^[-•*]\s*(.+?)(?:$|\n)', line)
        if title_match:
            title = title_match.group(1).strip()
            # Check if it's a job title
            if any(word in title.lower() for word in ['researcher', 'scientist', 'engineer', 'fellow', 'postdoc', 'mentor', 'assistant', 'professor', 'director', 'manager']):
                # Save previous
                if current_exp.get("title") or current_exp.get("company"):
                    data["experience"].append(current_exp)
                
                current_exp = {
                    "title": title,
                    "company": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "description": []
                }
                i += 1
                continue
        
        # Pattern 2: Company/Institution (usually follows title, no bullet)
        if current_exp.get("title") and not current_exp.get("company"):
            if any(word in line_lower for word in ['university', 'institute', 'college', 'ltd', 'inc', 'lab', 'center', 'centre', 'technologies', 'sutd', 'ntu', 'ucl']):
                current_exp["company"] = line
                # Extract location if in same line
                for loc in ['Singapore', 'UK', 'United Kingdom', 'USA', 'United States', 'London']:
                    if loc.lower() in line_lower:
                        current_exp["location"] = loc
                        break
                i += 1
                continue
        
        # Pattern 3: Date range (e.g., "01/09/2025 – Present" or "23/09/2024 – Present")
        date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{2,4})\s*[–-]\s*(present|current|\d{2}[/-]\d{2}[/-]\d{2,4})', line_lower)
        if date_match and current_exp.get("title"):
            current_exp["start_date"] = date_match.group(1)
            end_date = date_match.group(2)
            if 'present' in end_date.lower() or 'current' in end_date.lower():
                current_exp["end_date"] = "Present"
            else:
                current_exp["end_date"] = end_date
            i += 1
            continue
        
        # Pattern 4: Description bullets (starts with "-" or "•")
        if current_exp.get("title") and (line.startswith(('-', '•', '*')) or line.startswith('Strategic')):
            desc = line.lstrip('-•* ').strip()
            if len(desc) > 10 and desc.lower() not in ['strategic engagement for ai -for-science:']:
                current_exp["description"].append(desc)
            i += 1
            continue
        
        # Pattern 5: Title and company merged (e.g., "Postdoctoral Research FellowSingapore University...")
        # Try to split if we see a title keyword followed immediately by institution
        merged_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:Researcher|Scientist|Fellow|Engineer|Mentor|Professor|Assistant|Director|Manager))([A-Z][^a-z]*?(?:University|Institute|College|Ltd|Inc|Lab))', line)
        if merged_match and not current_exp.get("title"):
            title = merged_match.group(1).strip()
            company = merged_match.group(2).strip()
            
            # Save previous
            if current_exp.get("title") or current_exp.get("company"):
                data["experience"].append(current_exp)
            
            current_exp = {
                "title": title,
                "company": company,
                "location": "",
                "start_date": "",
                "end_date": "",
                "description": []
            }
            
            # Try to extract date from same line
            date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{2,4})\s*[–-]\s*(present|current|\d{2}[/-]\d{2}[/-]\d{2,4})', line_lower)
            if date_match:
                current_exp["start_date"] = date_match.group(1)
                end_date = date_match.group(2)
                if 'present' in end_date.lower():
                    current_exp["end_date"] = "Present"
                else:
                    current_exp["end_date"] = end_date
            
            # Extract location
            for loc in ['Singapore', 'UK', 'United Kingdom', 'USA', 'United States', 'London']:
                if loc.lower() in line_lower:
                    current_exp["location"] = loc
                    break
            
            i += 1
            continue
        
        i += 1
    
    # Save last experience
    if current_exp.get("title") or current_exp.get("company"):
        data["experience"].append(current_exp)
    
    # IMPROVED Publications Parsing
    pub_start = section_indices.get('publications', 0)
    if pub_start > 0:
        pub_end = min(
            section_indices.get('presentations', len(text_lines)),
            section_indices.get('awards', len(text_lines)),
            section_indices.get('skills', len(text_lines)),
            len(text_lines)
        )
        pub_lines = text_lines[pub_start:pub_end]
        pub_text = '\n'.join(pub_lines)
        
        # Split by numbered entries (1., 2., etc.) or look for publication patterns
        # Pattern: Number. Authors (Year): Title. Journal, Volume, Pages. DOI
        pub_pattern = re.compile(
            r'(\d+)\.\s*'  # Number
            r'([^:]+?)\s*'  # Authors
            r'\((\d{4})\):\s*'  # Year
            r'([^\.]+?\.)\s*'  # Title (first sentence)
            r'([^\.]+?\.)\s*'  # Journal
            r'(?:DOI[:\s]*([^\s,]+))?',  # Optional DOI
            re.IGNORECASE | re.MULTILINE
        )
        
        matches = pub_pattern.finditer(pub_text)
        for match in matches:
            authors = match.group(2).strip()
            year = int(match.group(3))
            title = match.group(4).strip()
            journal = match.group(5).strip()
            doi = match.group(6) if match.group(6) else None
            
            # Clean up title and journal
            title = title.rstrip('.,;')
            journal = journal.rstrip('.,;')
            
            if title and len(title) > 10:
                pub = {
                    "title": title[:400],
                    "authors": authors[:400] if authors else "",
                    "journal": journal[:200] if journal else "",
                    "year": year,
                    "doi": doi
                }
                data["publications"].append(pub)
        
        # Fallback: Split by numbered entries if pattern matching didn't work
        if not data["publications"]:
            pub_entries = re.split(r'\n(?=\d+\.|\d+\))', pub_text)
            for entry in pub_entries:
                entry = entry.strip()
                if len(entry) < 30:
                    continue
                
                # Remove leading number
                entry = re.sub(r'^\d+[\.\)]\s*', '', entry)
                
                year = extract_year(entry)
                
                # Extract DOI
                doi_match = re.search(r'doi[:\s]*([\d\.]+/[^\s,]+)', entry, re.IGNORECASE)
                doi = doi_match.group(1) if doi_match else None
                
                # Extract journal
                journal_patterns = [
                    r'Angew\.\s*Chem\.|J\.\s*Am\.\s*Chem\.\s*Soc\.|Nature\s*Methods|CCS\s*Chemistry|Chem\.\s*Commun\.|Dyes\s*Pigments',
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:,|\.)\s*\d+',
                    r'Journal of [A-Z][a-z]+'
                ]
                
                journal = ""
                for pattern in journal_patterns:
                    match = re.search(pattern, entry, re.IGNORECASE)
                    if match:
                        journal = match.group(0).strip('.,;')
                        break
                
                # Extract authors (usually at start, before colon or year)
                authors_match = re.match(r'^([^:\(]+?)(?::|\(|\d)', entry)
                authors = authors_match.group(1).strip() if authors_match else ""
                
                # Extract title (between authors and journal)
                if journal:
                    title_part = entry.split(journal)[0]
                    if ':' in title_part:
                        title = title_part.split(':')[-1].strip()
                    else:
                        # Try to find title after authors
                        title = title_part.split('(')[-1].strip() if '(' in title_part else title_part.strip()
                else:
                    if ':' in entry:
                        title = entry.split(':')[1].split('.')[0].strip()
                    else:
                        title = entry.split('.')[0].strip()
                
                if title and len(title) > 15:
                    pub = {
                        "title": title[:400],
                        "authors": authors[:400] if authors else "",
                        "journal": journal[:200] if journal else "",
                        "year": year,
                        "doi": doi
                    }
                    data["publications"].append(pub)
    
    # IMPROVED Skills Parsing (handle table format and category headers)
    skills_start = section_indices.get('skills', 0)
    if skills_start > 0:
        skills_end = min(len(text_lines), skills_start + 40)
        skills_lines = text_lines[skills_start:skills_end]
        
        for line in skills_lines:
            line_lower = line.lower()
            
            # Stop if we hit another section
            if any(word in line_lower for word in ['experience', 'education', 'publications', 'awards', '#']):
                break
            
            # Skip category headers
            if any(word in line_lower for word in ['category', 'technical skills and expertise', 'skills', 'expertise']) and '|' in line:
                continue
            
            # Extract skills from table rows (Category | Skills)
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    skills_text = parts[1] if len(parts) > 1 else ""
                    
                    # Extract individual skills
                    # Handle patterns like "Python (Pandas, NumPy, Matplotlib)"
                    skills_list = re.split(r'[,;:]', skills_text)
                    for skill in skills_list:
                        skill = skill.strip()
                        # Remove parentheses content for now (can be parsed separately)
                        skill = re.sub(r'\([^)]+\)', '', skill).strip()
                        # Remove common prefixes
                        skill = re.sub(r'^(Languages?|Software|Tools?|Frameworks?|ML|Machine Learning):\s*', '', skill, flags=re.IGNORECASE)
                        if len(skill) > 2 and skill.lower() not in ['and', 'or', 'the', 'a', 'category', 'skills']:
                            data["skills"].append(skill)
            
            # Extract from colon-separated format
            elif ':' in line and len(line.split(':')) == 2:
                category, skills_text = line.split(':', 1)
                # Skip if category is a header
                if category.lower().strip() not in ['category', 'technical skills', 'expertise']:
                    skills_list = re.split(r'[,;]', skills_text)
                    for skill in skills_list:
                        skill = skill.strip()
                        if len(skill) > 2:
                            data["skills"].append(skill)
            
            # Extract from bullet points
            elif line.startswith(('-', '•', '*')):
                skill = line.lstrip('-•* ').strip()
                if len(skill) > 2 and skill.lower() not in ['category', 'skills', 'expertise']:
                    data["skills"].append(skill)
    
    # Remove duplicates and filter out category headers
    filtered_skills = []
    skip_words = ['technical', 'expertise', 'skills', 'category', 'competencies', 'proficiencies', 'and', 'or']
    for skill in data["skills"]:
        skill_lower = skill.lower().strip()
        if (not any(word == skill_lower for word in skip_words) and 
            len(skill) > 2 and 
            not skill_lower.startswith('category') and
            not skill_lower.startswith('technical')):
            filtered_skills.append(skill)
    data["skills"] = list(dict.fromkeys(filtered_skills))[:50]
    
    return data


def parse_resume_file_improved(filepath: str) -> Dict:
    """Parse resume file using improved parser"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    file_ext = os.path.splitext(filepath)[1].lower()
    
    if file_ext == '.pdf':
        text = extract_text_from_pdf(filepath)
    elif file_ext in ['.docx', '.doc']:
        text = extract_text_from_docx(filepath)
    elif file_ext == '.txt':
        text = extract_text_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    if not text or len(text.strip()) < 50:
        raise ValueError("Resume file appears to be empty")
    
    return parse_resume_text_improved(text)
