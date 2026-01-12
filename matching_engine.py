"""
Matching Engine Module
Handles resume-JD matching logic and scoring calculations
Uses already extracted JSON data - NO Llama calls
"""

import streamlit as st

# SCORING CONFIGURATION
SCORING_CONFIG = {
    "skillsMatch": {
        "maxPoints": 40,
        "weight": "40%",
        "description": "Required skills match"
    },
    "experienceMatch": {
        "maxPoints": 35,
        "weight": "35%",
        "description": "Experience years requirement"
    },
    "educationMatch": {
        "maxPoints": 25,
        "weight": "25%",
        "description": "Education level requirement"
    }
}

TOTAL_POINTS = sum(config["maxPoints"] for config in SCORING_CONFIG.values())

# Education hierarchy for comparison
EDUCATION_HIERARCHY = {
    "high school": 1,
    "diploma": 1,
    "bachelor": 2,
    "bachelor's": 2,
    "master": 3,
    "master's": 3,
    "phd": 4,
    "doctorate": 4,
    "not specified": 0
}

# Assessment thresholds
ASSESSMENT_THRESHOLDS = {
    70: {"color": "🟢", "text": "Excellent Match"},
    50: {"color": "🟡", "text": "Good Match"},
    0: {"color": "🔴", "text": "Needs Review"}
}

def get_assessment(score):
    """Get color-coded assessment based on score"""
    for threshold in sorted(ASSESSMENT_THRESHOLDS.keys(), reverse=True):
        if score >= threshold:
            return ASSESSMENT_THRESHOLDS[threshold]
    return ASSESSMENT_THRESHOLDS[0]

def normalize_education(degree):
    """
    Normalize education degree to standard format
    
    Args:
        degree (str): Education degree
        
    Returns:
        tuple: (normalized_name, hierarchy_level)
    """
    if not degree:
        return "not specified", 0
    
    degree_lower = degree.lower().strip()
    
    for key, value in EDUCATION_HIERARCHY.items():
        if key in degree_lower:
            return key, value
    
    return degree_lower, 0

def check_experience_match(resume_data, jd_data):
    """
    Check if candidate's experience meets JD requirements
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
        
    Returns:
        dict: Experience match result
    """
    candidate_years = resume_data.get('totalYearsExperience', 0)
    required_years = jd_data.get('minExperienceYears', 0)
    
    # Ensure values are numbers
    try:
        candidate_years = float(candidate_years) if candidate_years else 0
        required_years = float(required_years) if required_years else 0
    except:
        candidate_years = 0
        required_years = 0
    
    met = candidate_years >= required_years
    
    if met:
        score = 35  # Full points if requirement met
        details = f"✅ Candidate has {int(candidate_years)} years experience. Required: {int(required_years)} years. MEETS requirement."
    else:
        score = 0  # Zero points if requirement not met
        details = f"❌ Candidate has {int(candidate_years)} years experience. Required: {int(required_years)} years. DOES NOT MEET requirement."
    
    return {
        "met": met,
        "candidateExperience": int(candidate_years),
        "requiredExperience": int(required_years),
        "details": details,
        "score": score
    }

def check_education_match(resume_data, jd_data):
    """
    Check if candidate's education meets JD requirements
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
        
    Returns:
        dict: Education match result
    """
    # Get candidate's highest education
    candidate_degree = "not specified"
    candidate_level = 0
    
    education_list = resume_data.get('education', [])
    if education_list:
        # Get the first education entry (should be highest)
        candidate_degree = education_list[0].get('degree', 'not specified')
        candidate_degree_norm, candidate_level = normalize_education(candidate_degree)
    
    # Get required education
    required_degree = jd_data.get('requiredEducation', 'not specified')
    required_degree_norm, required_level = normalize_education(required_degree)
    
    # Compare: candidate level must be >= required level
    met = candidate_level >= required_level
    
    if met:
        score = 25  # Full points if requirement met
        details = f"✅ Candidate has {candidate_degree}. Required: {required_degree}. MEETS requirement."
    else:
        score = 0  # Zero points if requirement not met
        details = f"❌ Candidate has {candidate_degree}. Required: {required_degree}. DOES NOT MEET requirement."
    
    return {
        "met": met,
        "candidateDegree": candidate_degree,
        "requiredDegree": required_degree,
        "details": details,
        "score": score
    }

