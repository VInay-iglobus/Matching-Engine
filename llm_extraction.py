"""
LLM Extraction Module - FIXED VERSION
Better prompts + aggressive extraction for accurate data
"""

import json
import re
from datetime import datetime
import hashlib
import logging
import requests
import urllib3
import pdfplumber
from docx import Document
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "llama3.2:latest",
    "temperature": 0.0,
    "top_p": 0.1,
    "top_k": 10,
    "num_predict": 500,  # INCREASED - get more detailed responses
    "repeat_penalty": 1.1,
}
def init_cache():
    """Initialize in-memory cache"""
    return {}

extraction_cache = init_cache()


def call_ollama(prompt, max_retries=3, validate_func=None):
    """Call Ollama with caching"""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    if prompt_hash in extraction_cache:
        logger.info("✅ Using cached response")
        return extraction_cache[prompt_hash]
    
    base_url = OLLAMA_CONFIG["base_url"]
    model = OLLAMA_CONFIG["model"]
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🤖 Ollama attempt {attempt + 1}/{max_retries}")
            
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": OLLAMA_CONFIG["temperature"],
                    "top_p": OLLAMA_CONFIG["top_p"],
                    "top_k": OLLAMA_CONFIG["top_k"],
                    "num_predict": OLLAMA_CONFIG["num_predict"],
                    "repeat_penalty": OLLAMA_CONFIG["repeat_penalty"],
                },
                timeout=120,
                verify=False
            )
            
            if response.status_code == 200:
                text = response.json()
                response_text = text.get("response", "").strip()
                if not response_text:
                    logger.info(f"⚠️ Empty response from LLM")
                    continue
                if validate_func:
                    is_valid, msg = validate_func(response_text)
                    if not is_valid:
                        logger.warning(f"❌ Validation failed: {msg}")
                        if attempt < max_retries - 1:
                            continue
                        return None
                extraction_cache[prompt_hash] = response_text
                logger.info("✅ Extraction successful!")
                return response_text
            else:
                logger.warning(f"⚠️ Ollama error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                raise Exception("❌ Ollama not running: Run 'ollama serve'")
            logger.warning("⏳ Retrying...")
        except requests.exceptions.Timeout:
            logger.warning("⏱️ Timeout, retrying...")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
    
    return None

def validate_json_response(response_text):
    """Validate JSON structure in response"""
    if not response_text or '{' not in response_text:
        return False, "No JSON found"
    
    start = response_text.find('{')
    end = response_text.rfind('}')
    
    if start == -1 or end == -1 or start >= end:
        return False, "Invalid JSON structure"
    
    json_str = response_text[start:end + 1]
    
    try:
        json.loads(json_str)
        return True, "Valid JSON"
    except:
        return False, "JSON parsing failed"

# ==================== IMPROVED PROMPTS ====================

EXTRACTION_PROMPT_RESUME = """TASK: Extract EXACTLY this JSON from resume. Return ONLY the JSON object, no text before/after.

RESUME:
{content}

REQUIRED JSON (return exactly this structure):
{{
  "role": "current or most recent job title",
  "totalYearsExperience": (total years as INTEGER),
  "domain": "primary domain/field (IT/Software, Backend Development, Frontend Development, AI/ML/Data Science, DevOps/Cloud, QA/Testing, Finance/Accounting, Healthcare, Sales/Marketing, HR/Recruitment, Finance/Banking, or Unknown)",
  "experienceDetails": [
    {{
      "role": "job title",
      "company": "company name",
      "startDate": "YYYY",
      "endDate": "YYYY or Current",
      "years": (duration in years as NUMBER)
    }}
  ],
  "skills": [
    {{
      "name": "technical skill name"
    }}
  ],
  "education": [
    {{
      "degree": "degree type",
      "field": "field of study",
      "year": (graduation year as INTEGER)
    }}
  ],
  "certifications": ["certification name"],
  "summary": "brief summary"
}}

RULES:
1. totalYearsExperience = SUM of all job years
2. role = Most recent job title ONLY
3. domain = Classify the primary industry/domain of the candidate's experience
4. skills = ONLY technical/professional skills (NO soft skills)
5. For each job, calculate years as: endDate_year - startDate_year
6. Return ONLY valid JSON, nothing else
7. All fields must be present (use null for missing values)
8. No trailing commas"""

EXTRACTION_PROMPT_JD = """TASK: Extract EXACTLY this JSON from job description. Return ONLY the JSON object, no text before/after.

JOB DESCRIPTION:
{content}

REQUIRED JSON (return exactly this structure):
{{
  "jobTitle": "primary job title",
  "minExperienceYears": (minimum years required as INTEGER),
  "domain": "primary domain/field (IT/Software, Backend Development, Frontend Development, AI/ML/Data Science, DevOps/Cloud, QA/Testing, Finance/Accounting, Healthcare, Sales/Marketing, HR/Recruitment, Finance/Banking, or Unknown)",
  "requiredEducation": "education requirement",
  "requiredSkills": ["skill1", "skill2", "skill3"],
  "preferredSkills": ["preferred_skill1", "preferred_skill2"],
  "description": "job description summary",
  "responsibilities": ["responsibility 1", "responsibility 2"],
  "benefits": ["benefit 1", "benefit 2"]
}}

RULES:
1. jobTitle = Main job title
2. minExperienceYears = Integer (e.g., "5 years" → 5)
3. domain = Classify the primary domain/field for this job role
4. requiredEducation = Degree requirement
5. requiredSkills = Required technical skills
6. Return ONLY valid JSON, nothing else
7. All fields must be present (use null for missing values)
8. No trailing commas"""
# ==================== FILE PROCESSING ====================
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text if text else None
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return None

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text if text else None
    except Exception as e:
        logger.info(f"Error reading DOCX: {e}")
        logger.error(f"DOCX extraction error: {e}")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:

        logger.error(f"TXT extraction error: {e}")
        return None

def process_file(uploaded_file):
    """Process uploaded file and extract text"""
    if uploaded_file is None:
        return None
    
    try:
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension == '.pdf':
            return extract_text_from_pdf(uploaded_file)
        elif file_extension in ['.docx', '.doc']:
            return extract_text_from_docx(uploaded_file)
        elif file_extension == '.txt':
            return extract_text_from_txt(uploaded_file)
        else:
            logger.error(f"Unsupported file format: {file_extension}")
            return None
    except Exception as e:
        logger.error(f"File processing error: {e}")
        return None
def extract_structured_data_stable(text, doc_type="Resume"):
    """Extract structured data with stability"""
    from json_parser import clean_json_response, parse_with_validation, post_process_extraction, validate_data_types
    
    if not text:
        logger.info("No text to extract")
        return None
    
    if doc_type == "Resume":
        prompt_template = EXTRACTION_PROMPT_RESUME
    else:
        prompt_template = EXTRACTION_PROMPT_JD
    
    prompt = prompt_template.format(content=text[:3000])
    
    logger.info(f"### 🔍 Extracting {doc_type}...")
    
    # Multi-pass extraction
    for attempt in range(2):
        logger.info(f"**Pass {attempt + 1}/2**: Extracting...")
        
        response = call_ollama(
            prompt,                                     
            max_retries=2,
            validate_func= validate_json_response
        )
        
        if not response:
            logger.info(f"Attempt {attempt + 1} failed")
            continue
        
        # Parse
        data = parse_with_validation(response, doc_type)
        
        if data:
            logger.info(f"✅ Pass {attempt + 1} successful")
            
            # Validate and process
            data = validate_data_types(data, doc_type)
            data = post_process_extraction(data, doc_type, text)
            
            return data
    
    logger.info(f"❌ Failed to extract {doc_type}")
    return None
        
def repair_json_string(json_str):
    """Repair common JSON issues"""
    if not json_str:
        return None
    
    json_str = json_str.replace('\n', ' ').replace('\r', ' ')
    json_str = re.sub(r'\s+', ' ', json_str)
    
    # Fix smart quotes
    json_str = json_str.replace('"', '"').replace('"', '"')
    json_str = json_str.replace(''', "'").replace(''', "'")
    
    # Remove trailing commas
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Python literals to JSON
    json_str = re.sub(r'\bNone\b', 'null', json_str)
    json_str = re.sub(r'\bTrue\b', 'true', json_str)
    json_str = re.sub(r'\bFalse\b', 'false', json_str)
    
    # Fix unquoted keys
    json_str = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)(\s*:)', r'\1"\2"\3', json_str)
    
    # Fix missing commas
    json_str = re.sub(r'(\})\s*(\{)', r'\1,\2', json_str)
    json_str = re.sub(r'(\])\s*(\[)', r'\1,\2', json_str)
    
    # Close unclosed brackets
    open_braces = json_str.count('{') - json_str.count('}')
    open_brackets = json_str.count('[') - json_str.count(']')
    
    if open_braces > 0:
        json_str += '}' * open_braces
    if open_brackets > 0:
        json_str += ']' * open_brackets
    
    return json_str


def try_parse_json(json_str):
    """Try to parse JSON"""
    if not json_str:
        raise Exception("Empty JSON string")
    
    # Try direct parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Try truncation at last valid position
    for i in range(len(json_str) - 1, 0, -1):
        if json_str[i] == '}':
            try:
                test_str = json_str[:i + 1]
                open_brackets = test_str.count('[') - test_str.count(']')
                if open_brackets > 0:
                    test_str += ']' * open_brackets
                return json.loads(test_str)
            except:
                continue
    
    raise Exception("Cannot parse JSON")


    
    