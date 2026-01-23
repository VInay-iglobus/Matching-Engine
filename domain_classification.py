"""
Domain Classification Module
Classifies resumes and job descriptions into relevant domains
and provides domain compatibility scoring
"""

import logging
import json

logger = logging.getLogger(__name__)

# ==================== DOMAIN DEFINITIONS ====================

DOMAIN_CATEGORIES = {
    "IT/Software": {
        "description": "Information Technology and Software Development",
        "keywords": ["software", "developer", "engineer", "programming", "code", "it", "technology", "web", "app", "mobile"],
    },
    "Backend Development": {
        "description": "Server-side and API development",
        "keywords": ["backend", "server", "api", "django", "fastapi", "nodejs", "express", "spring", "microservices"],
    },
    "Frontend Development": {
        "description": "Client-side and UI development",
        "keywords": ["frontend", "ui", "ux", "react", "angular", "vue", "html", "css", "javascript", "web development"],
    },
    "AI/ML/Data Science": {
        "description": "Machine Learning, AI, and Data Science",
        "keywords": ["ai", "ml", "machine learning", "deep learning", "neural", "tensorflow", "pytorch", "data science", "nlp", "computer vision", "algorithm"],
    },
    "DevOps/Cloud": {
        "description": "DevOps, Cloud Infrastructure, and System Administration",
        "keywords": ["devops", "cloud", "aws", "azure", "gcp", "kubernetes", "docker", "ci/cd", "jenkins", "terraform", "infrastructure"],
    },
    "QA/Testing": {
        "description": "Quality Assurance and Software Testing",
        "keywords": ["qa", "test", "testing", "automation", "selenium", "pytest", "manual testing", "quality assurance"],
    },
    "Finance/Accounting": {
        "description": "Finance, Accounting, and Financial Services",
        "keywords": ["finance", "accounting", "gaap", "ledger", "audit", "cpa", "financial", "accountant", "bookkeeping", "tax"],
    },
    "Healthcare": {
        "description": "Healthcare and Medical Services",
        "keywords": ["healthcare", "medical", "nurse", "doctor", "physician", "hospital", "clinical", "pharmaceutical", "health"],
    },
    "Sales/Marketing": {
        "description": "Sales and Marketing",
        "keywords": ["sales", "marketing", "marketing", "business development", "account executive", "campaign", "seo", "digital marketing"],
    },
    "HR/Recruitment": {
        "description": "Human Resources and Recruitment",
        "keywords": ["hr", "human resources", "recruitment", "hiring", "talent", "employee", "payroll"],
    },
    "Finance/Banking": {
        "description": "Banking and Financial Services",
        "keywords": ["banking", "bank", "loan", "credit", "mortgage", "trading", "investment", "portfolio"],
    },
}

# ==================== DOMAIN COMPATIBILITY MATRIX ====================
# Scores from 0-100 indicating how well experience from one domain transfers to another

