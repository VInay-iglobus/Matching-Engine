"""
Ultra-robust JSON parsing for FastAPI backend
Handles severely malformed JSON from LLM responses
FIXED: Truncated JSON completion and aggressive recovery
"""

import json
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def extract_json_string(response_text):
    """
    Extract JSON string from response with truncation handling
    
    Args:
        response_text (str): Raw response from LLM
        
    Returns:
        str: JSON string or None
    """
    if not response_text:
        return None
    
    response_text = response_text.strip()
    
    # Remove markdown code blocks
    response_text = re.sub(r'```json\n?', '', response_text)
    response_text = re.sub(r'```\n?', '', response_text)
    response_text = re.sub(r'`+', '', response_text)
    
    # Find first { and last }
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx == -1:
        logger.warning("No JSON object found (no opening {)")
        return None
    
    if end_idx == -1:
        logger.warning("No closing bracket found. JSON is truncated.")
        # Try to auto-complete truncated JSON
        json_str = response_text[start_idx:]
        json_str = auto_complete_json(json_str)
        return json_str if json_str else None
    
    if start_idx >= end_idx:
        logger.warning("Invalid JSON boundaries")
        return None
    
    json_str = response_text[start_idx:end_idx + 1]
    logger.debug(f"Extracted JSON: {len(json_str)} chars")
    return json_str


def auto_complete_json(partial_json):
    """
    Auto-complete truncated JSON by closing all open structures
    
    Args:
        partial_json (str): Incomplete JSON string
        
    Returns:
        str: Completed JSON string
    """
    logger.info("Auto-completing truncated JSON")
    
    # Remove incomplete last field
    # Find last comma and check if content after it is incomplete
    last_comma = partial_json.rfind(',')
    if last_comma != -1:
        after_comma = partial_json[last_comma:].strip()
        # If after comma is short and has unmatched quotes, it's incomplete
        if len(after_comma) < 100 and ('"' in after_comma and after_comma.count('"') % 2 != 0):
            logger.debug("Removing incomplete field after last comma")
            partial_json = partial_json[:last_comma]
    
    # Count open structures
    open_braces = partial_json.count('{') - partial_json.count('}')
    open_brackets = partial_json.count('[') - partial_json.count(']')
    
    logger.info(f"Open braces: {open_braces}, Open brackets: {open_brackets}")
    
    # Close all open structures
    if open_brackets > 0:
        partial_json += ']' * open_brackets
    if open_braces > 0:
        partial_json += '}' * open_braces
    
    logger.info(f"Auto-completed: added {open_brackets} brackets and {open_braces} braces")
    return partial_json


def escape_newlines_in_strings(json_str):
    """Escape newlines that are inside string values"""
    if not json_str:
        return json_str
        
    result = []
    in_string = False
    escape = False
    
    for char in json_str:
        if in_string:
            if char == '"' and not escape:
                in_string = False
                result.append(char)
            elif char == '\\' and not escape:
                escape = True
                result.append(char)
            elif char == '\n':
                # Replace newline with \n literal
                result.append('\\n')
                escape = False 
            elif char == '\r':
                # Skip carriage returns in strings
                pass 
            else:
                escape = False
                result.append(char)
        else:
            if char == '"':
                in_string = True
            result.append(char)
            
    return "".join(result)


