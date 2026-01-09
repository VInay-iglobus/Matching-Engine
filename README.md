# 🎯 AI-Powered Resume-JD Matching Engine

A local, privacy-first resume and job description matching application that uses **Llama 3.2** for intelligent data extraction and **local matching logic** for accurate candidate-job fit analysis.

## ✨ Features

### 🤖 Intelligent Data Extraction
- **Multi-format support**: PDF, DOCX, TXT files
- **Structured extraction** using Llama 3.2:
  - Resume: Role, experience, skills, education, certifications, achievements
  - Job Description: Title, required skills, experience, education, responsibilities
- **Automatic JSON formatting** for easy processing

### 🔍 Smart Matching Algorithm
- **Local matching** - No external API calls for matching
- **Three-tier evaluation**:
  1. **Experience Matching** (35% weight) - Compares years of experience
  2. **Skills Matching** (40% weight) - Calculates skill overlap percentage
  3. **Education Matching** (25% weight) - Validates education hierarchy
- **Transparent scoring**: See exactly why each score was given

### 📊 Detailed Results
- **Overall Match Score** (0-100)
- **Color-coded assessment** (Excellent/Good/Needs Review)
- **Criteria analysis** with pass/fail for each criterion
- **Skill gap identification** - See exactly what's missing
- **Smart recommendations** - Get specific improvement suggestions
- **Downloadable results** as JSON for record-keeping

### 🔐 Privacy First
- All processing runs **locally** on your machine
- No data sent to external servers
- Uses local Ollama instance for extraction
- Fully customizable and transparent

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) installed and running with `llama3.2` model

### Installation

1. **Clone or download the project**
```bash
cd resume-jd-matcher
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Ollama**
```bash
ollama serve
# In another terminal, pull the model if needed:
ollama pull llama3.2
```

5. **Run the application**
```bash
streamlit run Matching.py
```

6. **Open in browser**
```
http://localhost:8501
```

---

## 📁 Project Structure

```
resume-jd-matcher/
├── Matching.py              # Main application orchestrator
├── matching_logic.py       # Matching & scoring logic
├── ui_components.py         # Streamlit UI display components
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### File Descriptions

#### `Matching.py` (Main Application)
- **Responsibilities**: Application flow, file processing, data extraction
- **Key Functions**:
  - `process_file()` - Extract text from PDF/DOCX/TXT
  - `call_llama()` - Call Llama API with retry logic
  - `extract_structured_data()` - Extract resume/JD data using Llama
  - `main()` - Application entry point

#### `matching_logic.py` (Business Logic)
- **Responsibilities**: Matching algorithm, scoring, validation
- **Key Functions**:
  - `calculate_match()` - Compare resume vs JD (LOCAL, NO API CALLS)
  - `check_experience_match()` - Validate years of experience
  - `check_education_match()` - Validate education level
  - `check_skills_match()` - Calculate skill overlap
  - `calculate_gaps()` - Identify missing skills/requirements
  - `calculate_recommendations()` - Generate improvement suggestions

#### `ui_components.py` (User Interface)
- **Responsibilities**: All Streamlit UI display logic
- **Key Functions**:
  - `setup_page_config()` - Configure page settings
  - `display_header()` - Show page title
  - `display_upload_section()` - File upload UI
  - `display_results()` - Show complete results
  - Message functions - `show_error_message()`, `show_success_message()`, etc.

---

## 📊 Scoring System

### Weights & Points

| Criterion | Max Points | Weight | Met = | Not Met = |
|-----------|-----------|--------|-------|-----------|
| Skills Match | 40 | 40% | Proportional (40 × matched/required) | 0 |
| Experience Match | 35 | 35% | 35 | 0 |
| Education Match | 25 | 25% | 25 | 0 |
| **Total** | **100** | **100%** | - | - |

### Assessment Levels

| Score | Assessment | Color |
|-------|-----------|-------|
| 70-100 | Excellent Match | 🟢 |
| 50-69 | Good Match | 🟡 |
| 0-49 | Needs Review | 🔴 |

### Matching Logic

**Experience Matching:**
```
If candidate_years >= required_years → MET (35 points)
If candidate_years < required_years → NOT MET (0 points)
```

**Education Matching:**
```
Education hierarchy: High School < Bachelor < Master < PhD
If candidate_level >= required_level → MET (25 points)
Otherwise → NOT MET (0 points)
```

**Skills Matching:**
```
Percentage = (matched_skills / required_skills) × 100
If percentage >= 50% → MET (score = 40 × percentage/100)
If percentage < 50% → NOT MET (0 points)
```

---

## 🎯 How It Works

