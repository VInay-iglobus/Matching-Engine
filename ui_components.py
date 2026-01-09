"""
UI Components Module
Handles all Streamlit UI display and layout logic
"""

import streamlit as st
from matching_logic import (
    get_scoring_breakdown,
    get_total_points,
    format_score_label,
    get_assessment
)

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Resume-JD Matcher",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def display_header():
    """Display page header and title"""
    st.title("🎯 AI-Powered Resume-JD Matching Engine (Local Llama 3.2)")
    st.markdown("*Extract, analyze, and match resumes using your local Llama 3.2*")

def display_sidebar_info(ollama_url, model_name, check_connection_callback, test_model_callback):
    """
    Display sidebar information and controls
    
    Args:
        ollama_url (str): Ollama server URL
        model_name (str): Model name
        check_connection_callback (function): Callback to check connection
        test_model_callback (function): Callback to test model
    """
    with st.sidebar:
        st.info(f"🤖 Model: **{model_name}**")
        st.info(f"🔌 Server: **{ollama_url}**")
        
        if st.button("🔌 Check Ollama Connection"):
            if check_connection_callback():
                st.success("✅ Ollama is connected and running!")
            else:
                st.error("❌ Cannot connect to Ollama")
                st.error("Make sure to run: `ollama serve`")
        
        if st.button("🧪 Test Model"):
            test_model_callback()

def display_upload_section():
    """
    Display file upload section for resume and JD
    
    Returns:
        tuple: (resume_file, resume_text_input, jd_file, jd_text_input)
    """
    st.header("Upload Documents & Analyze")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume")
        resume_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'doc', 'txt'],
            key='resume_uploader'
        )
        resume_text_input = st.text_area(
            "Or paste resume text",
            height=300,
            placeholder="Paste resume content here...",
            key='resume_text'
        )
    
    with col2:
        st.subheader("Job Description")
        jd_file = st.file_uploader(
            "Upload JD (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'doc', 'txt'],
            key='jd_uploader'
        )
        jd_text_input = st.text_area(
            "Or paste JD text",
            height=300,
            placeholder="Paste job description here...",
            key='jd_text'
        )
    
    st.divider()
    
    return resume_file, resume_text_input, jd_file, jd_text_input

def display_analyze_button():
    """
    Display analyze button
    
    Returns:
        bool: True if button clicked, False otherwise
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        return st.button("🔍 Extract & Analyze", use_container_width=True, key='analyze_btn')
    
    return False

def display_overall_score(overall_score):
    """
    Display overall match score with assessment
    
    Args:
        overall_score (int): Overall match score (0-100)
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.metric(
            "Overall Match Score",
            f"{overall_score}/100",
            delta=None
        )
        
        assessment = get_assessment(overall_score)
        color = assessment["color"]
        text = assessment["text"]
        
        st.write(f"{color} {text}")

def display_scoring_breakdown():
    """Display scoring breakdown configuration"""
    st.subheader("Scoring Breakdown")
    st.write("**Maximum Points Available:**")
    st.write("- Skills Match: **45 points**")
    st.write("- Experience Match: **25 points**")
    st.write("- Education Match: **30 points**")
    st.write(f"- **Total: {get_total_points()} points**")
    st.write("")
    st.write("*Score given only if criterion is MET*")
    st.write("*If NOT MET, that section gets 0 points*")

def display_criteria_analysis(criteria):
    """
    Display criteria analysis details
    
    Args:
        criteria (dict): Criteria analysis from matching result
    """
    st.subheader("Criteria Analysis")
    
    for criterion, analysis in criteria.items():
        met = analysis.get('met', False)
        details = analysis.get('details', 'No details')
        status = "✅ MET" if met else "❌ NOT MET"
        label = format_score_label(criterion)
        
        # Display with color coding
        if met:
            st.success(f"**{label}**: {status}")
        else:
            st.error(f"**{label}**: {status}")
        
        st.caption(details)

