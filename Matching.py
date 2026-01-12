"""
Resume-JD Matching Application
Main application file - orchestrates file processing, matching, and UI
Supports both Single and Batch resume processing with Database & Dashboard
"""

import streamlit as st
from pathlib import Path
import pdfplumber
from docx import Document
import re
import requests
import json
from datetime import datetime

# Import from separate modules
from matching_engine import calculate_match, get_scoring_breakdown
from ui_components import (
    setup_page_config,
    display_header,
    display_sidebar_info,
    display_mode_selector,
    display_single_upload_section,
    display_analyze_button,
    display_batch_upload_section,
    display_batch_process_button,
    display_results,
    display_batch_results,
    show_error_message,
    show_success_message,
    show_warning_message,
    show_info_message,
    show_loading_spinner
)

# Import JSON parser
from json_parser import parse_with_validation

# Import database
from database import DatabaseManager

# ==================== CONFIGURATION ====================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:latest"

# Initialize database
db = DatabaseManager()

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
    """Call Llama via local Ollama"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,  # Lower temperature for more consistent JSON
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
    with show_loading_spinner("Testing model..."):
        result = call_llama(test_prompt)
    if result:
        show_success_message("✅ Model is working!")
        st.write(f"Response: {result[:100]}")
    else:
        show_error_message("❌ Model test failed")

# ==================== DATA EXTRACTION ====================

EXTRACTION_PROMPT_TEMPLATE = """Extract resume data as JSON. Return ONLY valid JSON.

RESUME TEXT:
{content}

Return this exact JSON structure. Use null for missing values. Use empty arrays [] for lists.

{{
  "role": "job title here",
  "totalYearsExperience": 0,
  "skills": [
    {{"name": "Python"}},
    {{"name": "Django"}}
  ],
  "education": [
    {{"degree": "Bachelor", "field": "CS", "institution": "MIT", "year": 2020}}
  ],
  "experienceDetails": [
    {{"role": "Developer", "years": 5, "company": "Google"}}
  ],
  "certifications": [],
  "responsibilities": [],
  "keyAchievements": [],
  "technologies": [],
  "softSkills": [],
  "languages": [],
  "summary": "brief summary"
}}

RULES:
- Return ONLY the JSON object
- No markdown code blocks
- No explanations
- No extra text
- Use double quotes for all strings
- Numbers must be numbers (not strings)
- All arrays must be valid JSON arrays
- Use null for empty/missing values"""

JD_PROMPT_TEMPLATE = """Extract job requirements as JSON. Return ONLY valid JSON.

JOB DESCRIPTION TEXT:
{content}

Return this exact JSON structure. Use null for missing values. Use empty arrays [] for lists.

{{
  "jobTitle": "job title here",
  "minExperienceYears": 0,
  "requiredEducation": "Bachelor",
  "requiredSkills": ["Python", "Django"],
  "preferredSkills": [],
  "responsibilities": ["responsibility 1"]
}}

