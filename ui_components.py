"""
UI Components Module
Handles all Streamlit UI display and layout logic
Updated for Single & Batch Processing
"""

import streamlit as st
import pandas as pd
import json
from matching_engine import (
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
    st.title("🎯 AI-Powered Resume-JD Matching Engine")
    st.markdown("*Extract, analyze, and match resumes using local Llama 3.2*")

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

def display_mode_selector():
    """
    Display mode selection UI
    
    Returns:
        str: Selected mode ('Single' or 'Batch')
    """
    st.subheader("🎯 Processing Mode")
    
    mode = st.radio(
        "Select processing mode:",
        ["📄 Single Resume", "📂 Batch Processing"],
        horizontal=True
    )
    
    return mode

def display_single_upload_section():
    """
    Display file upload section for single resume mode
    
    Returns:
        tuple: (resume_file, resume_text_input, jd_file, jd_text_input)
    """
    st.header("📋 Single Resume Matching")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume")
        resume_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'doc', 'txt'],
            key='single_resume_uploader'
        )
        resume_text_input = st.text_area(
            "Or paste resume text",
            height=300,
            placeholder="Paste resume content here...",
            key='single_resume_text'
        )
    
    with col2:
        st.subheader("Job Description")
        jd_file = st.file_uploader(
            "Upload JD (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'doc', 'txt'],
            key='single_jd_uploader'
        )
        jd_text_input = st.text_area(
            "Or paste JD text",
            height=300,
            placeholder="Paste job description here...",
            key='single_jd_text'
        )
    
    st.divider()
    
    return resume_file, resume_text_input, jd_file, jd_text_input

def display_analyze_button(label="🔍 Analyze Match"):
    """
    Display analyze button
    
    Args:
        label (str): Button label
        
    Returns:
        bool: True if button clicked, False otherwise
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        return st.button(label, use_container_width=True, type="primary")
    
    return False

def display_batch_upload_section():
    """
    Display file upload section for batch processing mode
    
    Returns:
        tuple: (jd_file, jd_text_input, resume_files)
    """
    st.header("📂 Batch Resume Matching")
    st.write("Compare multiple resumes against a single job description")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Job Description")
        jd_file = st.file_uploader(
            "Upload JD (single file)",
            type=['pdf', 'docx', 'doc', 'txt'],
            key='batch_jd_uploader'
        )
        jd_text_input = st.text_area(
            "Or paste JD text",
            height=200,
            placeholder="Paste job description here...",
            key='batch_jd_text'
        )
    
    with col2:
        st.subheader("📊 Info")
        st.info("""
        **Batch Processing**
        - Upload multiple resumes
        - Compare to one JD
        - Rank candidates
        - Export results
        """)
    
    st.divider()
    
    st.subheader("📄 Resumes")
    resume_files = st.file_uploader(
        "Upload multiple resumes",
        type=['pdf', 'docx', 'doc', 'txt'],
        accept_multiple_files=True,
        key='batch_resume_uploader'
    )
    
    if resume_files:
        st.write(f"**{len(resume_files)} resumes selected**")
        
        with st.expander("📋 File List"):
            for idx, file in enumerate(resume_files, 1):
                st.write(f"{idx}. {file.name}")
    
    st.divider()
    
    return jd_file, jd_text_input, resume_files

def display_batch_process_button():
    """
    Display batch process button
    
    Returns:
        bool: True if button clicked
    """
    return st.button("🚀 Process All Resumes", use_container_width=True, type="primary")

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
    st.write("- Skills Match: **40 points**")
    st.write("- Experience Match: **35 points**")
    st.write("- Education Match: **25 points**")
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
    Display extracted structured data in tabs
    
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
    st.download_button(
        label="📥 Download Results as JSON",
        data=json.dumps(results_json, indent=2),
        file_name="matching_results.json",
        mime="application/json"
    )

def display_results(results, resume_data, jd_data):
    """
    Display complete results section for single match
    
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

def display_batch_results(batch_data):
    """
    Display batch processing results
    
    Args:
        batch_data (dict): Batch processing results
    """
    import plotly.express as px
    
    results = batch_data['results']
    jd_data = batch_data['jd_data']
    
    st.success(f"✅ Processed {batch_data['total_valid']}/{batch_data['total_processed']} resumes")
    
    st.divider()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    scores = [r['matching_result']['overallScore'] for r in results]
    
    with col1:
        st.metric("Total Candidates", len(results))
    with col2:
        st.metric("Average Score", f"{sum(scores)/len(scores):.1f}")
    with col3:
        st.metric("Top Score", max(scores))
    with col4:
        st.metric("Lowest Score", min(scores))
    
    st.divider()
    
    # Ranking table
    st.subheader("🏆 Candidate Rankings")
    
    ranking_data = []
    for rank, result in enumerate(results, 1):
        matching = result['matching_result']
        criteria = matching['criteriaAnalysis']
        
        ranking_data.append({
            'Rank': rank,
            'Candidate': result['filename'],
            'Score': matching['overallScore'],
            'Assessment': matching['assessment']['text'],
            'Experience': '✅' if criteria['experienceMatch']['met'] else '❌',
            'Education': '✅' if criteria['educationMatch']['met'] else '❌',
            'Skills': f"{criteria['skillsMatch']['percentage']}%"
        })
    
    df = pd.DataFrame(ranking_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Score distribution chart
    st.subheader("📊 Score Distribution")
    
    fig = px.histogram(
        df,
        x='Score',
        nbins=10,
        title='Score Distribution Across Candidates',
        labels={'Score': 'Overall Match Score'},
        color_discrete_sequence=['#4ECDC4']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Top candidate details
    st.subheader("🌟 Top Candidate Details")
    top_result = results[0]
    
    with st.expander("View Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**File**: {top_result['filename']}")
            st.write(f"**Overall Score**: {top_result['matching_result']['overallScore']}/100")
            st.write(f"**Assessment**: {top_result['matching_result']['assessment']['text']}")
        
        with col2:
            st.write("**Criteria Analysis**:")
            for criterion, analysis in top_result['matching_result']['criteriaAnalysis'].items():
                status = "✅ MET" if analysis['met'] else "❌ NOT MET"
                st.write(f"- {format_score_label(criterion)}: {status}")
    
    st.divider()
    
    # Export options
    st.subheader("📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        json_data = json.dumps({
            'jd': jd_data,
            'results': [
                {
                    'filename': r['filename'],
                    'score': r['matching_result']['overallScore'],
                    'assessment': r['matching_result']['assessment']['text'],
                    'criteria': r['matching_result']['criteriaAnalysis']
                }
                for r in results
            ]
        }, indent=2)
        
        st.download_button(
            "📄 JSON",
            json_data,
            "batch_results.json",
            "application/json"
        )
    
    with col2:
        # CSV export
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📊 CSV",
            csv_data,
            "batch_results.csv",
            "text/csv"
        )
    
    with col3:
        st.info("📋 CSV can be opened in Excel")
    
    st.divider()
    
    # Compare selected
    st.subheader("🔄 Compare Candidates")
    
    if st.checkbox("Select candidates to compare"):
        selected_indices = st.multiselect(
            "Choose candidates:",
            range(len(results)),
            format_func=lambda i: f"#{i+1} - {results[i]['filename']} ({results[i]['matching_result']['overallScore']}/100)"
        )
        
        if selected_indices:
            comparison_df = df.iloc[selected_indices]
            st.dataframe(comparison_df, use_container_width=True)

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