### Step 1: Upload Documents
- Resume (PDF, DOCX, or TXT)
- Job Description (PDF, DOCX, or TXT)
- Or paste text directly

### Step 2: Extract Data
- **Llama 3.2** analyzes documents
- Extracts structured JSON data:
  - **Resume**: Role, experience, skills, education, certifications
  - **Job Description**: Title, required skills, experience, education

### Step 3: Local Matching
- **NO additional API calls** - Uses extracted JSON directly
- Compares resume vs JD requirements
- Calculates scores based on matching rules
- Identifies gaps and generates recommendations

### Step 4: View Results
- **Overall Score** with color-coded assessment
- **Criteria Analysis** showing what matched/didn't match
- **Skill Gaps** identifying what's missing
- **Recommendations** for improvement
- **Extracted Data** as JSON for verification
- **Download** results as JSON

---

## 🔧 Configuration

### Ollama Settings
Edit in `Matching.py`:
```python
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"
```

### Scoring Weights
Edit in `matching_logic.py`:
```python
SCORING_CONFIG = {
    "skillsMatch": {"maxPoints": 40, "weight": "40%"},
    "experienceMatch": {"maxPoints": 35, "weight": "35%"},
    "educationMatch": {"maxPoints": 25, "weight": "25%"}
}
```

### Assessment Thresholds
Edit in `matching_logic.py`:
```python
ASSESSMENT_THRESHOLDS = {
    70: {"color": "🟢", "text": "Excellent Match"},
    50: {"color": "🟡", "text": "Good Match"},
    0: {"color": "🔴", "text": "Needs Review"}
}
```

---

## 🔌 Requirements

### System Requirements
- Python 3.8 or higher
- Ollama with llama3.2 model
- 4GB RAM minimum
- 2GB disk space

### Python Dependencies
```
streamlit>=1.28.0
pdfplumber>=0.10.0
python-docx>=0.8.11
requests>=2.31.0
```

### Install All Dependencies
```bash
pip install -r requirements.txt
```

---

## 📝 Usage Examples

### Example 1: Perfect Match
**Resume**: 8 years experience, Master's degree, 12 skills
**Job Description**: 5 years required, Bachelor's degree, 10 required skills

**Result**:
- Experience Match: ✅ MET → 35 points
- Education Match: ✅ MET → 25 points
- Skills Match: ✅ MET → 40 points
- **Overall Score: 100 🟢 Excellent Match**

### Example 2: Good Match
**Resume**: 5 years experience, Bachelor's degree, 8/10 skills
**Job Description**: 5 years required, Bachelor's degree, 10 required skills

**Result**:
- Experience Match: ✅ MET → 35 points
- Education Match: ✅ MET → 25 points
- Skills Match: ✅ MET → 32 points (80% of skills)
- **Overall Score: 92 🟢 Excellent Match**

### Example 3: Partial Match
**Resume**: 2 years experience, Bachelor's degree, 5/10 skills
**Job Description**: 5 years required, Bachelor's degree, 10 required skills

**Result**:
- Experience Match: ❌ NOT MET → 0 points
- Education Match: ✅ MET → 25 points
- Skills Match: ❌ NOT MET → 0 points
- **Overall Score: 25 🔴 Needs Review**

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to Ollama"
**Solution**: 
1. Ensure Ollama is running: `ollama serve`
2. Verify model is installed: `ollama list`
3. Check URL is correct: `http://localhost:11434`

### Issue: "Request timed out"
**Solution**:
1. Increase timeout in `Matching.py`:
```python
timeout=600  # Increase from 300
```
2. Reduce document size
3. Check system resources (RAM, CPU)

### Issue: "Error parsing JSON"
**Solution**:
1. Check document formatting
2. Use plain text for better extraction
3. Remove special characters from resume/JD

### Issue: "Low matching score despite good match"
**Solution**:
1. Check extracted data in "Extracted Structured Data" tabs
2. Verify skill names match exactly (case-insensitive matching)
3. Ensure education field is recognized
4. Check experience years are numbers

---

## 📈 Advanced Usage

### Batch Processing Multiple Resumes
Create a script to process multiple resumes:

```python
from matching_logic import calculate_match
from Matching import extract_structured_data, process_file

# Process multiple resumes against one JD
jd_data = extract_structured_data("job_description.txt", "Job Description")

resumes = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
results = []

for resume_file in resumes:
    resume_text = process_file(resume_file)
    resume_data = extract_structured_data(resume_text, "Resume")
    match = calculate_match(resume_data, jd_data)
    results.append({
        "file": resume_file,
        "score": match["overallScore"],
        "assessment": match["assessment"]
    })

# Sort by score
results.sort(key=lambda x: x["score"], reverse=True)
```