RULES:
- Return ONLY the JSON object
- No markdown code blocks
- No explanations
- No extra text
- Use double quotes for all strings
- Numbers must be numbers (not strings)
- All arrays must be valid JSON arrays
- Use null for missing/empty values
- requiredSkills must be an array of strings"""

def extract_structured_data(text, doc_type="Resume"):
    """Extract structured data from text using Llama"""
    
    if doc_type == "Job Description":
        prompt = JD_PROMPT_TEMPLATE
    else:
        prompt = EXTRACTION_PROMPT_TEMPLATE
    
    prompt = prompt.format(content=text, doc_type=doc_type)
    
    response_text = call_llama(prompt)
    
    if response_text is None:
        return None
    
    # 🆕 USE NEW PARSER
    data = parse_with_validation(response_text, doc_type)
    
    # 🆕 SHOW DEBUG INFO IN BATCH MODE
    if data and data.get('role') == 'Not extracted' or (doc_type == "Job Description" and data.get('jobTitle') == 'Not extracted'):
        with st.expander(f"🔧 Debug - {doc_type} Parsing"):
            st.warning(f"⚠️ {doc_type} extraction had issues")
            st.write(f"**Raw response (first 300 chars):**")
            st.code(response_text[:300])
    
    return data if data else None

# ==================== SINGLE RESUME MODE ====================

def process_single_mode():
    """Process single resume matching"""
    
    # Upload section
    resume_file, resume_text_input, jd_file, jd_text_input = display_single_upload_section()
    st.divider()
    
    # Analyze button
    if display_analyze_button("🔍 Analyze Match"):
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
                with show_loading_spinner("🤖 Extracting resume data..."):
                    resume_data = extract_structured_data(resume_text, "Resume")
                
                if resume_data:
                    # Extract JD data
                    with show_loading_spinner("🤖 Extracting JD data..."):
                        jd_data = extract_structured_data(jd_text, "Job Description")
                    
                    if jd_data:
                        # Calculate match - LOCAL MATCHING (NO LLAMA CALL)
                        with show_loading_spinner("🔄 Calculating match scores..."):
                            matching_results = calculate_match(resume_data, jd_data)
                        
                        if matching_results:
                            st.session_state.resume_data = resume_data
                            st.session_state.jd_data = jd_data
                            st.session_state.matching_results = matching_results
                            st.session_state.mode = 'single'
                            show_success_message("✅ Analysis Complete!")
                            
                            # SAVE TO DATABASE
                            try:
                                resume_filename = resume_file.name if resume_file else "Pasted Resume"
                                job_title = jd_data.get('jobTitle', 'Unknown Job')
                                
                                match_id = db.save_single_match(
                                    resume_name=resume_filename,
                                    job_title=job_title,
                                    resume_data=resume_data,
                                    jd_data=jd_data,
                                    matching_result=matching_results
                                )
                                
                                st.info(f"💾 Saved to database (ID: {match_id})")
                                
                            except Exception as e:
                                st.warning(f"⚠️ Could not save to database: {e}")
    
    # Display results if available
    if 'matching_results' in st.session_state and st.session_state.mode == 'single':
        display_results(
            st.session_state.matching_results,
            st.session_state.resume_data,
            st.session_state.jd_data
        )

# ==================== BATCH RESUME MODE ====================

def process_batch_mode():
    """Process batch resume matching"""
    
    # Upload section
    jd_file, jd_text_input, resume_files = display_batch_upload_section()
    st.divider()
    
    # Process button
    if display_batch_process_button():
        if not resume_files:
            show_error_message("Please upload at least one resume")
            return
        
        if not (jd_file or jd_text_input):
            show_error_message("Please provide job description")
            return
        
        if not check_ollama_connection():
            show_error_message("❌ Cannot reach Ollama. Please start it with: `ollama serve`")
            return
        
        # Extract JD once
        final_jd_text = jd_text_input
        if jd_file:
            extracted = process_file(jd_file)
            if extracted:
                final_jd_text = extracted
        
        with show_loading_spinner("🤖 Extracting job description..."):
            jd_data = extract_structured_data(final_jd_text, "Job Description")
        
        if not jd_data:
            show_error_message("Failed to extract JD")
            return
        
        # Process each resume
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, resume_file in enumerate(resume_files):
            # Update progress
            progress = (idx + 1) / len(resume_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {idx + 1}/{len(resume_files)}: {resume_file.name}")
            
            # Extract resume
            resume_text = process_file(resume_file)
            if not resume_text:
                show_warning_message(f"Failed to extract {resume_file.name}")
                continue
            
            resume_data = extract_structured_data(resume_text, "Resume")
            if not resume_data:
                show_warning_message(f"Failed to parse {resume_file.name}")
                continue
            
            # Match
            matching_result = calculate_match(resume_data, jd_data)
            if matching_result:
                results.append({
                    'filename': resume_file.name,
                    'resume_data': resume_data,
                    'matching_result': matching_result
                })
        
        progress_bar.empty()
        status_text.empty()
        
        if not results:
            show_error_message("No valid resumes to process")
            return
        
        # Sort by score
        results.sort(key=lambda x: x['matching_result']['overallScore'], reverse=True)
        
        batch_data = {
            'results': results,
            'jd_data': jd_data,
            'mode': 'batch',
            'total_processed': len(resume_files),
            'total_valid': len(results)
        }
        
        st.session_state.batch_data = batch_data
        st.session_state.mode = 'batch'
        show_success_message("✅ Batch Processing Complete!")
        
        # SAVE TO DATABASE
        try:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            job_title = jd_data.get('jobTitle', 'Unknown Job')
            
            db.save_batch_result(
                batch_id=batch_id,
                job_title=job_title,
                results=results,
                jd_data=jd_data
            )
            
            st.info(f"💾 Batch saved to database (ID: {batch_id})")
            
        except Exception as e:
            st.warning(f"⚠️ Could not save batch to database: {e}")
    
    # Display batch results if available
    if 'batch_data' in st.session_state and st.session_state.mode == 'batch':
        display_batch_results(st.session_state.batch_data)

# ==================== MAIN APPLICATION ====================

def main():
    """Main application flow with navigation"""
    setup_page_config()
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🎯 Resume Matcher")
        page = st.radio(
            "Navigate to:",
            ["🔍 Matcher", "📊 Dashboard"],
            label_visibility="collapsed"
        )
    
    # Page routing
    if page == "🔍 Matcher":
        # Matcher Page
        display_header()
        display_sidebar_info(
            OLLAMA_BASE_URL,
            OLLAMA_MODEL,
            check_ollama_connection,
            test_model
        )
        
        # Mode selection
        mode = display_mode_selector()
        
        st.divider()
        
        if "📄 Single Resume" in mode:
            process_single_mode()
        else:
            process_batch_mode()
    
    else:  # Dashboard Page
        # Import and display dashboard
        from dashboard import display_dashboard
        display_dashboard()

if __name__ == "__main__":
    main()