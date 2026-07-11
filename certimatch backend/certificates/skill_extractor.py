"""
Skill extractor — maps certificate title keywords to known skill sets.
Replace with NLP / PDF parsing as needed.
"""

CERT_SKILL_MAP = {
    # Programming Languages
    'python':           ['Python', 'OOP', 'Data Structures'],
    'java':             ['Java', 'Spring Boot', 'OOP'],
    'javascript':       ['JavaScript', 'DOM', 'Async Programming'],
    'typescript':       ['TypeScript', 'Type Safety', 'OOP'],
    'c++':              ['C++', 'Memory Management', 'System Programming'],
    'c#':               ['C#', 'ASP.NET', '.NET Framework'],
    'php':              ['PHP', 'Web Development', 'Server-Side'],
    'kotlin':           ['Kotlin', 'Android Development'],
    'swift':            ['Swift', 'iOS Development'],
    'go':               ['Go', 'Concurrent Programming'],
    'rust':             ['Rust', 'Memory Safety', 'Performance'],
    
    # Web Frameworks
    'django':           ['Django', 'REST APIs', 'Python', 'MySQL'],
    'flask':            ['Flask', 'Microservices', 'Python'],
    'react':            ['React', 'JavaScript', 'HTML', 'CSS', 'Component Architecture'],
    'angular':          ['Angular', 'TypeScript', 'RxJS'],
    'vue':              ['Vue.js', 'Component Development'],
    'express':          ['Express.js', 'Node.js', 'REST APIs'],
    'spring boot':      ['Spring Boot', 'Java', 'Microservices'],
    'fastapi':          ['FastAPI', 'Python', 'Async'],
    
    # Frontend
    'html':             ['HTML', 'Web Markup', 'Semantic HTML'],
    'css':              ['CSS', 'Responsive Design', 'SASS', 'Layout'],
    'responsive':       ['Responsive Design', 'CSS', 'Mobile-First'],
    
    # Databases
    'sql':              ['SQL', 'MySQL', 'Database Design', 'Query Optimization'],
    'mysql':            ['MySQL', 'SQL', 'Database Administration'],
    'postgresql':       ['PostgreSQL', 'Advanced SQL', 'ACID'],
    'mongodb':          ['MongoDB', 'NoSQL', 'Document Databases'],
    'firebase':         ['Firebase', 'Realtime Database', 'Authentication'],
    'redis':            ['Redis', 'Caching', 'Session Management'],
    
    # Data Science & Analytics
    'machine learning': ['Machine Learning', 'Scikit-learn', 'Python', 'Statistics'],
    'data science':     ['Python', 'SQL', 'Data Analysis', 'Pandas', 'Visualization', 'Statistics'],
    'deep learning':    ['Deep Learning', 'TensorFlow', 'PyTorch', 'Neural Networks', 'CNN', 'RNN'],
    'data analysis':    ['Data Analysis', 'Excel', 'Tableau', 'Power BI'],
    'nlp':              ['NLP', 'Python', 'NLTK', 'Transformers'],
    'computer vision':  ['Computer Vision', 'OpenCV', 'Image Processing'],
    'statistics':       ['Statistics', 'Probability', 'Hypothesis Testing'],
    
    # Cloud & DevOps
    'aws':              ['Cloud Computing', 'AWS', 'EC2', 'S3', 'IAM', 'Lambda'],
    'azure':            ['Cloud Computing', 'Azure', 'AKS', 'Azure Functions'],
    'docker':           ['Docker', 'Containerization', 'DevOps'],
    'kubernetes':       ['Kubernetes', 'Orchestration', 'Container Management'],
    'ci/cd':            ['CI/CD', 'Jenkins', 'DevOps'],
    'devops':           ['DevOps', 'Infrastructure as Code', 'Automation'],
    
    # Mobile
    'android':          ['Android Development', 'Java', 'Kotlin', 'Mobile Apps'],
    'ios':              ['iOS Development', 'Swift', 'Objective-C'],
    'flutter':          ['Flutter', 'Mobile Development', 'Dart'],
    'react native':     ['React Native', 'JavaScript', 'Mobile Apps'],
    
    # Blockchain
    'blockchain':       ['Blockchain', 'Solidity', 'Smart Contracts', 'Ethereum'],
    'solidity':         ['Solidity', 'Smart Contracts', 'Ethereum'],
    'web3':             ['Web3', 'Blockchain', 'Cryptocurrency'],
    
    # Testing & QA
    'testing':          ['Testing', 'Test Automation', 'QA'],
    'selenium':         ['Selenium', 'Test Automation', 'Python'],
    'junit':            ['JUnit', 'Unit Testing', 'Java'],
    'pytest':           ['Pytest', 'Unit Testing', 'Python'],
    
    # Other Skills
    'api':              ['API Design', 'REST', 'HTTP', 'Integration'],
    'linux':            ['Linux', 'Unix', 'Command Line'],
    'git':              ['Git', 'Version Control', 'GitHub'],
    'agile':            ['Agile', 'Scrum', 'Kanban'],
    'security':         ['Cybersecurity', 'Encryption', 'Authentication'],
    'aws':              ['AWS', 'Cloud', 'Infrastructure'],
}


def extract_skills_from_title(title: str) -> str:
    """Return a comma-separated skill string inferred from cert title."""
    title_lower = title.lower()
    found = set()
    for keyword, skills in CERT_SKILL_MAP.items():
        if keyword in title_lower:
            found.update(skills)
    return ', '.join(sorted(found)) if found else 'General Skills'
