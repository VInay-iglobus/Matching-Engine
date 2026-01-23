"""
skills_analogy.py - Centralized Skill & Role Analogy Mapping
Contains:
1. SKILL_ANALOGY - Maps similar skills across all industries
2. ROLE_ANALOGY - Maps similar job titles/roles
3. EDUCATION_HIERARCHY - Education degree levels
4. ASSESSMENT_THRESHOLDS - Match scoring thresholds

Easily update and maintain skill/role relationships
Last Updated: 2024
"""

# ===== PROGRAMMING LANGUAGES =====
PROGRAMMING = {
    "python": ["py", "python3", "python 3"],
    "javascript": ["js", "nodejs", "node.js", "typescript", "ts"],
    "typescript": ["ts", "javascript", "js"],
    "java": ["springboot", "spring", "j2ee"],
    "c++": ["cpp", "c plus plus"],
    "c#": ["csharp", "c sharp", ".net"],
    "php": ["laravel", "symfony"],
    "golang": ["go"],
    "rust": ["rustlang"],
    "kotlin": ["android"],
    "swift": ["ios", "objective-c", "objc"],
    "ruby": ["ruby on rails", "ror"],
    "scala": ["spark", "big data"],
    "r": ["rstudio"],
}

# ===== WEB FRAMEWORKS & FRONTEND =====
WEB_FRONTEND = {
    "react": ["reactjs", "react.js", "jsx", "react native"],
    "angular": ["angularjs", "angular.js", "ng"],
    "vue": ["vuejs", "vue.js"],
    "next.js": ["nextjs", "next"],
    "nuxt": ["nuxtjs"],
    "svelte": ["sveltekit"],
    "html": ["html5", "markup"],
    "css": ["styling", "sass", "scss", "less", "postcss"],
    "sass": ["scss", "css"],
    "bootstrap": ["css framework", "frontend framework"],
    "tailwind": ["tailwind css", "utility css"],
}

# ===== BACKEND & APIS =====
BACKEND = {
    "nodejs": ["node.js", "node", "javascript", "js"],
    "express": ["express.js", "nodejs"],
    "django": ["python", "drf"],
    "flask": ["python", "microframework"],
    "spring": ["springboot", "java", "spring boot"],
    "fastapi": ["python", "async api"],
    "rest": ["restful", "rest api", "api"],
    "graphql": ["api", "query language"],
    "soap": ["web service"],
}

# ===== DATABASES =====
DATABASES = {
    "sql": ["mysql", "postgresql", "postgres", "t-sql", "tsql", "sql server", "oracle", "mariadb"],
    "mysql": ["sql", "mariadb", "percona"],
    "postgresql": ["postgres", "sql", "pg"],
    "mongodb": ["nosql", "document database", "mongo"],
    "redis": ["cache", "in-memory", "nosql", "key-value"],
    "cassandra": ["nosql", "distributed database"],
    "elasticsearch": ["search", "elk", "opensearch"],
    "firebase": ["realtime database", "backend as service"],
    "dynamodb": ["nosql", "aws"],
    "oracle": ["sql", "database", "relational"],
    "sqlite": ["sql", "lightweight database"],
}

# ===== CLOUD & DEVOPS =====
CLOUD_DEVOPS = {
    "aws": ["amazon", "amazon web services", "ec2", "s3", "lambda", "rds", "ecs", "cloudformation"],
    "azure": ["microsoft", "microsoft azure", "cosmos db", "app service"],
    "gcp": ["google cloud", "google", "bigquery", "cloud functions", "cloud storage"],
    "kubernetes": ["k8s", "container orchestration", "docker"],
    "docker": ["containers", "containerization", "docker compose"],
    "jenkins": ["ci/cd", "continuous integration", "automation", "devops"],
    "gitlab": ["ci/cd", "git", "github", "version control", "devops"],
    "github": ["git", "gitlab", "version control", "scm"],
    "github actions": ["ci/cd", "automation"],
    "terraform": ["infrastructure as code", "iac", "aws", "infrastructure"],
    "ansible": ["infrastructure", "automation", "devops", "configuration management"],
    "argocd": ["gitops", "continuous delivery"],
    "helm": ["kubernetes", "package manager"],
    "git": ["github", "gitlab", "bitbucket", "version control", "scm"],
}