DOMAIN_COMPATIBILITY_MATRIX = {
    "IT/Software": {
        "IT/Software": 100,
        "Backend Development": 95,
        "Frontend Development": 90,
        "AI/ML/Data Science": 75,
        "DevOps/Cloud": 85,
        "QA/Testing": 80,
        "Finance/Accounting": 20,
        "Healthcare": 15,
        "Sales/Marketing": 10,
        "HR/Recruitment": 10,
        "Finance/Banking": 15,
    },
    "Backend Development": {
        "IT/Software": 95,
        "Backend Development": 100,
        "Frontend Development": 60,
        "AI/ML/Data Science": 80,
        "DevOps/Cloud": 85,
        "QA/Testing": 75,
        "Finance/Accounting": 20,
        "Healthcare": 15,
        "Sales/Marketing": 10,
        "HR/Recruitment": 10,
        "Finance/Banking": 20,
    },
    "Frontend Development": {
        "IT/Software": 90,
        "Backend Development": 60,
        "Frontend Development": 100,
        "AI/ML/Data Science": 40,
        "DevOps/Cloud": 50,
        "QA/Testing": 70,
        "Finance/Accounting": 10,
        "Healthcare": 10,
        "Sales/Marketing": 15,
        "HR/Recruitment": 10,
        "Finance/Banking": 10,
    },
    "AI/ML/Data Science": {
        "IT/Software": 75,
        "Backend Development": 80,
        "Frontend Development": 40,
        "AI/ML/Data Science": 100,
        "DevOps/Cloud": 60,
        "QA/Testing": 50,
        "Finance/Accounting": 45,
        "Healthcare": 50,
        "Sales/Marketing": 20,
        "HR/Recruitment": 10,
        "Finance/Banking": 50,
    },
    "DevOps/Cloud": {
        "IT/Software": 85,
        "Backend Development": 85,
        "Frontend Development": 50,
        "AI/ML/Data Science": 60,
        "DevOps/Cloud": 100,
        "QA/Testing": 70,
        "Finance/Accounting": 25,
        "Healthcare": 20,
        "Sales/Marketing": 10,
        "HR/Recruitment": 10,
        "Finance/Banking": 25,
    },
    "QA/Testing": {
        "IT/Software": 80,
        "Backend Development": 75,
        "Frontend Development": 70,
        "AI/ML/Data Science": 50,
        "DevOps/Cloud": 70,
        "QA/Testing": 100,
        "Finance/Accounting": 20,
        "Healthcare": 20,
        "Sales/Marketing": 15,
        "HR/Recruitment": 10,
        "Finance/Banking": 20,
    },
    "Finance/Accounting": {
        "IT/Software": 20,
        "Backend Development": 20,
        "Frontend Development": 10,
        "AI/ML/Data Science": 45,
        "DevOps/Cloud": 25,
        "QA/Testing": 20,
        "Finance/Accounting": 100,
        "Healthcare": 30,
        "Sales/Marketing": 50,
        "HR/Recruitment": 40,
        "Finance/Banking": 85,
    },
    "Healthcare": {
        "IT/Software": 15,
        "Backend Development": 15,
        "Frontend Development": 10,
        "AI/ML/Data Science": 50,
        "DevOps/Cloud": 20,
        "QA/Testing": 20,
        "Finance/Accounting": 30,
        "Healthcare": 100,
        "Sales/Marketing": 25,
        "HR/Recruitment": 20,
        "Finance/Banking": 25,
    },
    "Sales/Marketing": {
        "IT/Software": 10,
        "Backend Development": 10,
        "Frontend Development": 15,
        "AI/ML/Data Science": 20,
        "DevOps/Cloud": 10,
        "QA/Testing": 15,
        "Finance/Accounting": 50,
        "Healthcare": 25,
        "Sales/Marketing": 100,
        "HR/Recruitment": 70,
        "Finance/Banking": 60,
    },
    "HR/Recruitment": {
        "IT/Software": 10,
        "Backend Development": 10,
        "Frontend Development": 10,
        "AI/ML/Data Science": 10,
        "DevOps/Cloud": 10,
        "QA/Testing": 10,
        "Finance/Accounting": 40,
        "Healthcare": 20,
        "Sales/Marketing": 70,
        "HR/Recruitment": 100,
        "Finance/Banking": 40,
    },
    "Finance/Banking": {
        "IT/Software": 15,
        "Backend Development": 20,
        "Frontend Development": 10,
        "AI/ML/Data Science": 50,
        "DevOps/Cloud": 25,
        "QA/Testing": 20,
        "Finance/Accounting": 85,
        "Healthcare": 25,
        "Sales/Marketing": 60,
        "HR/Recruitment": 40,
        "Finance/Banking": 100,
    },
}

# ==================== DOMAIN DETECTION ====================