### Custom Scoring
Modify weights in `matching_logic.py`:

```python
SCORING_CONFIG = {
    "skillsMatch": {"maxPoints": 50, "weight": "50%"},      # More important
    "experienceMatch": {"maxPoints": 30, "weight": "30%"},  # Medium
    "educationMatch": {"maxPoints": 20, "weight": "20%"}    # Less important
}
```

---

## 🔐 Privacy & Security

✅ **All processing is local**
- No data sent to external servers
- Ollama runs on your machine
- No cloud dependencies

✅ **No API keys needed**
- No authentication required
- Works offline (after model download)

✅ **Transparent matching logic**
- Source code is open and readable
- You can audit the matching algorithm
- Full control over scoring rules

---

## 📄 Data Format

### Extracted Resume JSON
```json
{
  "role": "Senior Python Developer",
  "totalYearsExperience": 8,
  "skills": [
    {"name": "Python", "proficiency": "expert"},
    {"name": "Django", "proficiency": "expert"},
    {"name": "PostgreSQL", "proficiency": "advanced"}
  ],
  "education": [
    {
      "degree": "Master",
      "field": "Computer Science",
      "institution": "MIT",
      "year": "2018"
    }
  ],
  "certifications": [
    {"name": "AWS Solutions Architect", "issuer": "AWS", "year": "2020"}
  ]
}
```

### Extracted JD JSON
```json
{
  "jobTitle": "Senior Python Developer",
  "minExperienceYears": 5,
  "requiredEducation": "Bachelor",
  "requiredSkills": ["Python", "Django", "PostgreSQL", "AWS"],
  "preferredSkills": ["Kubernetes", "Docker"],
  "responsibilities": [
    "Develop scalable backend services",
    "Lead technical design reviews"
  ]
}
```

### Matching Results JSON
```json
{
  "overallScore": 92,
  "assessment": {"color": "🟢", "text": "Excellent Match"},
  "criteriaAnalysis": {
    "experienceMatch": {
      "met": true,
      "candidateExperience": 8,
      "requiredExperience": 5,
      "details": "✅ Candidate has 8 years experience..."
    },
    "skillsMatch": {
      "met": true,
      "percentage": 100,
      "matchedSkills": ["Python", "Django", "PostgreSQL", "AWS"],
      "missingSkills": []
    }
  },
  "gaps": [],
  "recommendations": ["Excellent candidate for interview"],
  "summary": "Strong candidate with excellent match..."
}
```

---

## 🤝 Contributing

To customize or extend this project:

1. **Modify scoring**: Edit `matching_logic.py` `SCORING_CONFIG`
2. **Change UI**: Edit `ui_components.py` for layout/display
3. **Add new extraction fields**: Edit extraction prompts in `Matching.py`
4. **Adjust matching logic**: Edit `check_*_match()` functions

---

## 📞 Support

### Common Questions

**Q: Can I use a different Ollama model?**
A: Yes! Change `OLLAMA_MODEL` in `Matching.py` to any installed model.

**Q: How accurate is the matching?**
A: Accuracy depends on data quality. Well-formatted resumes/JDs extract better. Matching logic is deterministic and transparent.

**Q: Can I modify the scoring weights?**
A: Yes! Edit `SCORING_CONFIG` in `matching_logic.py`.

**Q: Does it work offline?**
A: Yes, once Ollama and models are downloaded. No internet required after setup.

---

## 📜 License

This project is provided as-is for educational and commercial use.

---

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Llama 2 Model Card](https://huggingface.co/meta-llama/Llama-2-7b)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)

---

## 🚀 Future Enhancements

- [ ] Batch resume processing
- [ ] Database storage for results
- [ ] Custom resume templates
- [ ] Industry-specific scoring weights
- [ ] Resume improvement suggestions
- [ ] API endpoint for integration
- [ ] User accounts and history
- [ ] Resume comparison tool
- [ ] Interview prep generator
- [ ] Salary estimation based on match score

---

## 💡 Tips for Best Results

1. **Use well-formatted documents** - Clean PDFs extract better
2. **Be specific in requirements** - Detailed JD = better matching
3. **Include all relevant details** - More skills/experience = accurate scoring
4. **Use standard terminology** - "Python" not "py", "Docker" not "containers"
5. **Check extracted data** - Verify extraction before assessing match
6. **Download results** - Keep JSON records of matches

---

## 🎯 Version History

### v1.0 (Current)
- ✅ Local matching engine (no LLM calls for matching)
- ✅ Three-tier evaluation system
- ✅ Multi-format file support
- ✅ Downloadable JSON results
- ✅ Smart recommendations

---

**Happy Matching! 🚀**