import pytest
from app.parser.fields import parse_fields, extract_email, extract_phone, extract_linkedin, extract_github, extract_location

SAMPLE_RESUME_TEXT = """
Jane Doe
Email: jane.doe@example.com | Phone: (555) 123-4567 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/janedoe

SUMMARY
A highly motivated Software Engineer with 5 years of experience in Python and full-stack development.

SKILLS
Python, JavaScript, SQL, Docker, AWS, Git, CI/CD, React

EXPERIENCE
Software Engineer | Tech Corp
June 2020 - Present
- Designed and built scalable web applications using Python and Django.
- Managed deployments on AWS using Docker.

Junior Developer | Startup Inc
May 2018 - June 2020
- Built frontend features in React.
- Wrote SQL queries and structured databases.

EDUCATION
B.S. in Computer Science
Stanford University | 2014 - 2018

CERTIFICATIONS
AWS Certified Solutions Architect
Certified ScrumMaster (CSM)

LANGUAGES
English (Native), Spanish (Conversational)
"""

def test_extract_deterministic_fields():
    # Test Email
    assert extract_email(SAMPLE_RESUME_TEXT) == "jane.doe@example.com"
    
    # Test Phone
    assert extract_phone(SAMPLE_RESUME_TEXT) == "(555) 123-4567"
    
    # Test LinkedIn
    assert extract_linkedin(SAMPLE_RESUME_TEXT) == "linkedin.com/in/janedoe"
    
    # Test GitHub
    assert extract_github(SAMPLE_RESUME_TEXT) == "github.com/janedoe"
    
    # Test Location
    assert extract_location(SAMPLE_RESUME_TEXT) == "San Francisco, CA"

def test_parse_fields_full():
    parsed = parse_fields(SAMPLE_RESUME_TEXT)
    data = parsed["parsed_data"]
    meta = parsed["metadata"]
    
    # Check fields
    assert data["email"] == "jane.doe@example.com"
    assert data["phone"] == "(555) 123-4567"
    assert "Python" in data["skills"]
    assert "React" in data["skills"]
    assert len(data["education"]) > 0
    assert data["education"][0]["institution"] == "Stanford University"
    assert data["education"][0]["dates"] == "2014 - 2018"
    
    assert len(data["work_experience"]) > 0
    assert data["work_experience"][0]["company"] == "Tech Corp"
    assert data["work_experience"][0]["title"] == "Software Engineer"
    
    # Check metadata headers
    assert meta["has_skills_header"] is True
    assert meta["has_education_header"] is True
    assert meta["has_experience_header"] is True
    assert meta["has_certifications_header"] is True
    assert meta["has_languages_header"] is True
