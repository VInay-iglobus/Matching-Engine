"""
Resume-JD Matching Application
Main application file - orchestrates file processing, matching, and UI
"""

import streamlit as st
from pathlib import Path
import pdfplumber
from docx import Document
import re
import requests

# Import from separate modules
from matching_logic import calculate_match, get_scoring_breakdown
from ui_components import (
    setup_page_config,
    display_header,
    display_sidebar_info,
    display_upload_section,
    display_analyze_button,
    display_results,
    show_error_message,
    show_success_message,
    show_warning_message,
    show_info_message,
    show_loading_spinner
)

# ==================== CONFIGURATION ====================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

# ==================== FILE PROCESSING ====================

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        show_error_message(f"Error reading PDF: {e}")
        return None

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        show_error_message(f"Error reading DOCX: {e}")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        show_error_message(f"Error reading TXT: {e}")
        return None

def process_file(uploaded_file):
    """Process uploaded file and extract text"""
    if uploaded_file is None:
        return None
    
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(uploaded_file)
    elif file_extension == '.txt':
        return extract_text_from_txt(uploaded_file)
    else:
        show_error_message(f"Unsupported file format: {file_extension}")
        return None

# ==================== OLLAMA INTEGRATION ====================

def check_ollama_connection():
    """Check if Ollama server is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_llama(prompt, max_retries=2):
    """Call Llama 3.2 via local Ollama"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                show_error_message(f"❌ Ollama error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                show_error_message("❌ Cannot connect to Ollama. Make sure it's running on http://localhost:11434")
                show_error_message("Start Ollama with: `ollama serve`")
                return None
            show_warning_message(f"Connection attempt {attempt + 1} failed, retrying...")
        
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                show_error_message("❌ Request timed out. Your local Llama is taking too long.")
                return None
            show_warning_message(f"Timeout attempt {attempt + 1}, retrying...")
        
        except Exception as e:
            if attempt == max_retries - 1:
                show_error_message(f"❌ Error: {e}")
                return None
            show_warning_message(f"Attempt {attempt + 1} failed: {str(e)}")
    
    return None

def test_model():
    """Test if model is working"""
    test_prompt = "Say 'Ready' in one word."
    with show_loading_spinner("Testing Llama 3.2..."):
        result = call_llama(test_prompt)
    if result:
        show_success_message("✅ Llama 3.2 is working!")
        st.write(f"Response: {result[:100]}")
    else:
        show_error_message("❌ Model test failed")

# ==================== DATA EXTRACTION ====================

EXTRACTION_PROMPT_TEMPLATE = """You are an expert recruiter and data extraction specialist. 
Extract and structure all relevant information from the following {doc_type}.

{doc_type} Content:
{content}

IMPORTANT INSTRUCTIONS:
- Extract EVERY education entry (Bachelor, Master, PhD, Diploma, etc.)
- Extract EVERY certification (AWS, Google Cloud, Microsoft, CompTIA, Cisco, etc.)
- Look for years/dates associated with degrees and certifications
- Calculate TOTAL years of experience by summing all roles
- Be thorough and extract all items mentioned

Please extract the information in the following JSON format. Be precise and extract EXACTLY what's mentioned:

{{
  "role": "Current job title or position (string)",
  "totalYearsExperience": number (sum of all experience years, or 0 if not found),
  "experienceDetails": [
    {{"role": "Position name", "years": number, "company": "Company name"}}
  ],
  "skills": [
    {{"name": "Skill name", "proficiency": "beginner|intermediate|advanced|expert"}}
  ],
  "education": [
    {{"degree": "Bachelor/Master/PhD/Diploma/etc", "field": "Field of study", "institution": "University/College name", "year": "Graduation year or null"}}
  ],
  "certifications": [
    {{"name": "Certification name", "issuer": "Issuing organization", "year": "Year obtained or null"}}
  ],
  "responsibilities": ["Key responsibility"],
  "keyAchievements": ["Achievement with metrics if available"],
  "technologies": ["Technology/Tool"],
  "softSkills": ["Soft skill"],
  "languages": ["Language - Proficiency level"],
  "summary": "Brief professional summary"
}}

Return ONLY valid JSON, no markdown or extra text. 
- If education is not found, use empty array []
- If certifications are not found, use empty array []
- Extract all degrees and certifications mentioned, even if incomplete information
- Do NOT skip any education or certification entries"""

