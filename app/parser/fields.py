import re
import spacy
from typing import Dict, Any, List, Optional

# Load spaCy model for name extraction
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # Fallback if model not loaded properly
    nlp = None

# A baseline of common industry skills for fallback keyword matching
COMMON_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "php", "swift", "kotlin", "go", "rust",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot", "laravel",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis", "cassandra", "neo4j", "oracle",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "ci/cd", "terraform", "ansible",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "scipy", "spark", "hadoop", "tableau", "power bi",
    "agile", "scrum", "project management", "product management", "jira", "confluence",
    "rest api", "graphql", "grpc", "microservices", "system design", "linux", "unix", "bash"
]

def parse_fields(text: str) -> Dict[str, Any]:
    """
    Parses a resume's text to extract contact info, urls, skills, education,
    experience, certifications, languages, and summary.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Track which fields were found through clear section headers for scoring
    extracted_metadata = {
        "has_name_entity": False,
        "has_skills_header": False,
        "has_education_header": False,
        "has_experience_header": False,
        "has_certifications_header": False,
        "has_languages_header": False,
        "has_summary_header": False
    }

    # Extract Deterministic Fields using Regex
    email = extract_email(text)
    phone = extract_phone(text)
    linkedin = extract_linkedin(text)
    github = extract_github(text)
    location = extract_location(text)
    
    # Extract spaCy Named Entities for Name
    full_name, name_found = extract_name(lines)
    extracted_metadata["has_name_entity"] = name_found

    # Segment the resume by sections for heuristics
    sections = segment_sections(text, extracted_metadata)

    # Extract section-based fields
    skills = extract_skills(sections.get("skills", ""), text, extracted_metadata)
    summary = extract_summary(sections.get("summary", ""), lines, extracted_metadata)
    education = extract_education(sections.get("education", ""), extracted_metadata)
    experience = extract_experience(sections.get("experience", ""), extracted_metadata)
    certifications = extract_certifications(sections.get("certifications", ""), extracted_metadata)
    languages = extract_languages(sections.get("languages", ""), extracted_metadata)

    return {
        "parsed_data": {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin_url": linkedin,
            "github_url": github,
            "skills": skills,
            "education": education,
            "work_experience": experience,
            "certifications": certifications,
            "languages": languages,
            "summary": summary if summary else None
        },
        "metadata": extracted_metadata
    }

def extract_email(text: str) -> Optional[str]:
    pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    # Matches common phone patterns: +1-555-555-5555, (555) 555-5555, 555.555.5555, etc.
    pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None

def extract_linkedin(text: str) -> Optional[str]:
    pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0).strip() if match else None

def extract_github(text: str) -> Optional[str]:
    pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?'
    match = re.search(pattern, text, re.IGNORECASE)
    # Exclude common github pages that aren't profile pages if necessary
    if match:
        url = match.group(0).strip()
        if "github.com/features" in url or "github.com/pricing" in url:
            return None
        return url
    return None

def extract_location(text: str) -> Optional[str]:
    # Matches "City, ST" or "City, Country" patterns in first few lines
    lines = [line.strip() for line in text.split('\n') if line.strip()][:15]
    skill_keywords = ["python", "javascript", "java", "c++", "c#", "html", "css"]
    
    # First, look for a part of any line that explicitly has "location" prefix
    for line in lines:
        if "location" in line.lower():
            parts = re.split(r'location\s*:\s*', line, flags=re.IGNORECASE)
            if len(parts) > 1:
                loc_candidate = parts[1].split('|')[0].strip()
                if loc_candidate:
                    return loc_candidate

    pattern = r'\b([A-Z][a-zA-Z\s.]+),\s([A-Z]{2}|[A-Z][a-zA-Z\s]+)\b'
    for line in lines:
        # Split line by common separators to analyze segments independently
        segments = re.split(r'[|•\t]', line)
        for segment in segments:
            segment = segment.strip()
            match = re.search(pattern, segment)
            if match:
                matched_str = match.group(0)
                if "@" not in segment and "http" not in segment:
                    if not any(skill in matched_str.lower() for skill in skill_keywords):
                        return matched_str
    return None

def extract_name(lines: List[str]) -> tuple[Optional[str], bool]:
    """Extracts candidate name using spaCy PERSON entity recognition with fallbacks."""
    if not lines:
        return None, False

    # Check top 5 lines for PERSON entities
    if nlp:
        for line in lines[:5]:
            doc = nlp(line)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    # Perform simple validation: name shouldn't contain email/digits/excessive words
                    name = ent.text.strip()
                    if len(name.split()) <= 4 and not any(char.isdigit() for char in name) and "@" not in name:
                        return name, True

    # Fallback heuristic: First non-empty line that doesn't contain contact info/links
    for line in lines[:3]:
        clean_line = line.strip()
        if "@" not in clean_line and "http" not in clean_line and not any(kw in clean_line.lower() for kw in ["resume", "curriculum", "cv"]):
            words = clean_line.split()
            if 1 < len(words) <= 4 and not any(char.isdigit() for char in clean_line):
                return clean_line, False
                
    return None, False

def segment_sections(text: str, meta: Dict[str, bool]) -> Dict[str, str]:
    """Segments resume text into raw content blocks based on header matches."""
    headers = {
        "summary": [r'\bobjective\b', r'\bprofile\b', r'\bsummary\b', r'\babout\s+me\b'],
        "skills": [r'\bskills\b', r'\btechnical\s+skills\b', r'\bcore\s+competencies\b', r'\bexpertise\b'],
        "education": [r'\beducation\b', r'\bacademics\b', r'\bacademics\s+qualification\b', r'\bacademics\s+credentials\b'],
        "experience": [r'\bexperience\b', r'\bprofessional\s+experience\b', r'\bwork\s+experience\b', r'\bemployment\s+history\b', r'\bwork\s+history\b'],
        "certifications": [r'\bcertifications\b', r'\bcertificates\b', r'\bcredentials\b', r'\blicenses\b'],
        "languages": [r'\blanguages\b', r'\blanguage\b']
    }

    # Find the positions of all section headers in the text
    positions = []
    for section_name, patterns in headers.items():
        for pattern in patterns:
            # Search case-insensitively with word boundaries
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Ensure the header is on its own line or close to it
                start = match.start()
                positions.append((start, section_name))
                # Set metadata that header was found
                meta[f"has_{section_name}_header"] = True

    # Sort positions by their occurrence in the text
    positions.sort()
    
    sections = {}
    if not positions:
        return sections

    # Slice text based on section boundaries
    for i in range(len(positions)):
        start_idx, sec_name = positions[i]
        end_idx = positions[i+1][0] if i + 1 < len(positions) else len(text)
        
        # Keep the content excluding the header name itself
        content = text[start_idx:end_idx].strip()
        # Remove first line (which contains the header name)
        content_lines = content.split('\n')[1:]
        sections[sec_name] = "\n".join(content_lines).strip()
        
    return sections

def extract_skills(section_text: str, full_text: str, meta: Dict[str, bool]) -> List[str]:
    """Extracts skills from the specific section, or scans the full text as fallback."""
    skills_set = set()
    
    # 1. If we have a skills section, parse it line-by-line and comma-by-comma
    if section_text:
        # Split by typical separators: commas, bullet points, pipes, tabs, newlines
        parts = re.split(r'[,|•\t\n]|\s{2,}', section_text)
        for part in parts:
            clean_part = part.strip().strip(':-·*')
            if clean_part and len(clean_part) < 40:
                # Basic cleanup
                skills_set.add(clean_part)
                
    # 2. As a fallback/supplement, scan full text for predefined industry keywords
    normalized_text = full_text.lower()
    for skill in COMMON_SKILLS:
        # Use word boundaries to avoid false positives (e.g., "Go" inside "Google")
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, normalized_text):
            # Match casing of original COMMON_SKILLS
            skills_set.add(skill.title() if len(skill) > 3 and skill != "ci/cd" else skill)
            
    return sorted(list(skills_set))

def extract_summary(section_text: str, lines: List[str], meta: Dict[str, bool]) -> Optional[str]:
    """Extracts summary/objective description."""
    if section_text:
        return section_text
    return None

def extract_education(section_text: str, meta: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Parses education blocks into objects (institution, degree, field, dates)."""
    education_list = []
    if not section_text:
        return education_list

    lines = [e.strip() for e in section_text.split('\n') if e.strip()]
    
    # Let's find all lines that look like an institution
    inst_pattern = r'\b([A-Z][a-zA-Z\s,]+ (?:University|College|Institute|School|Academy|Polytechnic))\b'
    
    for idx, line in enumerate(lines):
        inst_match = re.search(inst_pattern, line)
        if inst_match:
            edu_obj = {
                "institution": inst_match.group(1).strip(),
                "degree": None,
                "field": None,
                "dates": None
            }
            
            # Look in the current line, previous line, and next line for context
            context_lines = []
            if idx > 0:
                context_lines.append(lines[idx-1])
            context_lines.append(line)
            if idx < len(lines) - 1:
                context_lines.append(lines[idx+1])
                
            combined_context = " | ".join(context_lines)
            
            # 2. Search for degree
            degree_pattern = r'\b(B\.?S\.?c?|B\.?A\.?|M\.?S\.?c?|M\.?A\.?|Ph\.?D\.?|Bachelor|Master|Doctorate|B\.?Tech|M\.?Tech|Diploma)\b'
            deg_match = re.search(degree_pattern, combined_context, re.IGNORECASE)
            if deg_match:
                edu_obj["degree"] = deg_match.group(0).strip()
                
            # 3. Search for dates
            date_pattern = r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4}|\d{4})\s*[-–to]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4}|\d{4}|Present|Current)\b'
            date_match = re.search(date_pattern, combined_context, re.IGNORECASE)
            if date_match:
                edu_obj["dates"] = date_match.group(0).strip()
                
            # 4. Search for field of study
            field_pattern = r'(?:in|Major in)\s+([A-Z][a-zA-Z\s]{3,30})'
            field_match = re.search(field_pattern, combined_context)
            if field_match:
                edu_obj["field"] = field_match.group(1).strip()
                
            education_list.append(edu_obj)
            
    # Fallback if no institutions were matched but we found a degree
    if not education_list:
        for line in lines:
            degree_pattern = r'\b(B\.?S\.?c?|B\.?A\.?|M\.?S\.?c?|M\.?A\.?|Ph\.?D\.?|Bachelor|Master|Doctorate|B\.?Tech|M\.?Tech|Diploma)\b'
            deg_match = re.search(degree_pattern, line, re.IGNORECASE)
            if deg_match:
                edu_obj = {
                    "institution": None,
                    "degree": deg_match.group(0).strip(),
                    "field": None,
                    "dates": None
                }
                date_pattern = r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4}|\d{4})\s*[-–to]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4}|\d{4}|Present|Current)\b'
                date_match = re.search(date_pattern, line, re.IGNORECASE)
                if date_match:
                    edu_obj["dates"] = date_match.group(0).strip()
                education_list.append(edu_obj)
                
    return education_list

