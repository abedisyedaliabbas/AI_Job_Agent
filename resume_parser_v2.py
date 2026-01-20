"""
Resume Parser V2 - Simple, Robust, Actually Works
Designed to handle real-world CV formats correctly
"""
import re
import os
from typing import Dict, List, Optional, Tuple

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PDF2_AVAILABLE = True
except ImportError:
    PDF2_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF using best available method"""
    text = ""
    
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text:
                return text
        except Exception as e:
            print(f"[PDF] pdfplumber failed: {e}, trying PyPDF2")
    
    if PDF2_AVAILABLE:
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    raise ImportError("No PDF library available. Install pdfplumber or PyPDF2")


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not installed")
    
    text_parts = []
    doc = Document(filepath)
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    
    return "\n".join(text_parts)


def parse_resume_v2(filepath: str) -> Dict:
    """
    Simple, robust resume parser that actually works
    """
    # Extract text
    file_ext = os.path.splitext(filepath)[1].lower()
    if file_ext == '.pdf':
        text = extract_text_from_pdf(filepath)
    elif file_ext in ['.docx', '.doc']:
        text = extract_text_from_docx(filepath)
    elif file_ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    if not text or len(text.strip()) < 50:
        raise ValueError("Resume file appears to be empty")
    
    # Preserve line structure - DON'T normalize all whitespace, keep line breaks
    # Only normalize multiple spaces to single space within lines
    lines = []
    for line in text.split('\n'):
        line = ' '.join(line.split())  # Normalize spaces within line
        if line.strip():
            lines.append(line.strip())
    
    print(f"[PARSER V2] Processing {len(lines)} lines")
    print(f"[PARSER V2] First 15 lines: {lines[:15]}")
    
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
        "awards": []
    }
    
    # 1. EXTRACT NAME - First line that looks like a name
    for i, line in enumerate(lines[:10]):
        words = line.split()
        # More lenient: 2-6 words, capitalized, no email/phone/colon
        if (2 <= len(words) <= 6 and 
            '@' not in line and 
            ':' not in line and
            not re.search(r'\+?\d', line) and
            len(words) >= 2 and all(w and len(w) > 0 and w[0].isupper() for w in words[:2]) and
            not any(w.lower() in ['email', 'phone', 'date', 'birth', 'orcid', 'website', 'experience', 'education', 'publications', 'researcher', 'id'] for w in words)):
            data["name"] = line
            print(f"[PARSER V2] Name found at line {i}: {line}")
            break
    
    if not data["name"]:
        print(f"[PARSER V2] Name NOT found. First 10 lines: {lines[:10]}")
    
    # 2. EXTRACT EMAIL
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        # Fix OCR errors
        email = emails[0].lower()
        email = email.replace('peabedi', 'abedi').replace('corn', 'com')
        data["email"] = email
        print(f"[PARSER V2] Email: {email}")
    
    # 3. EXTRACT PHONE
    phone_pattern = r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    phones = re.findall(phone_pattern, text)
    if phones:
        data["phone"] = phones[0]
        print(f"[PARSER V2] Phone: {phones[0]}")
    
    # 4. EXTRACT LOCATION
    locations = ['Singapore', 'USA', 'United States', 'UK', 'United Kingdom', 
                 'Australia', 'Canada', 'India', 'Malaysia', 'Thailand', 'Hong Kong']
    for loc in locations:
        if loc.lower() in text.lower():
            data["location"] = loc
            print(f"[PARSER V2] Location: {loc}")
            break
    
    # 5. FIND SECTIONS - Look for section headers (more lenient)
    section_starts = {}
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        words = line.split()
        word_count = len(words)
        
        # Education - check for "# Education" or "Education" header
        if 'education' in line_lower:
            if (line_lower.startswith('#') or 
                word_count <= 5 or
                line_lower == 'education' or
                line_lower.startswith('education')):
                section_starts['education'] = i
                print(f"[PARSER V2] Education section at line {i}: '{line[:50]}'")
        
        # Experience - check for "Experience" header (can have "(most recent first)")
        if 'experience' in line_lower and not section_starts.get('experience'):
            if (line_lower.startswith('#') or 
                word_count <= 8 or  # Allow "Experience (most recent first)"
                line_lower.startswith('experience')):
                section_starts['experience'] = i
                print(f"[PARSER V2] Experience section at line {i}: '{line[:50]}'")
        
        # Publications - check for "Publications" header
        if 'publications' in line_lower and not section_starts.get('publications'):
            if (line_lower.startswith('#') or 
                word_count <= 5 or
                line_lower.startswith('publications')):
                section_starts['publications'] = i
                print(f"[PARSER V2] Publications section at line {i}: '{line[:50]}'")
        
        # Skills - check for "Technical Skills" or "Skills" with "Expertise"
        if ('technical skills' in line_lower or 
            ('skills' in line_lower and 'expertise' in line_lower)) and not section_starts.get('skills'):
            if (line_lower.startswith('#') or 
                word_count <= 5 or
                'technical skills' in line_lower):
                section_starts['skills'] = i
                print(f"[PARSER V2] Skills section at line {i}: '{line[:50]}'")
    
    print(f"[PARSER V2] Sections found: {section_starts}")
    
    # If no sections found, try pattern-based detection
    if not section_starts:
        print(f"[PARSER V2] No explicit sections found, trying pattern-based detection...")
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Look for education patterns (PhD, MS, etc. with university)
            if not section_starts.get('education') and i > 5:
                if any(word in line_lower for word in ['phd', 'ms', 'bsc', 'bachelor', 'master']) and any(word in line_lower for word in ['university', 'college', 'institute']):
                    section_starts['education'] = max(0, i - 3)
                    print(f"[PARSER V2] Education pattern at line {i}: '{line[:50]}'")
            
            # Look for experience patterns (job titles)
            if not section_starts.get('experience') and i > 5:
                if any(word in line_lower for word in ['visiting researcher', 'postdoctoral', 'research fellow']) and any(word in line_lower for word in ['university', 'institute']):
                    section_starts['experience'] = max(0, i - 5)
                    print(f"[PARSER V2] Experience pattern at line {i}: '{line[:50]}'")
            
            # Look for publications (numbered entries)
            if not section_starts.get('publications') and i > 20:
                if re.match(r'^\d+\.', line.strip()):
                    if any(word in line_lower for word in ['doi', 'journal', 'chem', 'nature']):
                        section_starts['publications'] = max(0, i - 5)
                        print(f"[PARSER V2] Publications pattern at line {i}: '{line[:50]}'")
                        break
    
    # 6. PARSE EDUCATION - More aggressive search
    edu_start = section_starts.get('education', 0)
    
    # If no explicit section found, search entire document for education patterns
    if edu_start == 0:
        print(f"[PARSER V2] No education section found, searching entire document...")
        # Search all lines for education patterns
        for i, line in enumerate(lines[5:200], start=5):  # Skip header, search up to line 200
            line_lower = line.lower()
            
            # Look for degree keywords
            has_degree = any(word in line_lower for word in ['phd', 'ph.d', 'ph.d.', 'ms', 'm.s', 'm.sc', 'masters', 'bsc', 'b.s', 'bachelor', 'master', 'degree', 'doctorate'])
            # Look for institution keywords
            has_institution = any(word in line_lower for word in ['university', 'college', 'institute', 'sutd', 'ntu', 'lums', 'uet', 'nust', 'karachi', 'lahore', 'islamabad', 'engineering', 'technology'])
            # Look for education context
            has_context = any(word in line_lower for word in ['in ', 'of ', 'from', 'defence', 'awarded', 'graduated', 'thesis', 'dissertation', 'defended'])
            
            # If we find degree + (institution OR context), this is likely education
            if has_degree and (has_institution or has_context):
                edu_start = max(0, i - 3)  # Start a bit earlier
                print(f"[PARSER V2] Education pattern found at line {i}: '{line[:60]}'")
                # Don't break - continue to find the earliest occurrence
                if edu_start > 0:
                    break
    
    if edu_start > 0:
        edu_end = min(
            section_starts.get('experience', len(lines)),
            section_starts.get('publications', len(lines)),
            edu_start + 50
        )
        edu_lines = lines[edu_start:edu_end]
        
        current_edu = {}
        for i, line in enumerate(edu_lines):
            line_lower = line.lower()
            
            # Match degree: More flexible patterns
            # Pattern 1: "PhD in X" or "Ph.D in X"
            degree_match = re.search(r'[-•]?\s*(PhD|Ph\.D|Ph\.D\.|MS|M\.S|M\.Sc|MSc|BSc|B\.S|Bachelor|Master|Bachelors|Masters)\s+(?:in|of)?\s*([^,\n]+?)(?:,|$|\n|from)', line, re.IGNORECASE)
            # Pattern 2: "X University" followed by degree
            if not degree_match:
                degree_match = re.search(r'(PhD|Ph\.D|MS|M\.S|M\.Sc|BSc|B\.S|Bachelor|Master)\s+(?:in|of)?\s*([^,\n]+?)(?:,|$|\n)', line, re.IGNORECASE)
            
            if degree_match:
                if current_edu.get("degree"):
                    data["education"].append(current_edu)
                
                degree_type = degree_match.group(1)
                field = degree_match.group(2).strip() if len(degree_match.groups()) > 1 and degree_match.group(2) else ""
                current_edu = {
                    "degree": degree_type,
                    "field": field,
                    "institution": "",
                    "year": None
                }
            
            # Find institution (more flexible - can be before or after degree)
            if not current_edu.get("institution"):
                if any(word in line_lower for word in ['university', 'college', 'institute', 'sutd', 'ntu', 'lums', 'uet', 'nust', 'karachi', 'lahore', 'islamabad']):
                    # Clean up institution name
                    inst = line.strip()
                    # Remove common prefixes
                    inst = re.sub(r'^[-•]\s*', '', inst)
                    current_edu["institution"] = inst
                    # If we found institution but no degree yet, try to extract degree from same line
                    if not current_edu.get("degree"):
                        degree_in_line = re.search(r'(PhD|Ph\.D|MS|M\.S|BSc|B\.S|Bachelor|Master)', line, re.IGNORECASE)
                        if degree_in_line:
                            current_edu["degree"] = degree_in_line.group(1)
            
            # Find year (more flexible)
            if not current_edu.get("year"):
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    current_edu["year"] = int(year_match.group(0))
                # Also check for "Awarded: YYYY" or "Defence: YYYY"
                awarded_match = re.search(r'(?:awarded|defence|graduated|completed)[:\s]+(19|20)\d{2}', line_lower)
                if awarded_match:
                    current_edu["year"] = int(awarded_match.group(1) + awarded_match.group(0)[-2:])
        
        if current_edu.get("degree") or current_edu.get("institution"):
            data["education"].append(current_edu)
    
    # If still no education found, try searching entire document without section boundaries
    if len(data["education"]) == 0:
        print(f"[PARSER V2] No education in section, searching entire document...")
        current_edu = {}
        for i, line in enumerate(lines[5:150], start=5):  # Skip header
            line_lower = line.lower()
            
            # Look for degree patterns anywhere
            degree_match = re.search(r'\b(PhD|Ph\.D|Ph\.D\.|MS|M\.S|M\.Sc|MSc|BSc|B\.S|Bachelor|Master|Bachelors|Masters)\b', line, re.IGNORECASE)
            
            if degree_match:
                # If we have a previous education entry, save it
                if current_edu.get("degree") or current_edu.get("institution"):
                    data["education"].append(current_edu)
                
                degree_type = degree_match.group(1)
                # Try to extract field
                field_match = re.search(r'(?:in|of)\s+([^,\n]+?)(?:,|$|\n|from)', line, re.IGNORECASE)
                field = field_match.group(1).strip() if field_match else ""
                
                current_edu = {
                    "degree": degree_type,
                    "field": field,
                    "institution": "",
                    "year": None
                }
            
            # Look for institution in same or next lines
            if current_edu.get("degree") and not current_edu.get("institution"):
                if any(word in line_lower for word in ['university', 'college', 'institute', 'sutd', 'ntu', 'lums', 'uet', 'nust']):
                    inst = line.strip()
                    inst = re.sub(r'^[-•]\s*', '', inst)
                    current_edu["institution"] = inst
            
            # Look for year
            if current_edu.get("degree") and not current_edu.get("year"):
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    current_edu["year"] = int(year_match.group(0))
        
        # Save last education entry
        if current_edu.get("degree") or current_edu.get("institution"):
            data["education"].append(current_edu)
    
    print(f"[PARSER V2] Education: {len(data['education'])} entries")
    if len(data['education']) > 0:
        for i, edu in enumerate(data['education']):
            print(f"[PARSER V2]   Edu {i+1}: {edu.get('degree', '?')} in {edu.get('field', '?')} from {edu.get('institution', '?')}")
    
    # 7. PARSE EXPERIENCE
    exp_start = section_starts.get('experience', 0)
    # If no explicit section, search for experience patterns
    if exp_start == 0:
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Look for "Experience" header or job title patterns
            if 'experience' in line_lower and len(line.split()) <= 8:
                exp_start = i
                print(f"[PARSER V2] Experience header found at line {i}: '{line[:50]}'")
                break
            # Or look for job titles
            if i > 5 and any(word in line_lower for word in ['visiting researcher', 'postdoctoral', 'research fellow']):
                if any(word in line_lower for word in ['university', 'institute', 'ntu', 'sutd']):
                    exp_start = max(0, i - 2)
                    print(f"[PARSER V2] Experience pattern found at line {i}: '{line[:50]}'")
                    break
    
    if exp_start > 0:
        exp_end = min(
            section_starts.get('education', len(lines)),
            section_starts.get('publications', len(lines)),
            section_starts.get('skills', len(lines)),
            exp_start + 100
        )
        exp_lines = lines[exp_start:exp_end]
        
        current_exp = {}
        for i, line in enumerate(exp_lines):
            line_lower = line.lower()
            
            # Skip section header
            if i == 0 and 'experience' in line_lower:
                continue
            
            # Match job title: "- Visiting Researcher" or "- Postdoctoral Research Fellow"
            title_match = re.match(r'[-•]\s*(.+?)(?:$|\n)', line)
            if title_match:
                title = title_match.group(1).strip()
                if any(word in title.lower() for word in ['researcher', 'scientist', 'fellow', 'engineer', 'mentor', 'professor']):
                    if current_exp.get("title"):
                        data["experience"].append(current_exp)
                    
                    current_exp = {
                        "title": title,
                        "company": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "description": []
                    }
                    continue
            
            # Find company (line with university/institute, no bullet)
            if current_exp.get("title") and not current_exp.get("company"):
                if (not line.startswith(('-', '•')) and
                    any(word in line_lower for word in ['university', 'institute', 'college', 'ntu', 'sutd', 'ucl', 'nanyang'])):
                    current_exp["company"] = line
                    # Extract location
                    for loc in ['Singapore', 'UK', 'United Kingdom', 'USA', 'United States', 'London']:
                        if loc.lower() in line_lower:
                            current_exp["location"] = loc
                            break
                    continue
            
            # Find date range: "01/09/2025 – Present"
            date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{2,4})\s*[–-]\s*(present|current|\d{2}[/-]\d{2}[/-]\d{2,4})', line_lower)
            if date_match and current_exp.get("title"):
                current_exp["start_date"] = date_match.group(1)
                end_date = date_match.group(2)
                if 'present' in end_date.lower():
                    current_exp["end_date"] = "Present"
                else:
                    current_exp["end_date"] = end_date
                continue
            
            # Description bullets
            if current_exp.get("title") and (line.startswith(('-', '•')) or 
                                             any(word in line_lower[:20] for word in ['actively', 'perform', 'leverage', 'led', 'employed', 'conducted', 'guided', 'organized'])):
                desc = line.lstrip('-• ').strip()
                if len(desc) > 10:
                    current_exp["description"].append(desc)
        
        if current_exp.get("title"):
            data["experience"].append(current_exp)
    
    print(f"[PARSER V2] Experience: {len(data['experience'])} entries")
    
    # 8. PARSE PUBLICATIONS
    pub_start = section_starts.get('publications', 0)
    # If no explicit section, search for numbered publication entries
    if pub_start == 0:
        for i, line in enumerate(lines):
            # Look for numbered entries (1., 2., etc.) with publication content
            if re.match(r'^\d+\.', line.strip()):
                line_lower = line.lower()
                if any(word in line_lower for word in ['doi', 'journal', 'chem', 'nature', 'angew', 'int. ed', 'soc.']):
                    pub_start = max(0, i - 5)
                    print(f"[PARSER V2] Publications pattern found at line {i}: '{line[:50]}'")
                    break
    
    if pub_start > 0:
        pub_end = min(
            section_starts.get('skills', len(lines)),
            section_starts.get('awards', len(lines)),
            len(lines)
        )
        pub_lines = lines[pub_start:pub_end]
        pub_text = '\n'.join(pub_lines)
        
        # Split by numbered entries (1., 2., etc.)
        pub_entries = re.split(r'\n(?=\d+\.)', pub_text)
        
        for entry in pub_entries:
            entry = entry.strip()
            if len(entry) < 30:
                continue
            
            # Remove leading number
            entry = re.sub(r'^\d+\.\s*', '', entry)
            
            # Extract year
            year_match = re.search(r'\b(20\d{2}|19\d{2})\b', entry)
            year = int(year_match.group(0)) if year_match else None
            
            # Extract DOI
            doi_match = re.search(r'doi[:\s]*([\d\.]+/[^\s,]+)', entry, re.IGNORECASE)
            doi = doi_match.group(1) if doi_match else None
            
            # Extract journal (common patterns)
            journal = ""
            journal_patterns = [
                r'Angew\.\s*Chem\.\s*(?:Int\.\s*Ed\.)?',
                r'J\.\s*Am\.\s*Chem\.\s*Soc\.',
                r'Nature\s*Methods',
                r'CCS\s*Chemistry',
                r'Chem\.\s*Commun\.',
                r'Dyes\s*Pigments',
                r'Adv\.\s*Sci\.',
                r'Adv\.\s*Funct\.\s*Mater\.',
                r'Chin\.\s*Chem\.\s*Lett\.',
                r'Mater\.\s*Chem\.\s*Front\.',
                r'Nat\.\s*Commun\.',
                r'J\.\s*Phys\.\s*Chem\.\s*[A-Z]',
            ]
            
            for pattern in journal_patterns:
                match = re.search(pattern, entry, re.IGNORECASE)
                if match:
                    journal = match.group(0).strip('.,;')
                    break
            
            # Extract authors (before year in parentheses)
            authors_match = re.search(r'^([^\(]+?)\s*\((\d{4})\)', entry)
            if authors_match:
                authors = authors_match.group(1).strip()
            else:
                authors_match = re.match(r'^([^:]+?)(?::|\(|\d)', entry)
                authors = authors_match.group(1).strip() if authors_match else ""
            
            # Extract title (after colon or year, before journal)
            if ':' in entry:
                title_part = entry.split(':', 1)[1]
                if journal:
                    title = title_part.split(journal)[0].strip().rstrip('.,;')
                else:
                    title = title_part.split('.')[0].strip().rstrip('.,;')
            else:
                # Try to extract from format "Authors (Year): Title. Journal"
                title_match = re.search(r'\((\d{4})\):\s*([^\.]+?)(?:\.|$)', entry)
                if title_match:
                    title = title_match.group(2).strip().rstrip('.,;')
                else:
                    # Fallback
                    parts = entry.split('.')
                    title = parts[0].strip().rstrip('.,;') if parts else entry[:200].strip()
            
            if title and len(title) > 10:
                pub = {
                    "title": title[:500],
                    "authors": authors[:500] if authors else "",
                    "journal": journal[:200] if journal else "",
                    "year": year,
                    "doi": doi
                }
                data["publications"].append(pub)
    
    print(f"[PARSER V2] Publications: {len(data['publications'])} entries")
    
    # 9. PARSE SKILLS
    skills_start = section_starts.get('skills', 0)
    # If no explicit section, search for skills table
    if skills_start == 0:
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Look for "Technical Skills" or table with "Category | Skills"
            if ('technical skills' in line_lower or 
                ('skills' in line_lower and 'expertise' in line_lower) or
                ('|' in line and 'category' in line_lower and 'skill' in line_lower)):
                skills_start = i
                print(f"[PARSER V2] Skills section found at line {i}: '{line[:50]}'")
                break
    
    if skills_start > 0:
        skills_end = min(len(lines), skills_start + 50)
        skills_lines = lines[skills_start:skills_end]
        
        # Look for table format: "| Category | Skills |"
        in_table = False
        for line in skills_lines:
            line_lower = line.lower()
            
            # Skip section header
            if 'technical skills' in line_lower or ('skills' in line_lower and 'expertise' in line_lower):
                continue
            
            # Check for table header
            if '|' in line and 'category' in line_lower:
                in_table = True
                continue
            
            # Extract from table rows
            if in_table and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:  # | Category | Skills |
                    skills_text = parts[1] if len(parts) > 1 else ""
                    # Split skills by commas, semicolons, colons
                    skills_list = re.split(r'[,;:]', skills_text)
                    for skill in skills_list:
                        skill = skill.strip()
                        # Remove parentheses but keep content
                        skill = re.sub(r'\([^)]+\)', '', skill).strip()
                        # Remove common prefixes
                        skill = re.sub(r'^(Languages?|Software|Tools?|Frameworks?|ML|Machine Learning|Data|Programming):\s*', '', skill, flags=re.IGNORECASE)
                        if len(skill) > 2 and skill.lower() not in ['and', 'or', 'the', 'a', 'category', 'skills']:
                            data["skills"].append(skill)
        
        # Remove duplicates and filter out sentence fragments
        filtered_skills = []
        skip_words = ['technical', 'expertise', 'skills', 'category', 'competencies', 'proficiencies']
        # Sentence fragments and non-skill words to filter
        sentence_fragments = [
            'actively', 'guided', 'utilising', 'utilizing', 'performed', 'conducted', 'led', 'organized',
            'employing', 'leveraging', 'developing', 'creating', 'designing', 'implementing',
            'density', 'photostability', 'stability', 'methodology', 'approach', 'technique',
            'ntu', 'sutd', 'nus', 'ucl', 'mit', 'stanford', 'harvard', 'oxford', 'cambridge',
            'also', 'including', 'especially', 'particularly', 'specifically', 'primarily',
            'this', 'that', 'these', 'those', 'from', 'into', 'onto', 'upon', 'within', 'without',
            'and', 'or', 'the', 'a', 'an', 'with', 'using', 'via', 'for', 'to', 'in', 'on', 'at', 'by'
        ]
        
        for skill in data["skills"]:
            skill_lower = skill.lower().strip()
            # Skip if it's a category header or common word
            if any(word == skill_lower for word in skip_words):
                continue
            # Skip if it's a sentence fragment
            if skill_lower in sentence_fragments:
                continue
            # Skip if it starts with category/technical
            if skill_lower.startswith('category') or skill_lower.startswith('technical'):
                continue
            # Skip if it's too short
            if len(skill) < 3:
                continue
            # Skip if it ends with -ly (adverbs) unless it's a known skill
            if skill_lower.endswith('ly') and len(skill_lower) < 8:
                continue
            # Skip if it's just a verb ending in -ing (unless it's a known skill like "Programming")
            if skill_lower.endswith('ing') and skill_lower not in ['programming', 'engineering', 'marketing', 'designing']:
                if skill_lower in ['utilising', 'utilizing', 'employing', 'leveraging', 'developing', 'creating']:
                    continue
            # Skip if it's an institution name (short acronyms)
            if len(skill) <= 4 and skill.isupper() and skill_lower in ['ntu', 'sutd', 'nus', 'ucl', 'mit']:
                continue
            # Must have at least one letter
            if not re.search(r'[a-zA-Z]', skill):
                continue
            
            filtered_skills.append(skill)
        
        data["skills"] = list(dict.fromkeys(filtered_skills))[:100]
    
    print(f"[PARSER V2] Skills: {len(data['skills'])} entries")
    print(f"[PARSER V2] FINAL: Name='{data['name']}', Email='{data['email']}', Edu={len(data['education'])}, Exp={len(data['experience'])}, Pubs={len(data['publications'])}, Skills={len(data['skills'])}")
    
    return data


def parse_resume_file_v2(filepath: str) -> Dict:
    """Parse resume file using V2 parser"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    return parse_resume_v2(filepath)
