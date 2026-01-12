"""
Ultra-robust JSON parsing with advanced recovery
Handles severely malformed JSON from LLM responses
"""

import json
import re
import streamlit as st
import ast

def extract_json_string(response_text):
    """
    Extract JSON string from response with better detection
    
    Args:
        response_text (str): Raw response from LLM
        
    Returns:
        str: JSON string or None
    """
    if not response_text:
        return None
    
    response_text = response_text.strip()
    
    # Remove markdown blocks
    response_text = re.sub(r'```json\n?', '', response_text)
    response_text = re.sub(r'```\n?', '', response_text)
    response_text = re.sub(r'`+', '', response_text)
    
    # Find first { and last }
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        return None
    
    json_str = response_text[start_idx:end_idx + 1]
    return json_str


def fix_json_string(json_str):
    """
    Aggressively fix JSON formatting issues
    
    Args:
        json_str (str): Potentially malformed JSON
        
    Returns:
        str: Fixed JSON string
    """
    
    # Fix 1: Smart quotes to regular quotes
    json_str = json_str.replace('"', '"')
    json_str = json_str.replace('"', '"')
    json_str = json_str.replace("'", '"')
    json_str = json_str.replace('`', '"')
    
    # Fix 2: Remove newlines (can break JSON parsing)
    json_str = json_str.replace('\n', ' ')
    json_str = json_str.replace('\r', ' ')
    json_str = json_str.replace('\t', ' ')
    
    # Fix 3: Remove trailing commas before closing brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix 4: Remove multiple spaces
    json_str = re.sub(r'\s+', ' ', json_str)
    
    # Fix 5: Fix common LLM mistakes
    json_str = re.sub(r'\bNone\b', 'null', json_str)
    json_str = re.sub(r'\bTrue\b', 'true', json_str)
    json_str = re.sub(r'\bFalse\b', 'false', json_str)
    
    # Fix 6: Add quotes to unquoted keys (this is common)
    # Pattern: word: (key without quotes)
    # But be careful not to quote already quoted keys
    json_str = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
    
    # Fix 7: Fix escaped quotes inside string values
    # Replace \" with "
    json_str = re.sub(r'\\"', '"', json_str)
    
    # Fix 8: Remove control characters
    json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
    
    return json_str


def try_parse_json(json_str):
    """
    Try to parse JSON with multiple strategies
    
    Args:
        json_str (str): JSON string to parse
        
    Returns:
        dict: Parsed JSON or None
    """
    
    if not json_str:
        return None
    
    # Strategy 1: Direct parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try with fixes
    fixed_json = fix_json_string(json_str)
    try:
        return json.loads(fixed_json)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Try to extract and rebuild
    try:
        # Try to find array patterns and convert
        # This handles cases where array brackets might be wrong
        if '[' in fixed_json and ']' in fixed_json:
            # Replace [ with [ and ] with ]
            fixed_json = fixed_json.replace('[ ', '[').replace(' ]', ']')
            return json.loads(fixed_json)
    except json.JSONDecodeError:
        pass
    
    # Strategy 4: Try Python literal eval (last resort)
    try:
        python_obj = ast.literal_eval(fixed_json)
        return python_obj
    except (ValueError, SyntaxError):
        pass
    
    return None


def clean_json_response(response_text):
    """
    Complete JSON extraction and cleaning pipeline
    
    Args:
        response_text (str): Raw response from LLM
        
    Returns:
        dict: Parsed JSON or None
    """
    if not response_text:
        return None
    
    # Step 1: Extract JSON string
    json_str = extract_json_string(response_text)
    
    if not json_str:
        return None
    
    # Step 2: Try to parse
    parsed_json = try_parse_json(json_str)
    
    return parsed_json


def get_default_structure(doc_type="Resume"):
    """Get default structure based on type"""
    
    if doc_type == "Job Description":
        return {
            "jobTitle": "Not extracted",
            "requiredSkills": [],
            "preferredSkills": [],
            "minExperienceYears": 0,
            "requiredEducation": "Not specified",
            "responsibilities": []
        }
    else:  # Resume
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


def validate_data_types(data, doc_type):
    """
    Validate and fix data types
    
    Args:
        data (dict): Parsed data
        doc_type (str): "Resume" or "Job Description"
        
    Returns:
        dict: Data with corrected types
    """
    
    try:
        if doc_type == "Resume":
            # Ensure totalYearsExperience is a number
            if 'totalYearsExperience' in data:
                try:
                    data['totalYearsExperience'] = int(float(str(data['totalYearsExperience']).replace(',', '')))
                except (ValueError, TypeError, AttributeError):
                    data['totalYearsExperience'] = 0
            
            # Ensure skills is a list
            if 'skills' in data:
                if not isinstance(data['skills'], list):
                    data['skills'] = []
                else:
                    # Ensure each skill has 'name'
                    new_skills = []
                    for skill in data['skills']:
                        if isinstance(skill, dict):
                            if 'name' not in skill or not skill['name']:
                                continue
                            new_skills.append(skill)
                        elif isinstance(skill, str):
                            new_skills.append({'name': skill, 'proficiency': 'unknown'})
                    data['skills'] = new_skills
            
            # Ensure education is a list
            if 'education' in data:
                if not isinstance(data['education'], list):
                    data['education'] = []
            
            # Ensure experienceDetails is a list
            if 'experienceDetails' in data:
                if not isinstance(data['experienceDetails'], list):
                    data['experienceDetails'] = []
        
        else:  # Job Description
            # Ensure minExperienceYears is a number
            if 'minExperienceYears' in data:
                try:
                    data['minExperienceYears'] = int(float(str(data['minExperienceYears']).replace(',', '')))
                except (ValueError, TypeError, AttributeError):
                    data['minExperienceYears'] = 0
            
            # Ensure requiredSkills is a list
            if 'requiredSkills' in data:
                if not isinstance(data['requiredSkills'], list):
                    data['requiredSkills'] = []
                else:
                    # Convert to strings if needed
                    data['requiredSkills'] = [str(s) for s in data['requiredSkills'] if s]
            else:
                data['requiredSkills'] = []
            
            # Ensure preferredSkills is a list
            if 'preferredSkills' in data:
                if not isinstance(data['preferredSkills'], list):
                    data['preferredSkills'] = []
                else:
                    data['preferredSkills'] = [str(s) for s in data['preferredSkills'] if s]
            else:
                data['preferredSkills'] = []
    
    except Exception as e:
        pass  # Continue with best effort
    
    return data


def parse_with_validation(response_text, doc_type="Resume"):
    """
    Parse JSON with full validation and fallback
    This is the main function - use this in your code
    
    Args:
        response_text (str): Raw response from LLM
        doc_type (str): "Resume" or "Job Description"
        
    Returns:
        dict: Valid parsed data or default structure
    """
    
    # Try to clean and parse
    data = clean_json_response(response_text)
    
    if not data:
        # Fall back to defaults
        return get_default_structure(doc_type)
    
    # Validate structure based on type
    if doc_type == "Job Description":
        required_fields = ['jobTitle', 'requiredSkills', 'minExperienceYears']
    else:  # Resume
        required_fields = ['role', 'totalYearsExperience', 'skills', 'education']
    
    # Check if all required fields exist
    missing_fields = [f for f in required_fields if f not in data or data.get(f) is None]
    
    if missing_fields:
        # Merge with defaults
        defaults = get_default_structure(doc_type)
        defaults.update({k: v for k, v in data.items() if v is not None})
        data = defaults
    
    # Validate data types
    data = validate_data_types(data, doc_type)
    
    return data