# ===== DATA & ML =====
DATA_ML = {
    "tensorflow": ["machine learning", "ml", "deep learning", "keras"],
    "pytorch": ["machine learning", "ml", "deep learning", "torch"],
    "scikit-learn": ["machine learning", "ml", "sklearn"],
    "pandas": ["data analysis", "python", "data science"],
    "numpy": ["data analysis", "python", "data science"],
    "spark": ["big data", "apache spark", "scala", "pyspark"],
    "hadoop": ["big data", "mapreduce", "hdfs"],
    "airflow": ["data pipeline", "workflow orchestration"],
    "dbt": ["data transformation", "analytics engineering"],
    "tableau": ["data visualization", "business intelligence", "bi"],
    "powerbi": ["data visualization", "business intelligence", "bi", "microsoft"],
    "looker": ["data visualization", "business intelligence"],
    "analytics": ["data analytics", "business analytics"],
}

# ===== QA & TESTING =====
QA_TESTING = {
    "selenium": ["test automation", "web testing"],
    "pytest": ["testing", "python", "unit testing"],
    "junit": ["testing", "java", "unit testing"],
    "postman": ["api testing", "rest api testing"],
    "jira": ["project management", "issue tracking", "agile"],
    "testng": ["testing", "java", "automation"],
    "cucumber": ["bdd", "behavior driven development"],
    "automation": ["test automation", "qa automation"],
}

# ===== HR & HUMAN RESOURCES =====
HR = {
    "human resources": ["hr", "human resource", "hrm", "hr management", "human resources management", "hr operations", "people management"],
    "human resources management": ["hr", "human resource", "hrm", "hr management", "human resources"],
    "hr management": ["human resources", "hr", "human resource management", "hrm"],
    "recruitment": ["recruiting", "talent acquisition", "hiring", "recruitment process", "talent management", "sourcing", "talent"],
    "payroll": ["payroll management", "payroll administration", "payroll processing", "salary processing"],
    "payroll administration": ["payroll", "payroll management", "payroll processing", "salary"],
    "payroll management": ["payroll", "payroll administration", "salary"],
    "hrms": ["hr software", "hr system", "hr management system", "human resource management system", "greythr", "brighthr", "workday", "oracle hcm"],
    "employee engagement": ["engagement", "employee relations", "staff engagement", "team engagement"],
    "employee relations": ["employee engagement", "employee management", "staff relations"],
    "onboarding": ["induction", "employee onboarding", "new hire", "joining formalities", "orientation"],
    "induction": ["onboarding", "orientation", "employee onboarding", "training"],
    "performance management": ["appraisal", "performance appraisal", "performance review", "pms"],
    "performance appraisal": ["performance management", "appraisal", "performance review"],
    "leave management": ["attendance", "leave admin", "leave tracking", "attendance management"],
    "attendance management": ["leave management", "attendance tracking", "time tracking"],
    "compliance": ["statutory compliance", "legal compliance", "labour law", "labor law", "regulatory compliance"],
    "statutory compliance": ["compliance", "legal", "labour law", "labor law"],
    "labour law": ["labor law", "compliance", "statutory compliance", "employment law"],
    "labor law": ["labour law", "compliance", "statutory compliance"],
    "employee grievances": ["grievance management", "grievance handling", "employee relations", "conflict resolution"],
    "grievance management": ["employee grievances", "grievance handling", "conflict resolution"],
    "training": ["training and development", "l&d", "learning and development", "employee development", "training delivery"],
    "training and development": ["training", "l&d", "learning and development"],
    "exit management": ["offboarding", "employee exit", "exit formalities", "full and final"],
    "offboarding": ["exit management", "employee exit", "exit formalities"],
    "policy implementation": ["policy", "policy management", "procedure implementation"],
    "vendor management": ["vendor coordination", "vendor relations", "supplier management"],
    "talent acquisition": ["recruitment", "recruiting", "talent sourcing"],
    "talent management": ["recruitment", "employee development", "career management"],
}

