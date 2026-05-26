import os
import io
import pytest
from unittest.mock import patch
from app.parser.extractor import extract_text, extract_text_from_pdf, extract_text_from_docx
import docx

def test_extract_text_docx(tmp_path):
    # Create a real docx file in the temp path
    docx_path = tmp_path / "test.docx"
    doc = docx.Document()
    doc.add_paragraph("This is a simple test resume content for Python Developer.")
    doc.save(str(docx_path))
    
    # Extract and verify
    text = extract_text(str(docx_path), ".docx")
    assert "Python Developer" in text
    assert "simple test resume" in text

@patch('app.parser.extractor.extract_pdf_text')
def test_extract_text_pdf(mock_extract_pdf_text):
    # Mock the return value of pdfminer.high_level.extract_text
    mock_extract_pdf_text.return_value = "This is a mocked PDF resume for Jane Doe."
    
    dummy_pdf_bytes = b"%PDF-1.4..."
    text = extract_text(io.BytesIO(dummy_pdf_bytes), ".pdf")
    
    assert "Jane Doe" in text
    mock_extract_pdf_text.assert_called_once()

def test_unsupported_format():
    with pytest.raises(ValueError) as excinfo:
        extract_text(b"some content", ".txt")
    assert "Unsupported file format" in str(excinfo.value)