def fix_json_string(json_str):
    """
    Aggressively fix JSON formatting issues in multiple passes
    
    Args:
        json_str (str): Potentially malformed JSON
        
    Returns:
        str: Fixed JSON string
    """
    if not json_str:
        return None
    
    logger.debug("Starting JSON fixes")

    # Fix 0: Handle unescaped newlines in strings first (common LLM error)
    # This prevents the regexes below from seeing broken lines
    json_str = escape_newlines_in_strings(json_str)
    
    # Fix 1: Smart quotes to regular quotes
    json_str = json_str.replace('"', '"')  # Left double quotation mark
    json_str = json_str.replace('"', '"')  # Right double quotation mark
    
    # Fix 2: Remove trailing commas before closing brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix 3: Fix Python boolean/None to JSON equivalents
    json_str = re.sub(r'\bNone\b', 'null', json_str)
    json_str = re.sub(r'\bTrue\b', 'true', json_str)
    json_str = re.sub(r'\bFalse\b', 'false', json_str)
    
    # Fix 4: Add quotes to unquoted keys
    # Use a more specific regex to avoid matching inside strings (though tricky with regex alone)
    # The simple regex approach is imperfect but often works for simple keys.
    # We'll try to be conservative: match strictly expected key patterns at start of line or after {/,
    json_str = re.sub(
        r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:',
        r'\1"\2":',
        json_str
    )
    
    # Fix 5: Fix common incomplete patterns - "field": "value (missing closing quote)
    # This matching is risky if it matches across lines or complex structures.
    # We should let aggressive recovery handle structural issues if possible.
    # But let's keep a safe version for simple cases.
    # json_str = re.sub(r':\s*"([^"]*?)(?=,|\}|\])', r': "\1"', json_str) 
    # ^ DISABLED: Too risky, can match across fields if newlines are missing
    
    # Fix 6: Handle missing commas between array elements
    json_str = re.sub(r'}\s*{', '},{', json_str)
    json_str = re.sub(r'\]\s*\[', '],[', json_str)
    
    # Fix 7 is removed as it often corrupts valid strings with spaces using the naive logic
    
    # Fix 8: Remove control characters (except newline/tab which are valid whitespace)
    json_str = ''.join(
        char for char in json_str 
        if ord(char) >= 32 or char in '\n\r\t'
    )
    
    logger.debug("JSON fixes complete")
    return json_str


def aggressive_json_recovery(json_str):
    """
    Last resort: aggressive recovery for severely malformed JSON
    Finds last complete structure and closes everything properly,
    ignoring braces/brackets inside strings.
    """
    logger.info("Attempting aggressive JSON recovery")
    
    # Remove any text before first {
    start = json_str.find('{')
    if start >= 0:
        json_str = json_str[start:]
    else:
        return json_str

    # State tracking
    in_string = False
    escape = False
    depth_braces = 0
    depth_brackets = 0
    
    # We will rebuild the string to ensure we don't have partial multi-byte chars or other oddities,
    # but primarily to handle cutting off at the right spot if needed.
    # Actually, just finding the cut-off point is enough.
    
    valid_len = 0
    
    for i, char in enumerate(json_str):
        if in_string:
            if char == '"' and not escape:
                in_string = False
            elif char == '\\' and not escape:
                escape = True
            else:
                escape = False
        else:
            if char == '"':
                in_string = True
            elif char == '{':
                depth_braces += 1
            elif char == '}':
                depth_braces -= 1
            elif char == '[':
                depth_brackets += 1
            elif char == ']':
                depth_brackets -= 1
        
        # If depths go negative, we have text AFTER the JSON closed (or malformed)
        # We should stop exactly there.
        if depth_braces < 0 or depth_brackets < 0:
            logger.warning(f"Found extra closing brace/bracket at index {i}")
            json_str = json_str[:i]
            # Reset depths for the truncated string (should be 0 now or close to it)
            # Actually, if we cut at '}', depth was -1, so now it is effectively 0 after cut?
            # Let's just break and let the closer handle remaining opens if any (unlikely if we cut on a closer)
            break
            
        valid_len = i + 1

    # If we ended inside a string, close it
    if in_string:
        logger.info("Closing unclosed string")
        json_str += '"'
        in_string = False
    
    # Re-calculate depths on the (potentially truncated/modified) string to be safe
    # This is cheaper than complex tracking logic during the modification above
    depth_braces = 0
    depth_brackets = 0
    in_string = False
    escape = False
    
    for char in json_str:
        if in_string:
            if char == '"' and not escape:
                in_string = False
            elif char == '\\' and not escape:
                escape = True
            else:
                escape = False
        else:
            if char == '"':
                in_string = True
            elif char == '{':
                depth_braces += 1
            elif char == '}':
                depth_braces -= 1
            elif char == '[':
                depth_brackets += 1
            elif char == ']':
                depth_brackets -= 1

    if open_braces := depth_braces:
        if open_braces > 0:
            logger.info(f"Closing {open_braces} braces")
            json_str += '}' * open_braces
            
    if open_brackets := depth_brackets:
        if open_brackets > 0:
            logger.info(f"Closing {open_brackets} brackets")
            json_str += ']' * open_brackets
    
    return json_str