def extract_experience(section_text: str, meta: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Parses work experience blocks into company, title, dates, and description."""
    experience_list = []
    if not section_text:
        return experience_list

    # Separate entries by double newlines or lines starting with companies/dates
    lines = section_text.split('\n')
    current_exp = None
    
    # Common job title keywords for matching
    title_keywords = r'\b(Developer|Engineer|Manager|Analyst|Consultant|Designer|Lead|Architect|Specialist|Director|Intern|Associate|Administrator)\b'
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        # Detect dates pattern which typically signals a new job entry
        date_pattern = r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4}|\d{4})\s*[-–to]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4}|\d{4}|Present|Current)\b'
        date_match = re.search(date_pattern, line_strip, re.IGNORECASE)
        
        # Check if line contains a company or job title + date (indicates a new entry)
        is_new_entry = False
        if date_match and (re.search(title_keywords, line_strip, re.IGNORECASE) or len(line_strip.split()) < 10):
            is_new_entry = True
            
        if is_new_entry or current_exp is None:
            if current_exp:
                experience_list.append(current_exp)
                
            current_exp = {
                "company": None,
                "title": None,
                "dates": None,
                "description": ""
            }
            
            if date_match:
                current_exp["dates"] = date_match.group(0).strip()
                # Clean up date from entry header candidate
                clean_header = line_strip.replace(current_exp["dates"], "").strip(" ,-|–")
            else:
                clean_header = line_strip
                
            # Attempt to split company & title
            parts = re.split(r'\s{2,}|[|•–\t\-]', clean_header)
            parts = [p.strip() for p in parts if p.strip()]
            
            if len(parts) >= 2:
                current_exp["title"] = parts[0]
                current_exp["company"] = parts[1]
            elif len(parts) == 1:
                # If only one part, try matching title keyword
                if re.search(title_keywords, parts[0], re.IGNORECASE):
                    current_exp["title"] = parts[0]
                else:
                    current_exp["company"] = parts[0]
        else:
            # Bullet point or description line
            if current_exp:
                if current_exp["description"]:
                    current_exp["description"] += "\n" + line_strip
                else:
                    current_exp["description"] = line_strip
                    
    if current_exp:
        experience_list.append(current_exp)
        
    return experience_list

def extract_certifications(section_text: str, meta: Dict[str, bool]) -> List[str]:
    """Extracts certification names from certifications block."""
    certs = []
    if not section_text:
        return certs
        
    lines = section_text.split('\n')
    for line in lines:
        line_strip = line.strip().strip(':-·*•')
        if line_strip and len(line_strip) < 100:
            certs.append(line_strip)
    return certs

def extract_languages(section_text: str, meta: Dict[str, bool]) -> List[str]:
    """Extracts language names from languages block."""
    languages = []
    if not section_text:
        return languages
        
    # Split by commas, slashes, or newlines
    parts = re.split(r'[,/|\n]', section_text)
    for part in parts:
        clean_part = re.sub(r'\([^)]*\)', '', part).strip().strip(':-·*•')  # remove (Fluent), (Native) etc.
        if clean_part and len(clean_part) < 30:
            languages.append(clean_part)
    return languages
