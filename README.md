# 📄 Resume-JD Matcher

**Resume-JD Matcher** is a sophisticated AI-powered resume screening platform that automates candidate evaluation through intelligent matching algorithms. The system combines LLM-based data extraction (Hugging Face Llama 3.2), multi-criteria scoring, domain classification, and extensive skill analogy mapping to provide accurate, explainable matching results.

---

## 🌟 Key Features

- **AI-Powered Extraction**: Automatically extracts structured data from PDF, DOCX, and TXT files using Hugging Face Llama 3.2.
- **Intelligent Matching**: Multi-criteria scoring based on Experience, Education, and Skills.
- **Skill Recognition**: Comprehensive mapping of 500+ skills across 12 technology families, including fuzzy matching and analogy mapping.
- **Domain Awareness**: Industry-specific domain classification and compatibility checks to prevent cross-domain false matches.
- **Batch Processing**: Capability to process 100+ resumes simultaneously with real-time progress tracking and CSV export.
- **Interactive Dashboard**: Match history, analytics, and stats for data-driven recruitment.
- **Customizable Weights**: Adjust scoring criteria importance (Experience vs. Education vs. Skills) to suit specific hiring needs.

---

## 🏗️ Architecture

The project follows a modular, full-stack architecture:

- **Frontend**: Single-page application built with Vanilla JS, HTML5, and CSS3. Uses `PDF.js` and `Mammoth.js` for client-side file parsing.
- **Backend**: FastAPI (Python) server handling authentication, routing, and orchestration.
- **AI Layer**: Hugging Face Inference API (Llama 3.2) for structured data extraction.
- **Database**: SQLite for persistent storage of users, match history, and analytics.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, SQLite
- **AI Engine**: Hugging Face Llama 3.2 (via Inference Client)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Libraries**: 
  - `huggingface-hub`: LLM Interaction
  - `pdfplumber`: Server-side PDF parsing
  - `python-docx`: DOCX parsing
  - `mammoth.js` & `pdf.js`: Client-side parsing

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Hugging Face API Token

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Resume-JD-Matcher
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
HUGGINGFACE_API_KEY=hf_YourActualTokenHere
HUGGINGFACE_MODEL=meta-llama/Llama-3.2-3B-Instruct
SECRET_KEY=your-secret-key-for-jwt
```

### 5. Hugging Face Setup
1. Get your token from [Hugging Face Settings](https://huggingface.co/settings/tokens).
2. **Important**: Accept the Llama 3.2 license at [meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct).

---

## 🏃 Running the Application

Start the FastAPI server:
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```
Access the UI at `http://localhost:8001`

---

## 📂 Project Structure

- `main.py`: Entry point for the FastAPI application.
- `llm_extraction.py`: Handles interaction with Hugging Face for data extraction.
- `matching_engine.py`: Core matching and scoring algorithms.
- `database.py`: SQLite database management.
- `skills_analogy.py`: Skill mapping and fuzzy matching logic.
- `domain_classification.py`: Industry domain detection and compatibility scoring.
- `static/`: Frontend application files (HTML, CSS, JS).

---

## 📝 License

This project is licensed under the MIT License.
