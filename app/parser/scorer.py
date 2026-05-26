from typing import Dict, Any

def calculate_completeness(parsed_data: Dict[str, Any]) -> float:
    """
    Calculates completeness_score (0-100) as the percentage of key fields populated.
    Key fields: full_name, email, phone, location, skills, education, work_experience.
    """
    key_fields = [
        "full_name",
        "email",
        "phone",
        "location",
        "skills",
        "education",
        "work_experience"
    ]
    
    populated_count = 0
    for field in key_fields:
        val = parsed_data.get(field)
        if isinstance(val, list):
            if len(val) > 0:
                populated_count += 1
        elif val is not None and str(val).strip() != "":
            populated_count += 1
            
    return round((populated_count / len(key_fields)) * 100, 1)

def calculate_confidence(parsed_data: Dict[str, Any], metadata: Dict[str, bool]) -> float:
    """
    Calculates confidence_score (0-100) based on extraction reliability.
    - Email and phone via regex: high confidence (100).
    - URLs via regex: high confidence (100).
    - Name: spaCy (85), Heuristic fallback (50).
    - Section fields (skills, education, experience): Header found (95), Inferred (40).
    """
    scores = []
    
    # 1. Email (Regex)
    if parsed_data.get("email"):
        scores.append(100)
        
    # 2. Phone (Regex)
    if parsed_data.get("phone"):
        scores.append(100)
        
    # 3. URLs (Regex)
    if parsed_data.get("linkedin_url"):
        scores.append(100)
    if parsed_data.get("github_url"):
        scores.append(100)
        
    # 4. Location (Regex/Heuristic)
    if parsed_data.get("location"):
        scores.append(80)
        
    # 5. Name (spaCy vs Fallback)
    if parsed_data.get("full_name"):
        if metadata.get("has_name_entity", False):
            scores.append(85)
        else:
            scores.append(50)
            
    # 6. Skills (Header vs Scanned)
    if parsed_data.get("skills"):
        if metadata.get("has_skills_header", False):
            scores.append(95)
        else:
            scores.append(50)
            
    # 7. Education
    if parsed_data.get("education"):
        if metadata.get("has_education_header", False):
            scores.append(95)
        else:
            scores.append(45)
            
    # 8. Experience
    if parsed_data.get("work_experience"):
        if metadata.get("has_experience_header", False):
            scores.append(95)
        else:
            scores.append(45)
            
    # 9. Certifications
    if parsed_data.get("certifications"):
        if metadata.get("has_certifications_header", False):
            scores.append(90)
        else:
            scores.append(40)
            
    # 10. Languages
    if parsed_data.get("languages"):
        if metadata.get("has_languages_header", False):
            scores.append(90)
        else:
            scores.append(40)
            
    if not scores:
        return 0.0
        
    return round(sum(scores) / len(scores), 1)

def score_resume(parsed_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes both completeness and confidence scores and updates the parsed result.
    """
    data = parsed_result["parsed_data"]
    meta = parsed_result["metadata"]
    
    completeness = calculate_completeness(data)
    confidence = calculate_confidence(data, meta)
    
    parsed_result["completeness_score"] = completeness
    parsed_result["confidence_score"] = confidence
    
    return parsed_result
