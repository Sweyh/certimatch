import re, pickle, logging
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / 'ml_models' / 'job_model(1) (1).pkl'
_model_data = None

def _load_model():
    global _model_data
    if _model_data is None:
        try:
            with open(MODEL_PATH, 'rb') as f:
                _model_data = pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            _model_data = {}
    return _model_data

SKILL_PATTERNS = [
    # Programming Languages
    ('Python',          ['python', 'py']),
    ('Java',            [r'java(?!script)', r'\bjava\b']),
    ('JavaScript',      ['javascript', 'js', 'nodejs', 'node.js']),
    ('TypeScript',      ['typescript', 'ts']),
    ('C++',             [r'c\+\+', r'\bcpp\b', 'advanced cpp', r'\bc\+\+']),
    ('C',               [r'\bc programming\b', r'language c\b', r'\bc language\b', r'\bc\s']),
    ('C#',              ['c#', 'c sharp', 'csharp']),
    ('PHP',             [r'\bphp\b']),
    ('Go',              [r'\bgo\b', 'golang']),
    ('Rust',            [r'\brust\b']),
    ('Kotlin',          ['kotlin']),
    ('Swift',           [r'\bswift\b']),
    ('R',               [r'\br\b', r'\br programming\b']),
    ('Ruby',            ['ruby']),
    ('Perl',            ['perl']),
    ("Objective-C",     ['objective c', 'objective-c']),
    ('Scala',           ['scala']),
    ('Groovy',          ['groovy']),
    
    # Web Frameworks & Frontend
    ('React',           [r'\breact\b', 'reactjs', r'\bfb/react\b']),
    ('Angular',         ['angular', 'angularjs']),
    ('Vue.js',          ['vue.js', 'vue', 'vuejs']),
    ('Express',         ['express', 'expressjs']),
    ('Django',          ['django', 'django rest']),
    ('Flask',           [r'\bflask\b']),
    ('Spring Boot',     ['spring boot', 'springboot']),
    ('FastAPI',         ['fastapi', 'fast api']),
    ('ASP.NET',         ['asp.net', 'asp net']),
    ('Next.js',         ['next.js', 'nextjs']),
    ('Gatsby',          ['gatsby']),
    ('jQuery',          [r'\bjquery\b']),
    
    # Frontend Languages & Markup
    ('HTML',            [r'\bhtml\b', 'html5']),
    ('CSS',             [r'\bcss\b', 'css3', 'sass', 'scss']),
    ('SCSS',            ['scss', 'sass']),
    ('Web Development', ['web development', 'web design', 'web development']),
    
    # Databases
    ('SQL',             [r'\bsql\b', 'structured query']),
    ('MySQL',           ['mysql']),
    ('PostgreSQL',      ['postgresql', 'postgres']),
    ('MongoDB',         ['mongodb', 'mongo']),
    ('Firebase',        ['firebase']),
    ('SQLite',          ['sqlite']),
    ('Oracle',          ['oracle database', r'\boracle\b']),
    ('Cassandra',       ['cassandra']),
    ('Redis',           ['redis']),
    ('DynamoDB',        ['dynamodb', 'dynamo']),
    
    # Data Science & Analytics
    ('Machine Learning',['machine learning', r'\bml\b', 'ml models']),
    ('Deep Learning',   ['deep learning', 'neural networks']),
    ('Data Science',    ['data science']),
    ('Data Analysis',   ['data analysis', 'data analytics', 'analytics']),
    ('Big Data',        ['big data', 'hadoop', 'spark']),
    ('Statistics',      ['statistics', 'statistical']),
    ('Pandas',          ['pandas']),
    ('NumPy',           ['numpy']),
    ('Scikit-learn',    ['scikit.learn', 'sklearn', 'scikit learn']),
    ('SciPy',           ['scipy']),
    ('Matplotlib',      ['matplotlib']),
    ('Seaborn',         ['seaborn']),
    ('Plotly',          ['plotly']),
    ('Excel',           ['advanced excel', 'excel']),
    ('Tableau',         ['tableau']),
    ('Power BI',        ['power bi', 'powerbi', 'power-bi']),
    ('Apache Spark',    ['apache spark', 'spark']),
    ('Hadoop',          ['hadoop']),
    
    # AI/ML Frameworks
    ('TensorFlow',      ['tensorflow', 'tf']),
    ('PyTorch',         ['pytorch']),
    ('Keras',           ['keras']),
    ('OpenCV',          ['opencv']),
    ('NLP',             ['natural language processing', r'\bnlp\b', 'nlp']),
    ('Transformers',    ['transformers', 'bert', 'gpt', 'huggingface']),
    ('NLTK',            ['nltk']),
    ('Spacy',           ['spacy']),
    
    # Cloud Platforms
    ('AWS',             [r'\baws\b', 'amazon web services', 'ec2', 's3', 'lambda']),
    ('Azure',           [r'\bazure\b', 'azure cloud']),
    ('Google Cloud',    ['google cloud', 'gcp']),
    ('Kubernetes',      ['kubernetes', 'k8s', 'k8']),
    ('Docker',          ['docker']),
    ('Heroku',          ['heroku']),
    ('DigitalOcean',    ['digital ocean', 'digitalocean']),
    ('IBM Cloud',       ['ibm cloud']),
    
    # DevOps & Tools
    ('Git',             [r'\bgit\b', 'github', 'gitlab', 'bitbucket']),
    ('Jenkins',         ['jenkins']),
    ('GitLab CI',       ['gitlab ci', 'gitlabci']),
    ('GitHub Actions',  ['github actions']),
    ('CI/CD',           ['ci/cd', 'continuous integration', 'continuous deployment']),
    ('Terraform',       ['terraform']),
    ('Ansible',         ['ansible']),
    ('Prometheus',      ['prometheus']),
    ('Grafana',         ['grafana']),
    ('Linux',           ['linux', 'ubuntu', 'centos', 'redhat']),
    ('Bash',            ['bash', 'shell scripting']),
    ('PowerShell',      ['powershell']),
    
    # Others
    ('REST API',        ['rest api', 'restful', 'rest']),
    ('GraphQL',         ['graphql']),
    ('API Design',      ['api design', 'api development']),
    ('Blockchain',      ['blockchain', 'ethereum', 'bitcoin']),
    ('Solidity',        ['solidity']),
    ('Smart Contracts', ['smart contracts']),
    ('Mobile Development', ['mobile development', 'mobile app']),
    ('Android',         ['android']),
    ('iOS',             ['ios', 'iphone']),
    ('Flutter',         ['flutter']),
    ('React Native',    ['react native']),
    ('Xamarin',         ['xamarin']),
    ('Testing',         ['unit testing', 'integration testing', 'testing']),
    ('Pytest',          ['pytest']),
    ('JUnit',           ['junit']),
    ('Jest',            ['jest']),
    ('Selenium',        ['selenium']),
    ('Agile',           ['agile', 'scrum', 'kanban']),
    ('Microservices',   ['microservices', 'microservice']),
    ('Security',        ['cybersecurity', 'security', 'encryption']),
    ('AWS Lambda',      ['aws lambda', 'lambda']),
    ('Message Queues',  ['rabbitmq', 'kafka', 'message queue']),
    ('Networking',      ['networking', 'tcp/ip', 'dns']),
    ('Cloud Computing', ['cloud computing', 'cloud']),
    ('Automation',      ['automation', 'scripting']),
]

