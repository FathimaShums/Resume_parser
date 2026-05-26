import pytest
from app.parser.scorer import score_resume, calculate_completeness, calculate_confidence

def test_scorer_fully_populated():
    parsed_result = {
        "parsed_data": {
            "full_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA",
            "linkedin_url": "linkedin.com/in/janedoe",
            "github_url": "github.com/janedoe",
            "skills": ["Python", "Docker"],
            "education": [{"institution": "Stanford University", "degree": "BS"}],
            "work_experience": [{"company": "Tech Corp", "title": "Developer"}],
            "certifications": ["AWS Solutions Architect"],
            "languages": ["English"],
            "summary": "Full stack engineer"
        },
        "metadata": {
            "has_name_entity": True,
            "has_skills_header": True,
            "has_education_header": True,
            "has_experience_header": True,
            "has_certifications_header": True,
            "has_languages_header": True
        }
    }
    
    scored = score_resume(parsed_result)
    
    assert scored["completeness_score"] == 100.0
    # Confidence should be very high
    assert scored["confidence_score"] > 90.0

def test_scorer_mostly_empty():
    parsed_result = {
        "parsed_data": {
            "full_name": "John",
            "email": None,
            "phone": None,
            "location": None,
            "linkedin_url": None,
            "github_url": None,
            "skills": [],
            "education": [],
            "work_experience": [],
            "certifications": [],
            "languages": [],
            "summary": None
        },
        "metadata": {
            "has_name_entity": False,
            "has_skills_header": False,
            "has_education_header": False,
            "has_experience_header": False,
            "has_certifications_header": False,
            "has_languages_header": False
        }
    }
    
    scored = score_resume(parsed_result)
    
    # Only 1 key field populated: full_name (1/7 of 100% = 14.3%)
    assert scored["completeness_score"] == pytest.approx(14.3, 0.1)
    # Low confidence since name is heuristic fallback and no headers/other fields found
    assert scored["confidence_score"] == 50.0