def display_score_breakdown(section_scores):
    """
    Display individual section scores
    
    Args:
        section_scores (dict): Scores for each section
    """
    st.subheader("Score Breakdown")
    
    total = 0
    for section, score in section_scores.items():
        color = "🟢" if score > 0 else "🔴"
        label = format_score_label(section)
        
        # Get max points for this section
        max_points = get_scoring_breakdown().get(section, {}).get('maxPoints', 0)
        
        st.write(f"{color} **{label}**: {score}/{max_points} points")
        total += score
    
    st.divider()
    st.metric("Total Score", f"{total}/{get_total_points()}")

def display_criteria_and_scores_section(results):
    """
    Display criteria analysis and scoring breakdown side by side
    
    Args:
        results (dict): Matching results
    """
    col1, col2 = st.columns(2)
    
    criteria = results.get('criteriaAnalysis', {})
    section_scores = results.get('sectionScores', {})
    
    with col1:
        display_scoring_breakdown()
        display_criteria_analysis(criteria)
    
    with col2:
        display_score_breakdown(section_scores)

def display_gaps_and_recommendations(results):
    """
    Display skill gaps and recommendations
    
    Args:
        results (dict): Matching results
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Skill Gaps")
        gaps = results.get('gaps', [])
        if gaps:
            for gap in gaps:
                st.warning(f"❌ {gap}")
        else:
            st.success("✅ No significant gaps found!")
    
    with col2:
        st.subheader("Recommendations")
        recommendations = results.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                st.info(f"💡 {rec}")
        else:
            st.success("✅ Strong candidate overall!")

def display_summary(results):
    """
    Display matching summary
    
    Args:
        results (dict): Matching results
    """
    st.subheader("Summary")
    st.info(results.get('summary', 'No summary available'))

def display_extracted_data(resume_data, jd_data):
    """
    Display extracted structured data
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
    """
    st.subheader("Extracted Structured Data")
    
    tab1, tab2 = st.tabs(["📄 Resume Data", "🎯 Job Description Data"])
    
    with tab1:
        st.write("**Resume Extraction Result:**")
        st.json(resume_data)
    
    with tab2:
        st.write("**Job Description Extraction Result:**")
        st.json(jd_data)

def display_download_button(results_json):
    """
    Display download button for results
    
    Args:
        results_json (dict): Complete results to download
    """
    import json
    
    st.download_button(
        label="📥 Download Results as JSON",
        data=json.dumps(results_json, indent=2),
        file_name="matching_results.json",
        mime="application/json"
    )

def display_results(results, resume_data, jd_data):
    """
    Display complete results section
    
    Args:
        results (dict): Matching results
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
    """
    st.divider()
    st.header("📈 Results")
    
    overall = results.get('overallScore', 0)
    
    # Overall score
    display_overall_score(overall)
    
    st.divider()
    
    # Criteria and scores
    display_criteria_and_scores_section(results)
    
    st.divider()
    
    # Gaps and recommendations
    display_gaps_and_recommendations(results)
    
    st.divider()
    
    # Summary
    display_summary(results)
    
    st.divider()
    
    # Extracted data
    display_extracted_data(resume_data, jd_data)
    
    st.divider()
    
    # Download button
    results_json = {
        "resume": resume_data,
        "jd": jd_data,
        "matching": results
    }
    
    display_download_button(results_json)

def show_error_message(message):
    """
    Display error message
    
    Args:
        message (str): Error message to display
    """
    st.error(message)

def show_success_message(message):
    """
    Display success message
    
    Args:
        message (str): Success message to display
    """
    st.success(message)

def show_warning_message(message):
    """
    Display warning message
    
    Args:
        message (str): Warning message to display
    """
    st.warning(message)

def show_info_message(message):
    """
    Display info message
    
    Args:
        message (str): Info message to display
    """
    st.info(message)

def show_loading_spinner(message):
    """
    Show loading spinner context
    
    Args:
        message (str): Loading message
        
    Returns:
        context manager for spinner
    """
    return st.spinner(message)