def get_domain_compatibility(resume_domain, jd_domain):
    """
    Get compatibility score between resume domain and JD domain
    
    Args:
        resume_domain (str): Domain from resume
        jd_domain (str): Domain from JD
        
    Returns:
        dict: {
            "score": 0-100,
            "percentage": 0-100,
            "level": "Perfect" | "Good" | "Acceptable" | "Poor",
            "resume_domain": resume_domain,
            "jd_domain": jd_domain,
            "details": explanation string
        }
    """
    if not resume_domain or not jd_domain:
        return {
            "score": 0,
            "percentage": 0,
            "level": "Unknown",
            "resume_domain": resume_domain,
            "jd_domain": jd_domain,
            "details": "Could not determine domain(s)"
        }
    
    # Get compatibility score from matrix
    score = DOMAIN_COMPATIBILITY_MATRIX.get(resume_domain, {}).get(jd_domain, 0)
    
    # Determine level
    if score >= 85:
        level = "Perfect"
    elif score >= 60:
        level = "Good"
    elif score >= 35:
        level = "Acceptable"
    else:
        level = "Poor"
    
    # Generate details
    if resume_domain == jd_domain:
        details = f"Both from same domain ({resume_domain}). Excellent match! ✓"
    elif level == "Perfect":
        details = f"Strong domain alignment: {resume_domain} → {jd_domain}"
    elif level == "Good":
        details = f"Reasonable domain alignment: {resume_domain} → {jd_domain}. Some skills are transferable."
    elif level == "Acceptable":
        details = f"Moderate domain shift: {resume_domain} → {jd_domain}. Candidate may need upskilling."
    else:
        details = f"Significant domain change: {resume_domain} → {jd_domain}. Major career pivot required."
    
    return {
        "score": score,
        "percentage": score,
        "level": level,
        "resume_domain": resume_domain,
        "jd_domain": jd_domain,
        "details": details
    }


def extract_keywords(text):
    """Extract keywords from text for domain detection"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_keywords = []
    
    for domain, domain_info in DOMAIN_CATEGORIES.items():
        keywords = domain_info.get("keywords", [])
        count = 0
        for keyword in keywords:
            if keyword in text_lower:
                count += text_lower.count(keyword)
        
        if count > 0:
            found_keywords.append({
                "domain": domain,
                "keyword_count": count,
                "score": count  # Weight by frequency
            })
    
    # Sort by score (descending)
    found_keywords.sort(key=lambda x: x["score"], reverse=True)
    return found_keywords


def detect_domain_from_text(text, doc_type="Resume"):
    """
    Detect primary domain from text using keyword analysis
    
    Args:
        text (str): Document text
        doc_type (str): "Resume" or "Job Description"
        
    Returns:
        dict: {
            "primary_domain": "domain name",
            "confidence": 0-100,
            "detected_domains": [list of all detected domains with scores],
            "keywords_found": [list of keywords found]
        }
    """
    if not text:
        return {
            "primary_domain": "Unknown",
            "confidence": 0,
            "detected_domains": [],
            "keywords_found": []
        }
    
    keywords_found = extract_keywords(text)
    
    if not keywords_found:
        return {
            "primary_domain": "Unknown",
            "confidence": 0,
            "detected_domains": [],
            "keywords_found": []
        }
    
    # Primary domain is the one with highest keyword count
    primary = keywords_found[0]
    
    # Calculate confidence (0-100)
    # More keywords and higher concentration = higher confidence
    total_keywords = sum(k["score"] for k in keywords_found)
    confidence = min(100, (primary["score"] / total_keywords) * 100) if total_keywords > 0 else 0
    
    return {
        "primary_domain": primary["domain"],
        "confidence": int(confidence),
        "detected_domains": [
            {
                "domain": k["domain"],
                "keyword_count": k["keyword_count"],
                "score": k["score"]
            }
            for k in keywords_found[:3]  # Top 3
        ],
        "keywords_found": keywords_found
    }


def classify_domain_with_llm(text, doc_type="Resume"):
    """
    Classify domain using LLM (via Ollama) for more accurate classification
    Falls back to keyword-based detection if LLM fails
    
    Args:
        text (str): Document text
        doc_type (str): "Resume" or "Job Description"
        
    Returns:
        dict: Domain classification result
    """
    from llm_extraction import call_ollama, validate_json_response
    
    if not text:
        return {
            "primary_domain": "Unknown",
            "confidence": 0,
            "method": "none",
            "details": "No text provided"
        }
    
    # Create classification prompt
    classification_prompt = f"""TASK: Classify the domain/field of this {doc_type}. Return ONLY a JSON object.