# ===== SALES & SALES MANAGEMENT =====
SALES = {
    "sales": ["sales management", "sales execution", "b2b sales", "b2c sales", "sales revenue"],
    "sales management": ["sales", "sales execution", "sales leadership"],
    "sales leadership": ["sales management", "team management"],
    "business development": ["bd", "sales", "partnership", "business growth"],
    "crm": ["salesforce", "customer relationship management", "dynamics", "hubspot", "pipedrive"],
    "salesforce": ["crm", "customer relationship management", "sales", "force.com"],
    "sales execution": ["sales", "deal closure", "sales process"],
    "lead generation": ["prospecting", "business development", "sales"],
    "pipeline management": ["sales pipeline", "sales process", "deal management"],
    "account management": ["customer account", "account executive", "key account"],
    "customer retention": ["customer success", "client retention"],
    "closing deals": ["sales closure", "negotiation", "sales"],
    "negotiation": ["communication", "relationship management", "sales"],
}

# ===== MARKETING & DIGITAL MARKETING =====
MARKETING = {
    "marketing": ["digital marketing", "content marketing", "marketing management", "marketing strategy"],
    "digital marketing": ["marketing", "seo", "sem", "social media", "online marketing"],
    "seo": ["search engine optimization", "digital marketing", "organic search"],
    "sem": ["search engine marketing", "ppc", "digital marketing", "paid search"],
    "social media": ["marketing", "social media marketing", "content", "social media management"],
    "content marketing": ["marketing", "copywriting", "content creation", "content strategy"],
    "email marketing": ["marketing", "campaign", "email campaign"],
    "brand management": ["marketing", "brand strategy", "brand identity"],
    "product marketing": ["marketing", "product launch", "market positioning"],
    "marketing analytics": ["analytics", "marketing", "reporting"],
    "campaign management": ["marketing", "marketing execution"],
    "inbound marketing": ["marketing", "content marketing", "lead generation"],
    "outbound marketing": ["marketing", "sales", "lead generation"],
    "advertising": ["marketing", "digital advertising", "ad management"],
}

# ===== FINANCE & ACCOUNTING =====
FINANCE = {
    "accounting": ["bookkeeping", "financial accounting", "finance", "accounts"],
    "finance": ["financial management", "accounting", "bookkeeping", "financial planning"],
    "financial analysis": ["finance", "data analysis", "reporting", "financial modeling"],
    "budgeting": ["financial planning", "cost management", "budget planning"],
    "tax": ["tax planning", "compliance", "accounting", "tax preparation"],
    "audit": ["internal audit", "external audit", "compliance", "audit"],
    "excel": ["spreadsheet", "data analysis", "financial modeling"],
    "sap": ["erp", "enterprise resource planning", "finance", "accounting"],
    "quickbooks": ["accounting", "bookkeeping", "finance"],
    "financial planning": ["budgeting", "forecasting", "financial strategy"],
    "cost accounting": ["accounting", "cost management"],
    "accounts payable": ["accounting", "payables"],
    "accounts receivable": ["accounting", "receivables", "ar"],
    "general ledger": ["accounting", "gl"],
}

# ===== PROJECT MANAGEMENT =====
PROJECT_MANAGEMENT = {
    "project management": ["pm", "project manager", "leadership", "project planning"],
    "agile": ["scrum", "kanban", "agile methodology", "agile framework"],
    "scrum": ["agile", "sprint", "agile methodology"],
    "kanban": ["agile", "lean"],
    "jira": ["project management", "issue tracking", "agile", "project tracking"],
    "asana": ["project management", "task management"],
    "monday.com": ["project management"],
    "confluence": ["documentation", "collaboration", "wiki"],
    "risk management": ["project risk", "risk assessment"],
    "resource management": ["resource planning", "team allocation"],
    "timeline management": ["project planning", "scheduling"],
}

# ===== SUPPLY CHAIN & LOGISTICS =====
SUPPLY_CHAIN = {
    "supply chain": ["logistics", "procurement", "supply chain management", "scm"],
    "logistics": ["supply chain", "transportation", "warehouse management"],
    "procurement": ["purchasing", "supplier management", "sourcing"],
    "inventory management": ["stock management", "warehouse", "inventory"],
    "warehouse management": ["logistics", "inventory", "warehouse"],
    "vendor management": ["supplier", "vendor relations", "sourcing"],
    "demand planning": ["forecasting", "supply planning"],
    "forecasting": ["demand planning", "planning"],
}

