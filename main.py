"""
FastAPI Backend for Resume-JD Matcher - FIXED TOKEN ISSUE
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import jwt
import os
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import requests
from dotenv import load_dotenv

# ==================== FIXED IMPORTS ====================
from llm_extraction import extract_structured_data_stable
from matching_engine import calculate_match
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ==================== FIXED CONFIGURATION ====================
# Use environment variable or fixed fallback
SECRET_KEY = os.getenv("SECRET_KEY") or "resume-matcher-secret-key-2024-fixed"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = None
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logger.info(f"🔐 Using SECRET_KEY: {SECRET_KEY[:30]}...")
logger.info(f"🔐 From environment: {'YES' if os.getenv('SECRET_KEY') else 'NO (using fallback)'}")

# ==================== MODELS ====================

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

class SingleMatchRequest(BaseModel):
    resume_text: str
    jd_text: str
    weights: Optional[Dict[str, int]] = None

# ==================== AUTHENTICATION ====================

class AuthManager:
    """Handle authentication and JWT tokens"""
    
    def __init__(self):
        self.users_db = {}
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r") as f:
                    self.users_db = json.load(f)
                    logger.info(f"✅ Loaded {len(self.users_db)} users from users.json")
            except Exception as e:
                logger.warning(f"Could not load users.json: {e}")
                self.users_db = {}
        else:
            # Create default test user
            self.users_db = {
                "test@test.com": {
                    "name": "Test User",
                    "password": self.hash_password("test123"),
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            self.save_users()
            logger.info("✅ Created default test user: test@test.com / test123")
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open("users.json", "w") as f:
                json.dump(self.users_db, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password"""
        return self.hash_password(password) == hashed
    
    def create_access_token(self, email: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token - FIXED to use consistent SECRET_KEY"""
        to_encode = {"email": email}
        
        if ACCESS_TOKEN_EXPIRE_MINUTES is not None:
            if expires_delta is None:
                expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            expire = datetime.utcnow() + expires_delta
            to_encode["exp"] = expire
        
        # FIXED: Use the constant SECRET_KEY
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ Token created for {email}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return email - FIXED"""
        try:
            logger.info(f"🔐 Verifying token: {token[:30]}...")
            # FIXED: Use the constant SECRET_KEY
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("email")
            logger.info(f"✅ Token verified for: {email}")
            return email
        except jwt.ExpiredSignatureError:
            logger.warning("⏰ Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Token verification error: {e}")
            return None
    
    def register_user(self, name: str, email: str, password: str) -> tuple:
        """Register new user"""
        if email in self.users_db:
            return False, "Email already registered"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        self.users_db[email] = {
            "name": name,
            "password": self.hash_password(password),
            "created_at": datetime.utcnow().isoformat()
        }
        self.save_users()
        logger.info(f"✅ New user registered: {email}")
        return True, "Registration successful"
    
    def login_user(self, email: str, password: str) -> tuple:
        """Authenticate user"""
        if email not in self.users_db:
            logger.warning(f"⚠️ Login attempt with non-existent email: {email}")
            return False, None, "Invalid email or password"
        
        user = self.users_db[email]
        if not self.verify_password(password, user["password"]):
            logger.warning(f"⚠️ Failed login attempt for: {email}")
            return False, None, "Invalid email or password"
        
        token = self.create_access_token(email)
        logger.info(f"✅ User logged in: {email}")
        return True, token, "Login successful"

# ==================== INITIALIZATION ====================

app = FastAPI(title="Resume-JD Matcher API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_manager = AuthManager()
db_manager = None

try:
    db_manager = DatabaseManager()
    logger.info("✅ Database initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ Database initialization error: {e}")

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db_manager else "disconnected",
        "secret_key_set": bool(SECRET_KEY)
    }

@app.get("/api/health/ollama")
async def check_ollama_health():
    """Check if Ollama is running"""
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5,
            verify=False
        )
        
        if response.status_code == 200:
            models = response.json()
            return {
                "status": "healthy",
                "ollama_running": True,
                "models_available": len(models.get('models', [])),
                "models": [m['name'] for m in models.get('models', [])]
            }
        else:
            return {
                "status": "unhealthy",
                "ollama_running": False,
                "error": f"HTTP {response.status_code}"
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "status": "offline",
            "ollama_running": False,
            "error": "Cannot connect to Ollama at http://localhost:11434",
            "fix": "Run: ollama serve"
        }
    except Exception as e:
        return {
            "status": "error",
            "ollama_running": False,
            "error": str(e)
        }

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register new user"""
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    success, message = auth_manager.register_user(
        request.name, request.email, request.password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message, "status": "success"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return token"""
    success, token, message = auth_manager.login_user(request.email, request.password)
    
    if not success:
        raise HTTPException(status_code=401, detail=message)
    
    user_data = auth_manager.users_db[request.email]
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": request.email,
            "name": user_data["name"],
            "created_at": user_data["created_at"]
        }
    }