def try_parse_json(json_str):
    """
    Try to parse JSON with multiple recovery strategies
    
    Args:
        json_str (str): JSON string to parse
        
    Returns:
        dict: Parsed JSON or None
    """
    if not json_str:
        return None
    
    # Attempt 1: Direct parse
    try:
        data = json.loads(json_str)
        logger.info("✓ JSON parsed on first attempt")
        return data
    except json.JSONDecodeError as e:
        logger.debug(f"First parse failed at position {e.pos}: {e.msg}")
    
    # Attempt 2: Apply fixes and retry
    try:
        fixed_json = fix_json_string(json_str)
        data = json.loads(fixed_json)
        logger.info("✓ JSON parsed after standard fixes")
        return data
    except json.JSONDecodeError as e:
        logger.debug(f"Parse after fixes failed: {e.msg}")
    
    # Attempt 3: Aggressive recovery
    try:
        recovered_json = aggressive_json_recovery(json_str)
        data = json.loads(recovered_json)
        logger.info("✓ JSON parsed after aggressive recovery")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"All parse attempts failed: {e.msg}")
        logger.error(f"Problematic JSON (first 300 chars): {json_str[:300]}")
        logger.error(f"Problematic JSON (last 300 chars): {json_str[-300:]}")
    
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
        logger.warning("No response text provided")
        return None
    
    logger.debug(f"Processing response: {len(response_text)} chars")
    
    # Step 1: Extract JSON string
    json_str = extract_json_string(response_text)
    
    if not json_str:
        logger.error("Could not extract JSON string from response")
        return None
    
    logger.debug(f"Extracted JSON string: {len(json_str)} chars")
    
    # Step 2: Try to parse
    parsed_json = try_parse_json(json_str)
    
    return parsed_json