# ===== MANUFACTURING & OPERATIONS =====
MANUFACTURING = {
    "manufacturing": ["production", "operations", "factory management"],
    "operations": ["manufacturing", "operational management", "process"],
    "production": ["manufacturing", "production management"],
    "quality assurance": ["qa", "quality control", "quality"],
    "quality control": ["qa", "inspection", "quality"],
    "lean manufacturing": ["manufacturing", "process improvement", "efficiency"],
    "six sigma": ["quality", "process improvement", "lean"],
    "kaizen": ["process improvement", "continuous improvement"],
    "process improvement": ["optimization", "efficiency", "lean"],
    "maintenance": ["equipment maintenance", "preventive maintenance"],
    "safety": ["occupational safety", "health and safety", "ohs"],
}

# ===== HEALTHCARE & MEDICAL =====
HEALTHCARE = {
    "healthcare management": ["health management", "hospital management"],
    "nursing": ["registered nurse", "clinical nursing", "patient care"],
    "clinical skills": ["medical", "patient care", "healthcare"],
    "patient care": ["nursing", "healthcare", "clinical"],
    "medical coding": ["healthcare", "billing", "medical records"],
    "pharmaceutical": ["pharma", "medical", "drug"],
    "laboratory": ["lab", "testing", "pathology"],
    "surgery": ["surgical", "medical procedure"],
    "anesthesia": ["surgical support", "medical"],
    "radiology": ["medical imaging", "x-ray"],
    "pharmacy": ["pharmacist", "medication", "pharmaceutical"],
}

# ===== EDUCATION & TRAINING =====
EDUCATION = {
    "teaching": ["education", "instruction", "classroom management"],
    "education": ["teaching", "curriculum", "academic"],
    "training delivery": ["training", "instruction", "l&d"],
    "curriculum development": ["education", "course design", "instructional design"],
    "instructional design": ["education", "training", "elearning"],
    "elearning": ["online training", "digital learning", "instructional design"],
    "academic": ["education", "subject matter expertise"],
    "student management": ["education", "classroom"],
    "assessment": ["evaluation", "testing", "measurement"],
}

# ===== CUSTOMER SERVICE & SUPPORT =====
CUSTOMER_SERVICE = {
    "customer service": ["customer support", "customer care", "client service"],
    "customer support": ["customer service", "technical support", "helpdesk"],
    "customer experience": ["cx", "customer satisfaction", "service quality"],
    "technical support": ["support", "troubleshooting", "helpdesk"],
    "helpdesk": ["support", "ticket management", "user support"],
    "ticketing": ["support", "issue tracking", "ticket system"],
    "call center": ["customer service", "inbound", "outbound"],
    "chat support": ["customer service", "live chat", "messaging"],
    "email support": ["customer service", "support"],
    "customer retention": ["loyalty", "customer success", "retention"],
    "customer satisfaction": ["customer experience", "service quality"],
}

# ===== LEGAL & COMPLIANCE =====
LEGAL = {
    "legal": ["law", "contract", "legal compliance"],
    "compliance": ["regulatory", "legal", "policy"],
    "contract management": ["legal", "contract"],
    "intellectual property": ["ip", "patents", "trademarks"],
    "litigation": ["legal", "court"],
    "legal research": ["legal", "law"],
    "regulatory compliance": ["compliance", "regulations"],
    "data privacy": ["compliance", "gdpr", "ccpa"],
    "gdpr": ["data privacy", "compliance", "eu regulation"],
}

# ===== GENERAL BUSINESS SKILLS =====
BUSINESS_SKILLS = {
    "communication": ["interpersonal", "presentation", "writing", "public speaking"],
    "leadership": ["management", "team leadership", "people management", "executive"],
    "management": ["leadership", "team management", "people management"],
    "team management": ["leadership", "management", "team leadership"],
    "people management": ["leadership", "management", "hr"],
    "problem solving": ["analytical", "troubleshooting", "critical thinking"],
    "analytical": ["problem solving", "data analysis", "research"],
    "critical thinking": ["problem solving", "analysis"],
    "stakeholder management": ["communication", "relationship management"],
    "relationship management": ["stakeholder management", "communication"],
    "time management": ["organization", "planning", "productivity"],
    "organization": ["time management", "planning", "process improvement"],
    "planning": ["strategy", "organization", "project planning"],
    "strategy": ["strategic planning", "business strategy", "planning"],
    "strategic planning": ["strategy", "business planning"],
    "business acumen": ["business knowledge", "understanding"],
    "decision making": ["analysis", "judgment", "leadership"],
    "documentation": ["writing", "technical writing", "reporting"],
    "reporting": ["documentation", "analytics", "communication"],
    "research": ["analysis", "investigation", "data"],
    "presentation skills": ["communication", "public speaking"],
    "public speaking": ["presentation", "communication"],
    "writing": ["documentation", "communication", "content"],
    "listening": ["communication", "interpersonal"],
    "teamwork": ["collaboration", "team work"],
    "collaboration": ["teamwork", "communication"],
    "adaptability": ["flexibility", "learning"],
    "flexibility": ["adaptability", "change management"],
    "attention to detail": ["quality", "accuracy"],
    "multitasking": ["time management", "productivity"],
    "reliability": ["dependability", "accountability"],
    "accountability": ["responsibility", "reliability"],
    "creativity": ["innovation", "design thinking"],
    "innovation": ["creativity", "new ideas"],
    "customer focus": ["customer service", "customer satisfaction"],
    "result oriented": ["performance", "achievement"],
    "performance": ["achievement", "result oriented"],
}