def extract_skills_from_text(text: str) -> list:
    if not text or not text.strip():
        logger.warning("No text provided for skill extraction")
        return []
    text_lower = text.lower()
    logger.info(f"Extracting skills from text (length: {len(text)})")
    found = []
    for skill_name, patterns in SKILL_PATTERNS:
        for pattern in patterns:
            try:
                if re.search(pattern, text_lower):
                    found.append(skill_name)
                    logger.debug(f"Matched skill: {skill_name} (pattern: {pattern})")
                    break
            except re.error:
                if pattern.lower() in text_lower:
                    found.append(skill_name)
                    logger.debug(f"Matched skill: {skill_name} (literal: {pattern})")
                    break
    logger.info(f"Extracted skills: {list(dict.fromkeys(found))}")
    return list(dict.fromkeys(found))


def predict_salary(role: str, skills: list, experience: int, location: str) -> dict:
    data = _load_model()
    df   = data.get('df')
    if df is None:
        return _fallback(role, experience)

    role_lower = role.lower().strip()
    subset = df[df['job_title'].str.lower().str.contains(role_lower, na=False)]
    if subset.empty:
        for w in role_lower.split():
            if len(w) > 3:
                subset = df[df['job_title'].str.lower().str.contains(w, na=False)]
                if not subset.empty: break
    if subset.empty:
        return _fallback(role, experience)

    CORRECTION = 0.12
    base    = float(subset['salary_lpa'].mean()) * CORRECTION
    min_sal = float(subset['salary_lpa'].min())  * CORRECTION
    max_sal = float(subset['salary_lpa'].max())  * CORRECTION

    exp_factor  = min(0.6 + (experience / 10) * 0.8, 1.4)
    loc = location.lower()
    loc_bonus   = 1.15 if any(x in loc for x in ['bangalore','bengaluru']) else \
                  1.10 if any(x in loc for x in ['hyderabad','mumbai']) else \
                  1.05 if any(x in loc for x in ['chennai','pune','delhi']) else 1.0
    skill_bonus = min(1.0 + (len(skills) * 0.02), 1.20)

    predicted = round(base * exp_factor * loc_bonus * skill_bonus, 2)
    min_pred  = round(min_sal * exp_factor * 0.8, 2)
    max_pred  = round(max_sal * exp_factor * loc_bonus * 1.1, 2)

    predicted = max(3.0,  min(predicted, 80.0))
    min_pred  = max(2.5,  min(min_pred,  60.0))
    max_pred  = max(5.0,  min(max_pred, 100.0))

    return {
        'predicted_lpa': predicted,
        'min_lpa':       min_pred,
        'max_lpa':       max_pred,
        'currency':      'INR',
        'note':          f"Based on {len(subset)} similar roles | {experience} yr exp | {location}",
    }