def get_default_structure(doc_type="Resume"):
    """Get default structure based on type"""
    
    if doc_type == "Job Description":
        return {
            "jobTitle": "Not extracted",
            "requiredSkills": [],
            "minExperienceYears": 0,
            "requiredEducation": "Not specified",
            "preferredSkills": [],
            "description": None,
            "responsibilities": [],
            "benefits": []
        }
    else:  # Resume
        return {
            "role": "Not extracted",
            "totalYearsExperience": 0,
            "experienceDetails": [],
            "skills": [],
            "education": [],
            "certifications": [],
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
                    val = data['totalYearsExperience']
                    if val is None:
                        data['totalYearsExperience'] = 0
                    else:
                        data['totalYearsExperience'] = int(float(str(val).replace(',', '')))
                except (ValueError, TypeError, AttributeError):
                    data['totalYearsExperience'] = 0
            else:
                data['totalYearsExperience'] = 0
            
            # Ensure domain field exists
            if 'domain' not in data or not data['domain']:
                data['domain'] = "Unknown"
            else:
                data['domain'] = str(data['domain']).strip()
            
            # Ensure skills is a list of dicts with 'name'
            if 'skills' not in data or not isinstance(data['skills'], list):
                data['skills'] = []
            else:
                new_skills = []
                for skill in data['skills']:
                    if isinstance(skill, dict):
                        if 'name' in skill and skill['name']:
                            new_skills.append(skill)
                    elif isinstance(skill, str) and skill.strip():
                        new_skills.append({'name': skill.strip()})
                data['skills'] = new_skills
            
            # Ensure education is a list
            if 'education' not in data or not isinstance(data['education'], list):
                data['education'] = []
            
            # Ensure experienceDetails is a list
            if 'experienceDetails' not in data or not isinstance(data['experienceDetails'], list):
                data['experienceDetails'] = []
            
            logger.debug(f"Resume validated: {len(data['skills'])} skills, {len(data['education'])} education entries, domain: {data.get('domain', 'Unknown')}")
        
        else:  # Job Description
            # Ensure minExperienceYears is a number
            if 'minExperienceYears' not in data or data['minExperienceYears'] is None:
                data['minExperienceYears'] = 0
            else:
                try:
                    data['minExperienceYears'] = int(float(str(data['minExperienceYears']).replace(',', '')))
                except (ValueError, TypeError, AttributeError):
                    data['minExperienceYears'] = 0
            
            # Ensure domain field exists
            if 'domain' not in data or not data['domain']:
                data['domain'] = "Unknown"
            else:
                data['domain'] = str(data['domain']).strip()
            
            # Ensure requiredSkills is a list of strings
            if 'requiredSkills' not in data or not isinstance(data['requiredSkills'], list):
                data['requiredSkills'] = []
            else:
                data['requiredSkills'] = [
                    str(s).strip() for s in data['requiredSkills'] 
                    if s and str(s).strip()
                ]
            
            # Ensure preferredSkills is a list
            if 'preferredSkills' not in data or not isinstance(data['preferredSkills'], list):
                data['preferredSkills'] = []
            else:
                data['preferredSkills'] = [
                    str(s).strip() for s in data['preferredSkills'] 
                    if s and str(s).strip()
                ]
            
            logger.debug(f"JD validated: {data['minExperienceYears']} years experience, {len(data['requiredSkills'])} required skills, domain: {data.get('domain', 'Unknown')}")
    
    except Exception as e:
        logger.error(f"Error in validate_data_types: {e}", exc_info=True)
    
    return data


def parse_with_validation(response_text, doc_type="Resume"):
    """
    Parse JSON with full validation and fallback
    
    Args:
        response_text (str): Raw response from LLM
        doc_type (str): "Resume" or "Job Description"
        
    Returns:
        dict: Valid parsed data or default structure
    """
    
    logger.info(f"Parsing response for {doc_type}")
    
    # Try to clean and parse
    data = clean_json_response(response_text)
    
    if not data:
        logger.warning(f"Failed to parse JSON for {doc_type}, returning defaults")
        return get_default_structure(doc_type)
    
    # Validate structure based on type
    if doc_type == "Job Description":
        required_fields = ['jobTitle', 'requiredSkills', 'minExperienceYears']
    else:  # Resume
        required_fields = ['role', 'totalYearsExperience', 'skills', 'education']
    
    # Check if all required fields exist
    missing_fields = [f for f in required_fields if f not in data or data.get(f) is None]
    
    if missing_fields:
        logger.warning(f"Missing fields: {missing_fields}")
        # Merge with defaults
        defaults = get_default_structure(doc_type)
        defaults.update({k: v for k, v in data.items() if v is not None})
        data = defaults
    
    # Validate data types
    data = validate_data_types(data, doc_type)
    
    logger.info(f"Parsing complete for {doc_type}")
    return data


# ==================== EXPERIENCE CALCULATION ====================

def parse_date_safely(date_str):
    """Parse date from multiple formats safely"""
    
    if not date_str:
        return None
    
    date_str_lower = str(date_str).lower().strip()
    
    present_keywords = ['present', 'current', 'ongoing', 'till now', 'today', 
                       'till present', 'till date', 'current role']
    no_date_keywords = ['no date', 'n/a', 'not available', 'unknown', '--', 'none']
    
    if any(kw in date_str_lower for kw in present_keywords):
        return None
    
    if any(kw in date_str_lower for kw in no_date_keywords):
        return None
    
    date_str = str(date_str).strip()
    
    formats = [
        '%Y', '%Y-%m', '%Y-%m-%d', '%m/%Y', '%m-%Y', '%m/%d/%Y', '%d-%m-%Y',
        '%B %Y', '%b %Y', '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y',
        '%b\'%y', '%B\'%y', '%m.%Y', '%Y.%m',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    if "'" in date_str:
        try:
            cleaned = date_str.replace("'", "")
            return datetime.strptime(cleaned, '%b%y')
        except ValueError:
            pass
    
    logger.warning(f"Could not parse date: {date_str}")
    return None


def calculate_experience_from_details(experience_details):
    """Calculate total years from experience details"""
    
    if not experience_details or not isinstance(experience_details, list):
        return 0, 0
    
    today = datetime.now()
    periods = []
    
    for idx, exp in enumerate(experience_details):
        if not isinstance(exp, dict):
            continue
        
        start_date = parse_date_safely(exp.get('startDate'))
        end_date = parse_date_safely(exp.get('endDate'))
        
        if not start_date:
            continue
        
        if start_date > today:
            continue
        
        if not end_date:
            end_date = today
        
        if end_date < start_date:
            continue
        
        duration_days = (end_date - start_date).days
        
        if duration_days < 30 or duration_days > (60 * 365):
            continue
        
        periods.append({'start': start_date, 'end': end_date})
    
    if not periods:
        return 0, 0
    
    periods.sort(key=lambda x: x['start'])
    merged = [periods[0]]
    
    for current in periods[1:]:
        if current['start'] <= merged[-1]['end']:
            merged[-1]['end'] = max(merged[-1]['end'], current['end'])
        else:
            merged.append(current)
    
    total_days = sum((p['end'] - p['start']).days for p in merged)
    total_years = total_days // 365
    remaining_days = total_days % 365
    total_months = remaining_days // 30
    
    logger.info(f"Experience: {total_years} years {total_months} months")
    return total_years, total_months


# ==================== POST-PROCESSING ====================

def post_process_extraction(data, doc_type="Resume", original_text=""):
    """Fast local post-processing"""
    
    if not data:
        return data
    
    if doc_type == "Resume":
        # Calculate experience from details
        exp_details = data.get('experienceDetails', [])
        if exp_details:
            years, months = calculate_experience_from_details(exp_details)
            data['totalYearsExperience'] = years
            if months > 0:
                data['totalExperienceFormatted'] = f"{years} years {months} months"
        
        # Remove duplicate skills
        skills = data.get('skills', [])
        unique_skills = {}
        for skill in skills:
            if isinstance(skill, dict):
                name = skill.get('name', '').lower().strip()
            else:
                name = str(skill).lower().strip()
            
            if name and 1 < len(name) < 50 and name not in unique_skills:
                unique_skills[name] = {'name': name}
        
        data['skills'] = list(unique_skills.values())[:20]
    
    elif doc_type == "Job Description":
        skills = data.get('requiredSkills', [])
        unique_skills = []
        seen = set()
        for skill in skills:
            skill_lower = str(skill).lower().strip()
            if skill_lower and skill_lower not in seen:
                unique_skills.append(skill)
                seen.add(skill_lower)
        
        data['requiredSkills'] = unique_skills[:25]
    
    return data


def extract_role_from_text(text):
    """Extract job role from resume text"""
    role_patterns = [
        r'(?:Current |Title:?\s*)([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Architect|Lead|Senior|Junior|Analyst|Designer|Admin))',
        r'^([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Architect|Lead))',
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_skills_from_text(text):
    """Extract skills from resume text"""
    known_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust',
        'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'spring',
        'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'cassandra',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
        'html', 'css', 'typescript', 'kotlin', 'swift',
        'tensorflow', 'pytorch', 'pandas', 'numpy',
        'linux', 'bash', 'shell', 'elasticsearch', 'kafka', 'graphql', 'rest',
        'agile', 'scrum', 'jira', 'slack'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in known_skills:
        if re.search(r'\b' + skill + r'\b', text_lower):
            found_skills.append(skill.capitalize())
    
    return found_skills


def extract_job_title_from_text(text):
    """Extract job title from JD text"""
    patterns = [
        r'(?:Job Title|Position|Role)[:\s]+([A-Z][a-zA-Z\s]+)',
        r'(?:Hiring for|Seeking)[:\s]+(?:a\s+)?([A-Z][a-zA-Z\s]+)',
        r'^([A-Z][a-zA-Z\s]*(?:Engineer|Developer|Manager|Analyst|Designer|Architect))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if 2 < len(title) < 100:
                return title
    
    return None