# ===== NETWORKING =====
NETWORKING = {
    "networking": ["network administration", "network security", "cisco"],
    "linux": ["unix", "operating system", "ubuntu", "centos"],
    "windows": ["operating system", "microsoft"],
    "bash": ["shell", "scripting", "linux", "command line"],
    "shell scripting": ["bash", "scripting", "unix"],
    "cisco": ["networking", "ccna"],
    "networking protocols": ["tcp/ip", "networking"],
}

# ===== AUTOMOTIVE & MECHANICAL =====
MECHANICAL = {
    "automotive": ["vehicle", "car", "mechanical"],
    "mechanical engineering": ["engineering", "design", "manufacturing"],
    "cad": ["design", "autocad", "solidworks"],
    "autocad": ["cad", "design", "drafting"],
    "solidworks": ["cad", "design", "3d modeling"],
    "electrical": ["electrical engineering", "power"],
    "civil engineering": ["construction", "infrastructure"],
    "welding": ["fabrication", "metalwork"],
    "maintenance": ["equipment", "repair", "upkeep"],
}

# ===== CONSTRUCTION & REAL ESTATE =====
CONSTRUCTION = {
    "construction": ["building", "project management", "site management"],
    "real estate": ["property", "real estate management"],
    "project management": ["planning", "construction", "coordination"],
    "site management": ["construction", "supervision"],
    "building": ["construction", "real estate"],
    "architecture": ["design", "building", "construction"],
}

# ===== HOSPITALITY & TOURISM =====
HOSPITALITY = {
    "hospitality": ["hotel management", "customer service", "guest service"],
    "hotel management": ["hospitality", "operations", "guest service"],
    "food service": ["hospitality", "restaurant", "catering"],
    "event management": ["event planning", "coordination", "hospitality"],
    "guest service": ["customer service", "hospitality"],
    "tourism": ["hospitality", "travel"],
    "reservation": ["booking", "hospitality"],
}

# ===== MISCELLANEOUS =====
MISCELLANEOUS = {
    "excel": ["spreadsheet", "data analysis", "vba", "ms office"],
    "vba": ["excel", "automation"],
    "ms office": ["excel", "word", "powerpoint"],
    "word": ["ms office", "writing"],
    "powerpoint": ["ms office", "presentation"],
    "itil": ["it service management", "process improvement"],
    "itil v3": ["itil", "it service management"],
    "itil v4": ["itil", "it service management"],
}

# ===== COMBINE ALL SKILL ANALOGIES =====
SKILL_ANALOGY = {
    **PROGRAMMING,
    **WEB_FRONTEND,
    **BACKEND,
    **DATABASES,
    **CLOUD_DEVOPS,
    **DATA_ML,
    **QA_TESTING,
    **HR,
    **SALES,
    **MARKETING,
    **FINANCE,
    **PROJECT_MANAGEMENT,
    **SUPPLY_CHAIN,
    **MANUFACTURING,
    **HEALTHCARE,
    **EDUCATION,
    **CUSTOMER_SERVICE,
    **LEGAL,
    **BUSINESS_SKILLS,
    **NETWORKING,
    **MECHANICAL,
    **CONSTRUCTION,
    **HOSPITALITY,
    **MISCELLANEOUS,
}

