"""CV Analysis module using Google Gemini AI."""

import json
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
from docx import Document
from google import genai
from google.genai.types import GenerateContentConfig


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX."""
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text.strip()


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_text_from_file(file_path: str) -> str:
    """Extract text from CV file (PDF, DOCX, or TXT)."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {ext}. Supported: .pdf, .docx, .txt"
        )


def analyze_cv_with_gemini(
    cv_text: str, api_key: str, model: str = "gemini-2.5-flash"
) -> dict[str, Any]:
    """
    Analyze CV text using Google Gemini AI with structured outputs.

    Args:
        cv_text: Extracted CV text
        api_key: Gemini API key
        model: Gemini model to use

    Returns:
        Dictionary with extracted job search parameters
    """
    client = genai.Client(api_key=api_key)

    # Define response schema for structured output
    response_schema = {
        "type": "object",
        "properties": {
            "job_titles": {
                "type": "array",
                "description": "Exactly 3 relevant job titles - include the person's current/recent role plus 2 similar/related positions they could apply for",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 3,
            },
            "skills": {
                "type": "array",
                "description": "Top 5-7 technical keywords for job matching",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 7,
            },
            "experience_years": {
                "type": "integer",
                "description": "Total years of professional experience",
            },
            "experience_level": {
                "type": "string",
                "description": "Experience level",
                "enum": ["entry", "mid", "mid_senior", "senior"],
            },
            "languages": {
                "type": "object",
                "properties": {
                    "programming": {"type": "array", "items": {"type": "string"}},
                    "spoken": {
                        "type": "array",
                        "description": "2-letter language codes (e.g., en, de, fr)",
                        "items": {"type": "string"},
                    },
                },
                "required": ["programming", "spoken"],
            },
            "exclude_keywords": {
                "type": "array",
                "description": "Keywords to exclude from job search based on experience level",
                "items": {"type": "string"},
            },
        },
        "required": [
            "job_titles",
            "skills",
            "experience_years",
            "experience_level",
            "languages",
            "exclude_keywords",
        ],
    }

    prompt = f"""You are an expert CV analyzer for job search automation.

Extract structured data from the following resume/CV to help the person create automated job search alerts.

**Instructions:**
1. Identify the person's job search profile based on their experience
2. Extract ONLY information that's explicitly mentioned or clearly inferable

**Key Guidelines:**

- **job_titles**: Provide EXACTLY 3 job titles:
  1. The person's current/most recent job title
  2. A similar/related role they could apply for
  3. A broader or related position in their field
  (Example: ["Digital Marketing Specialist", "Marketing Coordinator", "Content Marketing Manager"])
  
- **skills**: Top 5-7 relevant keywords (technical skills, tools, soft skills, domain knowledge)

- **experience_years**: Total professional experience as integer

- **experience_level**: 
  * "entry" (0-2 years)
  * "mid" (2-5 years)
  * "mid_senior" (5-10 years)
  * "senior" (10+ years)
  
- **languages**:
  * programming: Array of programming languages (leave empty if none)
  * spoken: 2-letter codes like ["en", "de", "fr"]
  
- **exclude_keywords**: Based on experience_level:
  * If entry/mid: ["senior", "lead", "principal", "staff", "manager", "director"]
  * If mid_senior/senior: ["junior", "intern", "graduate", "entry"]

**CV Content:**
{cv_text[:8000]}"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )

    # Parse JSON response - guaranteed to match schema
    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse Gemini response: {e}\nResponse: {response.text[:500]}"
        )