@app.get("/api/auth/verify")
async def verify_token(token: str = Query(...)):
    """Verify token validity"""
    logger.info(f"🔐 Verifying token: {token[:30]}...")
    email = auth_manager.verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_data = auth_manager.users_db.get(email, {})
    return {
        "valid": True,
        "user": {
            "email": email,
            "name": user_data.get("name", "Unknown")
        }
    }

# ==================== MATCHING ENDPOINTS ====================

@app.post("/api/match/single")
async def single_match(token: str = Query(...), request: SingleMatchRequest = None):
    """Process single resume-JD match"""
    logger.info(f"🔍 Match endpoint called with token: {token[:30]}...")
    
    # Verify token - FIXED
    email = auth_manager.verify_token(token)
    if not email:
        logger.error("❌ Invalid token provided")
        raise HTTPException(status_code=401, detail="Unauthorized - Invalid token")
    
    logger.info(f"✅ Token verified for user: {email}")
    
    if not request or not request.resume_text or not request.jd_text:
        raise HTTPException(status_code=400, detail="Resume and JD text required")
    
    try:
        logger.info(f"📋 Processing single match for user: {email}")
        custom_weights = request.weights 
        if request.weights:
            logger.info(f"   Using custom weights: {custom_weights}")
        else:
            logger.info("   Using default weights")
        
        # Extract resume
        logger.info("📄 Extracting resume...")
        resume_data = extract_structured_data_stable(request.resume_text, "Resume")
        
        if not resume_data:
            logger.error("❌ Failed to extract resume")
            raise HTTPException(status_code=400, detail="Failed to extract resume")
        
        logger.info(f"✅ Resume extracted successfully")
        logger.info(f"   Role: {resume_data.get('role')}")
        logger.info(f"   Experience: {resume_data.get('totalYearsExperience')} years")
        logger.info(f"   Skills: {len(resume_data.get('skills', []))} found")
        
        # Extract JD
        logger.info("📋 Extracting job description...")
        jd_data = extract_structured_data_stable(request.jd_text, "Job Description")
        
        if not jd_data:
            logger.error("❌ Failed to extract job description")
            raise HTTPException(status_code=400, detail="Failed to extract job description")
        
        logger.info(f"✅ JD extracted successfully")
        logger.info(f"   Title: {jd_data.get('jobTitle')}")
        logger.info(f"   Experience Required: {jd_data.get('minExperienceYears')} years")
        logger.info(f"   Skills Required: {len(jd_data.get('requiredSkills', []))} found")
        
        # Calculate match
        logger.info("🎯 Calculating match...")
        matching_result = calculate_match(resume_data, jd_data)
        logger.info(f"✅ Match calculated: Score = {matching_result['overallScore']}")
        
        # Save to database
        if db_manager:
            try:
                db_manager.save_single_match(
                    user_email=email,
                    resume_name="Pasted Resume",
                    job_title=jd_data.get("jobTitle", "Unknown"),
                    resume_data=resume_data,
                    jd_data=jd_data,
                    matching_result=matching_result
                )
                logger.info("✅ Saved to database")
            except Exception as e:
                logger.warning(f"⚠️ Could not save to database: {e}")
        
        return {
            "status": "success",
            "data": matching_result,
            "resume": resume_data,
            "jd": jd_data,
            "weights_used": custom_weights
        } 
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Matching error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Matching error: {str(e)}")