# ===== EDUCATION HIERARCHY =====
EDUCATION_HIERARCHY = {
    "high school": 1,
    "hsc": 1,
    "intermediate": 1,
    "diploma": 1,
    "associate": 1.5,
    "bachelor": 2,
    "bachelor's": 2,
    "b.a": 2,
    "b.s": 2,
    "b.tech": 2,
    "b.e": 2,
    "bca": 2,
    "bcom": 2,
    "bba": 2,
    "llb": 2,
    "mbbs": 2,
    "master": 3,
    "master's": 3,
    "m.a": 3,
    "m.s": 3,
    "m.tech": 3,
    "mba": 3.5,
    "m.b.a": 3.5,
    "pgdm": 3.5,
    "ms": 3,
    "ma": 3,
    "phd": 4,
    "doctorate": 4,
    "md": 4,
    "postgraduate": 3,
}

# ===== ASSESSMENT THRESHOLDS =====
ASSESSMENT_THRESHOLDS = {
    70: {"text": "Excellent Match"},
    50: {"text": "Good Match"},
    0: {"text": "Needs Review"}
}

# ==================== CONSOLIDATED SKILL ANALOGY ====================
# Combines all skill categories for easier lookup

SKILL_ANALOGY = {}
for category in [PROGRAMMING, WEB_FRONTEND, BACKEND, DATABASES, CLOUD_DEVOPS,
                  DATA_ML, QA_TESTING, BUSINESS_SKILLS, HR, SALES, MARKETING, FINANCE, LEGAL]:
    if category:
        SKILL_ANALOGY.update(category)

# ==================== ROLE/JOB TITLE ANALOGIES ====================
# Maps similar job titles that are essentially the same role

ROLE_ANALOGY = {
    # ===== SOFTWARE ENGINEERING =====
    "software engineer": ["developer", "software developer", "engineer", "software development engineer", "sde"],
    "senior software engineer": ["senior developer", "staff engineer", "principal engineer"],
    "junior software engineer": ["junior developer", "associate engineer", "graduate engineer"],
    "frontend engineer": ["frontend developer", "ui engineer", "react developer", "angular developer"],
    "backend engineer": ["backend developer", "api developer", "server engineer"],
    "full stack engineer": ["full stack developer", "fullstack engineer"],
    "devops engineer": ["devops", "infrastructure engineer", "site reliability engineer", "sre"],
    "data engineer": ["data pipeline engineer", "etl engineer"],
    "ml engineer": ["machine learning engineer", "ai engineer"],
    
    # ===== MANAGEMENT & LEADERSHIP =====
    "manager": ["project manager", "team lead", "team manager", "engineering manager"],
    "project manager": ["pm", "project lead", "project coordinator"],
    "product manager": ["pm", "product lead", "product owner"],
    "engineering manager": ["tech lead manager", "software engineering manager"],
    "director": ["senior director", "vp", "vice president"],
    "head": ["department head", "team head", "function head"],
    
    # ===== HR ROLES =====
    "hr manager": ["human resources manager", "hr operations manager", "people manager"],
    "recruiter": ["recruitment specialist", "talent recruiter", "hiring manager", "sourcing specialist"],
    "hr executive": ["hr specialist", "human resources executive", "people operations"],
    "hr generalist": ["human resources generalist", "hr professional"],
    "compensation analyst": ["comp analyst", "payroll analyst", "benefits analyst"],
    "talent acquisition specialist": ["recruiter", "sourcing specialist", "talent sourcer"],
    
    # ===== SALES ROLES =====
    "sales executive": ["sales representative", "account executive", "sales professional"],
    "sales manager": ["sales lead", "regional sales manager", "territory manager"],
    "business development executive": ["bd executive", "business consultant", "account manager"],
    "account manager": ["relationship manager", "client manager", "key account manager"],
    
    # ===== MARKETING ROLES =====
    "marketing manager": ["marketing lead", "marketing director"],
    "digital marketing specialist": ["digital marketer", "online marketing specialist"],
    "content manager": ["content specialist", "content creator"],
    "brand manager": ["brand specialist", "brand lead"],
    
    # ===== FINANCE & ACCOUNTING =====
    "accountant": ["accounting specialist", "accounting associate"],
    "senior accountant": ["accounting manager", "supervisor accountant"],
    "financial analyst": ["analyst", "finance analyst", "financial reporting analyst"],
    "audit manager": ["audit lead", "audit supervisor"],
    
    # ===== OPERATIONS =====
    "operations manager": ["ops manager", "operations lead", "process manager"],
    "supply chain manager": ["scm manager", "logistics manager"],
    "warehouse manager": ["warehouse supervisor", "inventory manager"],
    "quality manager": ["quality lead", "qa manager", "quality assurance manager"],
    
    # ===== CUSTOMER SERVICE =====
    "customer service manager": ["customer support manager", "cs manager", "support lead"],
    "customer service executive": ["customer support executive", "support specialist"],
    "technical support specialist": ["support engineer", "technical support engineer"],
    
    # ===== DATA & ANALYTICS =====
    "data analyst": ["analytics specialist", "business analyst", "reporting analyst"],
    "senior data analyst": ["data analyst manager", "analytics lead"],
    "data scientist": ["data science engineer", "ml scientist"],
    
    # ===== QA & TESTING =====
    "qa engineer": ["quality assurance engineer", "test engineer", "qa specialist"],
    "automation engineer": ["automation test engineer", "qa automation engineer"],
    "manual tester": ["qa tester", "test specialist"],
    
    # ===== GENERAL SYNONYMS =====
    "engineer": ["specialist", "expert"],
    "specialist": ["expert", "professional"],
    "executive": ["professional", "specialist"],
    "lead": ["manager", "supervisor"],
    "supervisor": ["manager", "team lead"],
    "coordinator": ["assistant", "associate"],
    "consultant": ["advisor", "expert"],
}