def check_skills_match(resume_data, jd_data):
    """
    Check if candidate has required skills
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
        
    Returns:
        dict: Skills match result
    """
    # Extract candidate skills
    candidate_skills_list = resume_data.get('skills', [])
    candidate_skills = set()
    
    for skill in candidate_skills_list:
        if isinstance(skill, dict):
            skill_name = skill.get('name', '').lower().strip()
        else:
            skill_name = str(skill).lower().strip()
        
        if skill_name:
            candidate_skills.add(skill_name)
    
    # Extract required skills from JD
    required_skills_list = jd_data.get('requiredSkills', [])
    required_skills = set()
    
    for skill in required_skills_list:
        skill_name = str(skill).lower().strip()
        if skill_name:
            required_skills.add(skill_name)
    
    # Calculate match
    if not required_skills:
        return {
            "met": True,
            "candidateSkillsCount": len(candidate_skills),
            "requiredSkillsCount": 0,
            "percentage": 100,
            "matchedSkills": list(candidate_skills),
            "missingSkills": [],
            "details": "No specific skills required for this job.",
            "score": 40
        }
    
    matched_skills = candidate_skills.intersection(required_skills)
    missing_skills = required_skills - candidate_skills
    
    percentage = (len(matched_skills) / len(required_skills)) * 100
    
    # Threshold: candidate must have at least 50% of required skills
    threshold = 50
    met = percentage >= threshold
    
    if met:
        score = int((len(matched_skills) / len(required_skills)) * 40)
        details = f"✅ Candidate has {len(matched_skills)} out of {len(required_skills)} required skills ({int(percentage)}%). MEETS requirement (threshold: {threshold}%)."
    else:
        score = 0
        details = f"❌ Candidate has {len(matched_skills)} out of {len(required_skills)} required skills ({int(percentage)}%). DOES NOT MEET requirement (threshold: {threshold}%)."
    
    if missing_skills:
        details += f" Missing: {', '.join(sorted(missing_skills))}"
    
    return {
        "met": met,
        "candidateSkillsCount": len(matched_skills),
        "requiredSkillsCount": len(required_skills),
        "percentage": int(percentage),
        "matchedSkills": sorted(list(matched_skills)),
        "missingSkills": sorted(list(missing_skills)),
        "details": details,
        "score": score
    }

def calculate_gaps(resume_data, jd_data, criteria_analysis):
    """
    Calculate skill gaps and missing requirements
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
        criteria_analysis (dict): Criteria analysis results
        
    Returns:
        list: List of gaps
    """
    gaps = []
    
    # Experience gaps
    if not criteria_analysis['experienceMatch']['met']:
        gap = f"Experience: Needs {criteria_analysis['experienceMatch']['requiredExperience']} years, has {criteria_analysis['experienceMatch']['candidateExperience']} years"
        gaps.append(gap)
    
    # Education gaps
    if not criteria_analysis['educationMatch']['met']:
        gap = f"Education: Requires {criteria_analysis['educationMatch']['requiredDegree']}, has {criteria_analysis['educationMatch']['candidateDegree']}"
        gaps.append(gap)
    
    # Skills gaps
    if not criteria_analysis['skillsMatch']['met']:
        missing = criteria_analysis['skillsMatch']['missingSkills']
        if missing:
            gap = f"Skills: Missing {len(missing)} required skills - {', '.join(missing[:5])}"
            if len(missing) > 5:
                gap += f" and {len(missing) - 5} more"
            gaps.append(gap)
        else:
            gaps.append("Skills: Does not meet minimum skill requirements")
    
    return gaps