@app.post("/api/match/batch")
async def batch_match(
    token: str = Query(...),
    jd_text: str = Form(...),
    files: List[UploadFile] = File(...),
    weights: Optional[str] = Form(None)
):
    """Process batch resume matching"""
    # Verify token - FIXED
    email = auth_manager.verify_token(token)
    if not email:
        logger.error("❌ Invalid token provided")
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info(f"✅ Token verified for user: {email}")
    
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description required")
    
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one resume required")
    
    try:
        logger.info(f"📊 Processing batch with {len(files)} files for user: {email}")
        # Parse custom weights if provided
        custom_weights = None
        if weights:
            try:
                import json
                custom_weights = json.loads(weights)
                logger.info(f"📊 Custom weights provided: {custom_weights}")
            except json.JSONDecodeError:
                logger.warning("⚠️ Invalid weights format, using defaults")
        else:
            logger.info(f"📊 Using default weights")
        
        # Extract JD
        logger.info("📋 Extracting job description...")
        # Extract JD
        jd_data = extract_structured_data_stable(jd_text, "Job Description")
        if not jd_data:
            raise HTTPException(status_code=400, detail="Failed to extract job description")
        
        results = []
        errors = []
        
        for file in files:
            try:
                content = await file.read()
                
                from io import BytesIO
                import pdfplumber
                from docx import Document
                
                file_ext = Path(file.filename).suffix.lower()
                text = None
                
                if file_ext == ".pdf":
                    try:
                        with pdfplumber.open(BytesIO(content)) as pdf:
                            text = ""
                            for page in pdf.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text
                    except Exception as e:
                        errors.append(f"{file.filename}: PDF error - {str(e)}")
                        continue
                
                elif file_ext in [".docx", ".doc"]:
                    try:
                        doc = Document(BytesIO(content))
                        text = "\n".join([para.text for para in doc.paragraphs])
                    except Exception as e:
                        errors.append(f"{file.filename}: DOCX error - {str(e)}")
                        continue
                
                elif file_ext == ".txt":
                    try:
                        text = content.decode("utf-8")
                    except Exception as e:
                        errors.append(f"{file.filename}: TXT error - {str(e)}")
                        continue
                
                else:
                    errors.append(f"{file.filename}: Unsupported format")
                    continue
                
                if not text or len(text.strip()) < 10:
                    errors.append(f"{file.filename}: No text extracted")
                    continue
                
                # Extract resume
                logger.info(f"📄 Processing {file.filename}...")
                resume_data = extract_structured_data_stable(text, "Resume")
                if not resume_data:
                    errors.append(f"{file.filename}: Failed to extract resume")
                    continue
                
                # Calculate match
                logger.info(f"🎯 Calculating match for {file.filename}...")
                matching_result = calculate_match(resume_data, jd_data, custom_weights=custom_weights)
                logger.info(f"✅ {file.filename}: Score = {matching_result['overallScore']}")
                results.append({
                    "filename": file.filename,
                    "resume_data": resume_data,
                    "matching_result": matching_result
                })
            
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
                errors.append(f"{file.filename}: {str(e)}")
        
        if not results:
            raise HTTPException(status_code=400, detail="No valid resumes processed")
        
        # Sort by score
        results.sort(key=lambda x: x["matching_result"]["overallScore"], reverse=True)
        logger.info(f"✅ Batch processing complete: {len(results)} successful, {len(errors)} errors")
        # Save to database
        if db_manager:
            try:
                batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                db_manager.save_batch_result(
                    user_email=email,
                    batch_id=batch_id,
                    job_title=jd_data.get("jobTitle", "Unknown"),
                    results=results,
                    jd_data=jd_data
                )
                logger.info(f"✅ Batch saved (ID: {batch_id})")
            except Exception as e:
                logger.warning(f"⚠️ Could not save batch to database: {e}")
        
        return {
            "status": "success",
            "total_files": len(files),
            "total_processed": len(results),
            "total_errors": len(errors),
            "errors": errors,
            "jd": jd_data,
            "results": results,
            "weights_used": custom_weights
            
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Batch matching error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch error: {str(e)}")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(token: str = Query(...)):
    """Get dashboard statistics"""
    email = auth_manager.verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not db_manager:
        return {"error": "Database not available"}
    
    try:
        stats = db_manager.get_dashboard_stats(user_email=email)
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/history")
async def get_history(token: str = Query(...), match_type: str = "single", limit: int = 100):
    """Get matching history"""
    email = auth_manager.verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not db_manager:
        return {"error": "Database not available"}
    
    try:
        if match_type == "single":
            data = db_manager.get_all_single_matches(user_email=email,limit=limit)
        elif match_type == "batch":
            data = db_manager.get_all_batch_results(user_email=email, limit=limit)
        else:
            raise HTTPException(status_code=400, detail="Invalid match type")
        
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STATIC FILES ====================

from fastapi.staticfiles import StaticFiles

try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
    logger.info("✅ Static files mounted successfully")
except Exception as e:
    logger.warning(f"⚠️ Could not mount static files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)