{doc_type.upper()}:
{text[:2000]}

Return ONLY this JSON (no other text):
{{
  "primary_domain": "one of: IT/Software, Backend Development, Frontend Development, AI/ML/Data Science, DevOps/Cloud, QA/Testing, Finance/Accounting, Healthcare, Sales/Marketing, HR/Recruitment, Finance/Banking, or Unknown",
  "confidence": (confidence 0-100 as INTEGER),
  "reasoning": "brief explanation",
  "related_domains": ["domain2", "domain3"]
}}

RULES:
1. Choose the MOST RELEVANT primary domain
2. Confidence is how sure you are (80-100 = very sure, 50-79 = moderately sure, <50 = not sure)
3. Return valid JSON only
4. If unclear, set to "Unknown" with low confidence
"""
    
    try:
        logger.info(f"🤖 Classifying {doc_type} domain with LLM...")
        
        response = call_ollama(
            classification_prompt,
            max_retries=2,
            validate_func=validate_json_response
        )
        
        if response:
            # Extract JSON
            start = response.find('{')
            end = response.rfind('}')
            
            if start != -1 and end != -1:
                json_str = response[start:end + 1]
                try:
                    result = json.loads(json_str)
                    result["method"] = "llm"
                    logger.info(f"✅ LLM domain classification: {result['primary_domain']} ({result['confidence']}%)")
                    return result
                except:
                    logger.warning("Failed to parse LLM response, falling back to keyword detection")
    
    except Exception as e:
        logger.warning(f"LLM classification error: {e}, falling back to keyword detection")
    
    # Fallback to keyword-based detection
    keyword_result = detect_domain_from_text(text, doc_type)
    keyword_result["method"] = "keyword"
    
    logger.info(f"📊 Keyword-based domain classification: {keyword_result['primary_domain']} ({keyword_result['confidence']}%)")
    return keyword_result


def calculate_domain_adjustment_factor(domain_compatibility_score):
    """
    Calculate how much to adjust matching scores based on domain compatibility
    
    Args:
        domain_compatibility_score (int): 0-100
        
    Returns:
        float: Adjustment multiplier (0.1 to 1.0)
        
    Examples:
        95 compatibility → 1.0 (no adjustment)
        70 compatibility → 0.85 (15% penalty)
        50 compatibility → 0.65 (35% penalty)
        20 compatibility → 0.25 (75% penalty)
    """
    if domain_compatibility_score >= 85:
        return 1.0  # No adjustment
    elif domain_compatibility_score >= 70:
        return 0.90  # 10% penalty
    elif domain_compatibility_score >= 60:
        return 0.80  # 20% penalty
    elif domain_compatibility_score >= 50:
        return 0.65  # 35% penalty
    elif domain_compatibility_score >= 35:
        return 0.45  # 55% penalty
    else:
        return 0.25  # 75% penalty


# ==================== HELPER FUNCTIONS ====================

def get_domain_description(domain_name):
    """Get description of a domain"""
    domain_info = DOMAIN_CATEGORIES.get(domain_name, {})
    return domain_info.get("description", "Unknown domain")


def list_all_domains():
    """List all available domains"""
    return list(DOMAIN_CATEGORIES.keys())