JD_PROMPT_TEMPLATE = """You are an expert recruiter. Extract REQUIREMENTS from this JOB DESCRIPTION.
Content: {content}

Extract data in this JSON format:
{{
  "jobTitle": "Job Title",
  "requiredSkills": ["Must-have skill 1", "Must-have skill 2"],
  "preferredSkills": ["Nice-to-have skill 1"],
  "minExperienceYears": number,
  "requiredEducation": "Degree level required (e.g. Bachelor, Master, or Not specified)",
  "responsibilities": ["Responsibility 1"]
}}
Return ONLY valid JSON."""

def extract_structured_data(text, doc_type="Resume"):
    """Extract structured data from text using Llama"""
    import json
    
    if doc_type == "Job Description":
        prompt = JD_PROMPT_TEMPLATE
    else:
        prompt = EXTRACTION_PROMPT_TEMPLATE
    
    prompt = prompt.format(content=text, doc_type=doc_type)
    
    response_text = call_llama(prompt)
    
    if response_text is None:
        return None
    
    response_text = response_text.strip()
    
    # Remove markdown code blocks
    if response_text.startswith('```json'): response_text = response_text[7:]
    if response_text.startswith('```'): response_text = response_text[3:]
    if response_text.endswith('```'): response_text = response_text[:-3]
    
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(response_text.strip())
    except Exception as e:
        show_error_message(f"Error parsing {doc_type} JSON: {e}")
        show_error_message("Raw response from Llama:")
        st.text(response_text[:500])
        
        show_warning_message(f"Using empty {doc_type} result - please check the input text")
        
        if doc_type == "Job Description":
            return {
                "jobTitle": "Not extracted",
                "requiredSkills": [],
                "preferredSkills": [],
                "minExperienceYears": 0,
                "requiredEducation": "Not specified",
                "responsibilities": []
            }
        else:
            return {
                "role": "Not extracted",
                "totalYearsExperience": 0,
                "experienceDetails": [],
                "skills": [],
                "education": [],
                "certifications": [],
                "responsibilities": [],
                "keyAchievements": [],
                "technologies": [],
                "softSkills": [],
                "languages": [],
                "summary": "Error parsing this document"
            }

# ==================== MAIN APPLICATION ====================

def main():
    """Main application flow"""
    setup_page_config()
    display_header()
    display_sidebar_info(
        OLLAMA_BASE_URL,
        OLLAMA_MODEL,
        check_ollama_connection,
        test_model
    )
    
    # Main content tab
    tab1 = st.tabs(["📤 Upload, Analyze & Results"])[0]
    
    with tab1:
        # Upload section
        resume_file, resume_text_input, jd_file, jd_text_input = display_upload_section()
        st.divider()
        
        # Analyze button
        if display_analyze_button():
            if not check_ollama_connection():
                show_error_message("❌ Cannot reach Ollama. Please start it with: `ollama serve`")
            else:
                # Get resume text
                resume_text = resume_text_input
                if resume_file:
                    extracted = process_file(resume_file)
                    if extracted:
                        resume_text = extracted
                
                # Get JD text
                jd_text = jd_text_input
                if jd_file:
                    extracted = process_file(jd_file)
                    if extracted:
                        jd_text = extracted
                
                if not resume_text or not jd_text:
                    show_error_message("Please provide both resume and job description")
                else:
                    # Extract resume data
                    with show_loading_spinner("🤖 Extracting resume data with Llama 3.2..."):
                        resume_data = extract_structured_data(resume_text, "Resume")
                    
                    if resume_data:
                        # Extract JD data
                        with show_loading_spinner("🤖 Extracting JD data with Llama 3.2..."):
                            jd_data = extract_structured_data(jd_text, "Job Description")
                        
                        if jd_data:
                            # Calculate match
                            with show_loading_spinner("🔄 Calculating match scores with Llama 3.2..."):
                                matching_results = calculate_match(resume_data, jd_data)
                            
                            if matching_results:
                                st.session_state.resume_data = resume_data
                                st.session_state.jd_data = jd_data
                                st.session_state.matching_results = matching_results
                                show_success_message("✅ Analysis Complete!")
                                
                                # Debug: Show raw matching result
                                with st.expander("🔧 Debug - Raw Matching Result"):
                                    st.json(matching_results)
        
        # Display results if available
        if 'matching_results' in st.session_state:
            display_results(
                st.session_state.matching_results,
                st.session_state.resume_data,
                st.session_state.jd_data
            )

if __name__ == "__main__":
    main()