def calculate_recommendations(resume_data, jd_data, criteria_analysis, gaps):
    """
    Generate recommendations to improve match
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
        criteria_analysis (dict): Criteria analysis results
        gaps (list): List of gaps
        
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    # Experience recommendations
    if not criteria_analysis['experienceMatch']['met']:
        years_needed = criteria_analysis['experienceMatch']['requiredExperience'] - criteria_analysis['experienceMatch']['candidateExperience']
        recommendations.append(f"🔴 HIGH PRIORITY: Gain {int(years_needed)} more years of relevant experience (critical for this role)")
    
    # Education recommendations
    if not criteria_analysis['educationMatch']['met']:
        recommendations.append(f"Pursue {criteria_analysis['educationMatch']['requiredDegree']}'s degree")
    
    # Skills recommendations
    if not criteria_analysis['skillsMatch']['met']:
        missing = criteria_analysis['skillsMatch']['missingSkills']
        if missing:
            sample_skills = ', '.join(missing[:3])
            recommendations.append(f"Learn key missing skills: {sample_skills}")
            
            if len(missing) > 3:
                recommendations.append(f"Acquire remaining {len(missing) - 3} missing skills")
    
    # Positive recommendations
    if criteria_analysis['skillsMatch']['met']:
        recommendations.append("Strong technical skills match - excellent candidate")
    
    if criteria_analysis['experienceMatch']['met']:
        recommendations.append("Adequate work experience - ready for the role")
    
    return recommendations

def calculate_match(resume_data, jd_data):
    """
    Calculate match score between resume and job description
    Uses already extracted JSON data - NO Llama calls
    
    Args:
        resume_data (dict): Extracted resume data
        jd_data (dict): Extracted job description data
        
    Returns:
        dict: Matching results with scores and analysis
    """
    
    st.write("### 🔍 Analyzing Match...")
    
    # Show input data
    with st.expander("📊 Data Being Analyzed"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Resume Data:**")
            st.write(f"- Experience: {resume_data.get('totalYearsExperience', 0)} years")
            edu_list = resume_data.get('education', [])
            edu_display = edu_list[0].get('degree', 'Not specified') if edu_list else 'Not specified'
            st.write(f"- Education: {edu_display}")
            st.write(f"- Skills: {len(resume_data.get('skills', []))} skills")
        
        with col2:
            st.write("**JD Requirements:**")
            st.write(f"- Experience: {jd_data.get('minExperienceYears', 0)} years")
            st.write(f"- Education: {jd_data.get('requiredEducation', 'Not specified')}")
            st.write(f"- Skills: {len(jd_data.get('requiredSkills', []))} required")
    
    # Run all checks
    st.write("**Checking criteria...**")
    
    experience_result = check_experience_match(resume_data, jd_data)
    education_result = check_education_match(resume_data, jd_data)
    skills_result = check_skills_match(resume_data, jd_data)
    
    # Build criteria analysis
    criteria_analysis = {
        "experienceMatch": {
            "met": experience_result["met"],
            "candidateExperience": experience_result["candidateExperience"],
            "requiredExperience": experience_result["requiredExperience"],
            "details": experience_result["details"]
        },
        "educationMatch": {
            "met": education_result["met"],
            "candidateDegree": education_result["candidateDegree"],
            "requiredDegree": education_result["requiredDegree"],
            "details": education_result["details"]
        },
        "skillsMatch": {
            "met": skills_result["met"],
            "candidateSkillsCount": skills_result["candidateSkillsCount"],
            "requiredSkillsCount": skills_result["requiredSkillsCount"],
            "percentage": skills_result["percentage"],
            "matchedSkills": skills_result["matchedSkills"],
            "missingSkills": skills_result["missingSkills"],
            "details": skills_result["details"]
        }
    }
    
    # Build section scores
    section_scores = {
        "experienceMatch": experience_result["score"],
        "educationMatch": education_result["score"],
        "skillsMatch": skills_result["score"]
    }
    
    # Calculate gaps and recommendations
    gaps = calculate_gaps(resume_data, jd_data, criteria_analysis)
    recommendations = calculate_recommendations(resume_data, jd_data, criteria_analysis, gaps)
    
    # Calculate overall score
    overall_score = sum(section_scores.values())
    overall_score = min(100, max(0, overall_score))  # Clamp 0-100
    
    # Create summary
    matched_count = sum(1 for v in criteria_analysis.values() if v.get('met'))
    total_criteria = 3
    
    summary = f"Candidate matches {matched_count} out of {total_criteria} criteria. "
    if overall_score >= 70:
        summary += "Strong candidate recommended for interview."
    elif overall_score >= 50:
        summary += "Good candidate worth considering."
    else:
        summary += "Candidate needs improvement in key areas."
    
    # Build final result
    matching_result = {
        "criteriaAnalysis": criteria_analysis,
        "sectionScores": section_scores,
        "overallScore": overall_score,
        "assessment": get_assessment(overall_score),
        "gaps": gaps,
        "recommendations": recommendations,
        "summary": summary
    }
    
    st.success("✅ Analysis complete!")
    
    return matching_result

def get_scoring_breakdown():
    """Get scoring breakdown configuration"""
    return SCORING_CONFIG

def get_total_points():
    """Get total possible points"""
    return TOTAL_POINTS

def format_score_label(section_name):
    """Format section name for display"""
    return section_name.replace('Match', '').strip()

def validate_matching_result(result):
    """
    Validate matching result structure
    
    Args:
        result (dict): Matching result to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not result:
        return False, "No matching result"
    
    required_keys = ['criteriaAnalysis', 'sectionScores', 'overallScore']
    
    for key in required_keys:
        if key not in result:
            return False, f"Missing required key: {key}"
    
    return True, "Valid"