# ===== HELPER FUNCTIONS =====

def get_skill_group(skill_name):
    """
    Find the skill group for a given skill name.
    Returns the primary skill name that represents the group.
    E.g., "reactjs" → "react", "typescript" → "javascript"
    """
    if not skill_name:
        return None
    
    skill_lower = str(skill_name).lower().strip()
    skill_lower = skill_lower.replace('.', '').replace('-', ' ')
    
    # Search through all skill categories
    all_categories = [
        PROGRAMMING, WEB_FRONTEND, BACKEND, DATABASES, CLOUD_DEVOPS,
        DATA_ML, TESTING, AI_ML_ADVANCED, SOFT_SKILLS, BUSINESS_SKILLS
    ]
    
    for category in all_categories:
        for primary, aliases in category.items():
            # Check if it's the primary skill
            if skill_lower == primary.lower():
                return primary.lower()
            
            # Check if it's in the aliases
            for alias in aliases:
                if skill_lower == alias.lower():
                    return primary.lower()
    
    return None

def find_equivalent_skills(skill_name):
    """
    Find all equivalent skills for a given skill.
    E.g., "react" → ["reactjs", "react.js", "jsx", "react native"]
    """
    if not skill_name:
        return []
    
    group = get_skill_group(skill_name)
    if not group:
        return [skill_name]
    
    # Find the category containing this group
    all_categories = [
        PROGRAMMING, WEB_FRONTEND, BACKEND, DATABASES, CLOUD_DEVOPS,
        DATA_ML, TESTING, AI_ML_ADVANCED, SOFT_SKILLS, BUSINESS_SKILLS
    ]
    
    for category in all_categories:
        if group in category:
            return [group] + category[group]
    
    return [skill_name]

def is_technical_skill(skill_name):
    """
    Check if a skill is technical (not soft skills or business skills).
    Returns True for technical skills, False for soft/business skills.
    """
    if not skill_name:
        return False
    
    skill_lower = str(skill_name).lower().strip()
    
    # Check soft skills and business skills
    non_technical = list(SOFT_SKILLS.keys()) + list(BUSINESS_SKILLS.keys())
    
    for soft_skill in non_technical:
        if skill_lower == soft_skill.lower():
            return False
        # Check aliases
        if soft_skill in [SOFT_SKILLS, BUSINESS_SKILLS]:
            if isinstance(SOFT_SKILLS.get(soft_skill, []), list):
                for alias in SOFT_SKILLS.get(soft_skill, []):
                    if skill_lower == alias.lower():
                        return False
            if isinstance(BUSINESS_SKILLS.get(soft_skill, []), list):
                for alias in BUSINESS_SKILLS.get(soft_skill, []):
                    if skill_lower == alias.lower():
                        return False
    
    # If it's in any technical category, it's technical
    technical_categories = [
        PROGRAMMING, WEB_FRONTEND, BACKEND, DATABASES, CLOUD_DEVOPS,
        DATA_ML, TESTING, AI_ML_ADVANCED
    ]
    
    for category in technical_categories:
        if get_skill_group(skill_name) in category:
            return True
    
    return False