def _fallback(role, experience):
    rl = role.lower()
    if any(k in rl for k in ['machine learning','ml','ai','data scientist']): base = 10.0
    elif any(k in rl for k in ['blockchain','quantum']): base = 12.0
    elif 'data' in rl:   base = 8.0
    elif any(k in rl for k in ['software','engineer','developer']): base = 7.0
    else: base = 5.0
    base += experience * 0.8
    base  = min(base, 50.0)
    return {
        'predicted_lpa': round(base, 2),
        'min_lpa':       round(base * 0.7, 2),
        'max_lpa':       round(base * 1.4, 2),
        'currency':      'INR',
        'note':          'Estimated (role not found in dataset)',
    }


def get_skill_gap(user_skills: list, target_role: str) -> dict:
    data = _load_model()
    df   = data.get('df')
    if df is None:
        return {'missing':[],'matched':[],'error':'Model not loaded'}

    subset = df[df['job_title'].str.lower().str.contains(target_role.lower().strip(), na=False)]
    if subset.empty:
        return {
            'target_role': target_role,'missing':[],'matched':[],
            'readiness_percent':0,'matched_count':0,'missing_count':0,'suggestions':[],
            'error':'Role not found. Try: Data Scientist, ML Researcher, AI Engineer, Blockchain Developer',
        }

    all_req = set()
    for _, row in subset.iterrows():
        for s in str(row['skills_required']).split(','):
            all_req.add(s.strip().lower())

    user_lower = [u.lower() for u in user_skills]
    matched = sorted([s for s in all_req if s in user_lower])
    missing = sorted([s for s in all_req if s not in user_lower])

    COURSES = {
        'python':'Coursera: Python for Everybody',
        'machine learning':'Coursera: ML by Andrew Ng',
        'sql':'Udemy: Complete SQL Bootcamp',
        'tensorflow':'TensorFlow Developer Certificate',
        'pytorch':'PyTorch.org Tutorials',
        'docker':'Docker on Udemy',
        'aws':'AWS Skill Builder (free)',
        'linear algebra':'MIT OpenCourseWare',
        'qiskit':'IBM Quantum Learning (free)',
        'solidity':'CryptoZombies (free)',
    }
    suggestions = [{'skill':s,'course':COURSES.get(s,f'Search "{s}" on Coursera')} for s in missing]

    return {
        'target_role':target_role,'total_required':len(all_req),
        'matched_count':len(matched),'missing_count':len(missing),
        'matched':matched,'missing':missing,'suggestions':suggestions,
        'readiness_percent':round(len(matched)/max(len(all_req),1)*100),
    }