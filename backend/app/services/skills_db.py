"""
Built-in knowledge base used by the offline (no-API-key) analyzer:

* SKILLS          – ~300 common technical and soft skills, grouped by category.
                    Each entry is the display name; ALIASES maps alternative spellings.
* ROLE_SKILLS     – core skills expected for each job role in the dropdown.
* ACTION_VERBS    – strong verbs for rewriting weak resume bullet points.
* WEAK_PHRASES    – weak openings and the action verb to replace them with.
"""

SKILL_CATEGORIES = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "Kotlin",
        "Swift", "Ruby", "PHP", "R", "Scala", "MATLAB", "Perl", "Dart", "Objective-C", "Bash",
        "Shell Scripting", "PowerShell", "SQL", "Lua", "Haskell", "Elixir", "Julia", "Solidity",
        "Assembly", "VBA",
    ],
    "Web Frontend": [
        "HTML", "CSS", "React", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", "Redux",
        "jQuery", "Bootstrap", "Tailwind CSS", "Sass", "Material UI", "Webpack", "Vite", "Babel",
        "Responsive Design", "Web Accessibility", "Three.js", "D3.js", "Gatsby", "Zustand",
        "React Native", "Flutter", "Ionic", "Electron", "Storybook",
    ],
    "Web Backend & APIs": [
        "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot", "Spring",
        "ASP.NET", ".NET", "Laravel", "Ruby on Rails", "NestJS", "REST API", "GraphQL", "gRPC",
        "WebSockets", "Microservices", "OAuth", "JWT", "Hibernate", "Socket.IO", "Celery",
        "RabbitMQ", "Kafka", "Nginx", "Apache", "Serverless", "API Design",
    ],
    "Databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "SQL Server", "Redis", "Cassandra",
        "DynamoDB", "Firebase", "Elasticsearch", "Neo4j", "MariaDB", "Supabase", "Snowflake",
        "BigQuery", "Redshift", "NoSQL", "Database Design", "PL/SQL", "Prisma", "Sequelize",
        "Mongoose",
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins",
        "GitHub Actions", "GitLab CI", "CI/CD", "Linux", "Unix", "Heroku", "Vercel", "Netlify",
        "AWS Lambda", "EC2", "S3", "CloudFormation", "Prometheus", "Grafana", "Helm",
        "Infrastructure as Code", "Load Balancing", "Monitoring", "DevOps", "Site Reliability",
        "Networking", "TCP/IP", "DNS",
    ],
    "Data & Analytics": [
        "Excel", "Advanced Excel", "Power BI", "Tableau", "Looker", "Google Analytics", "Pandas",
        "NumPy", "Matplotlib", "Seaborn", "Plotly", "Jupyter", "Statistics", "Data Analysis",
        "Data Visualization", "Data Cleaning", "Data Mining", "Data Modeling", "Data Warehousing",
        "ETL", "Apache Spark", "Hadoop", "Airflow", "dbt", "A/B Testing", "Hypothesis Testing",
        "Regression Analysis", "Dashboards", "Reporting", "KPI", "SPSS", "SAS", "Google Sheets",
        "Pivot Tables", "VLOOKUP", "Business Intelligence",
    ],
    "AI & Machine Learning": [
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "scikit-learn",
        "NLP", "Computer Vision", "OpenCV", "LLM", "Generative AI", "Prompt Engineering",
        "Hugging Face", "LangChain", "Transformers", "Neural Networks", "CNN", "RNN",
        "Reinforcement Learning", "XGBoost", "Feature Engineering", "Model Deployment", "MLOps",
        "Time Series", "Recommendation Systems", "RAG",
    ],
    "Design": [
        "Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "InDesign", "Canva",
        "UI Design", "UX Design", "User Research", "Wireframing", "Prototyping", "Usability Testing",
        "Design Systems", "Interaction Design", "Visual Design", "Typography", "Information Architecture",
        "User Personas", "Journey Mapping", "Design Thinking", "Motion Design", "After Effects",
        "Mobile Design",
    ],
    "Testing & Quality": [
        "Unit Testing", "Integration Testing", "Jest", "Mocha", "Cypress", "Selenium", "Playwright",
        "PyTest", "JUnit", "Test Automation", "Manual Testing", "TDD", "Postman", "JMeter",
        "Regression Testing", "Bug Tracking",
    ],
    "Security": [
        "Cybersecurity", "Network Security", "Penetration Testing", "Ethical Hacking", "OWASP",
        "Cryptography", "SIEM", "Firewalls", "Vulnerability Assessment", "Wireshark", "Burp Suite",
        "Incident Response", "IAM", "Kali Linux",
    ],
    "Tools & Practices": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello", "Notion",
        "VS Code", "Agile", "Scrum", "Kanban", "SDLC", "OOP", "Data Structures", "Algorithms",
        "Design Patterns", "System Design", "Debugging", "Code Review", "Version Control",
        "Software Architecture", "Documentation", "SEO", "WordPress", "Shopify", "Salesforce",
        "SAP", "Blockchain", "IoT", "Arduino", "Raspberry Pi", "Android", "iOS", "Unity",
        "Product Management", "Project Management", "Requirements Gathering", "Stakeholder Management",
        "Roadmapping", "Market Research", "Digital Marketing",
    ],
    "Soft Skills": [
        "Communication", "Teamwork", "Leadership", "Problem Solving", "Critical Thinking",
        "Time Management", "Adaptability", "Creativity", "Collaboration", "Attention to Detail",
        "Analytical Skills", "Presentation Skills", "Negotiation", "Conflict Resolution",
        "Decision Making", "Mentoring", "Public Speaking", "Customer Service", "Self-Motivated",
        "Work Ethic", "Emotional Intelligence", "Organizational Skills", "Interpersonal Skills",
        "Multitasking", "Strategic Thinking", "Cross-functional Collaboration",
    ],
}

# Flat list of every skill (display names)
SKILLS = [s for group in SKILL_CATEGORIES.values() for s in group]

# Alternative spellings -> canonical skill name. Matching is case-insensitive.
ALIASES = {
    "js": "JavaScript", "es6": "JavaScript", "ts": "TypeScript", "golang": "Go",
    "reactjs": "React", "react.js": "React", "angularjs": "Angular", "vue": "Vue.js", "vuejs": "Vue.js",
    "nextjs": "Next.js", "nodejs": "Node.js", "node": "Node.js", "express": "Express.js",
    "expressjs": "Express.js", "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "html5": "HTML", "css3": "CSS", "scss": "Sass", "mui": "Material UI",
    "postgres": "PostgreSQL", "mongo": "MongoDB", "mssql": "SQL Server", "gcp": "Google Cloud",
    "google cloud platform": "Google Cloud", "amazon web services": "AWS", "microsoft azure": "Azure",
    "k8s": "Kubernetes", "ci cd": "CI/CD", "continuous integration": "CI/CD",
    "restful": "REST API", "rest apis": "REST API", "restful api": "REST API", "restful apis": "REST API",
    "ms excel": "Excel", "microsoft excel": "Excel", "powerbi": "Power BI",
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn", "ml": "Machine Learning",
    "dl": "Deep Learning", "natural language processing": "NLP", "genai": "Generative AI",
    "large language models": "LLM", "llms": "LLM", "spark": "Apache Spark", "pyspark": "Apache Spark",
    "user experience": "UX Design", "user interface": "UI Design",
    "wireframes": "Wireframing", "prototypes": "Prototyping", "usability": "Usability Testing",
    "object oriented programming": "OOP", "object-oriented programming": "OOP",
    "dsa": "Data Structures", "github actions": "GitHub Actions", "shell": "Shell Scripting",
    "team player": "Teamwork", "problem-solving": "Problem Solving", "time-management": "Time Management",
    "a/b tests": "A/B Testing", "ab testing": "A/B Testing", "visualization": "Data Visualization",
    "data visualisation": "Data Visualization", "springboot": "Spring Boot", "dotnet": ".NET",
    "asp.net core": "ASP.NET", "tensorflow.js": "TensorFlow", "huggingface": "Hugging Face",
    "retrieval augmented generation": "RAG", "power query": "Power BI", "dax": "Power BI",
    "statistical analysis": "Statistics", "google data studio": "Looker", "looker studio": "Looker",
    "pivot table": "Pivot Tables", "unit tests": "Unit Testing", "pytest": "PyTest",
    "agile methodologies": "Agile", "scrum master": "Scrum", "cross functional": "Cross-functional Collaboration",
}

# Skills that are short / ambiguous words: only match them case-sensitively in the
# original text to avoid false positives (e.g. "R", "C", "Go", "Swift").
CASE_SENSITIVE_SKILLS = {"R", "C", "Go", "Swift", "Rust", "Dart", "Julia", "Spring", "Unity",
                         "Apache", "Excel", "Ionic", "SAS", "KPI", "IAM", "RAG", "Lua", "S3", "EC2",
                         "dbt", "Helm", "Sketch", "Canva"}

# Core skills used when the job description itself lists very few skills
ROLE_SKILLS = {
    "Software Developer": ["Python", "Java", "JavaScript", "Git", "SQL", "Data Structures", "Algorithms",
                           "OOP", "REST API", "Unit Testing", "Agile", "Problem Solving"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Responsive Design",
                           "Redux", "Git", "REST API", "Web Accessibility", "Jest", "Figma"],
    "Backend Developer": ["Python", "Java", "Node.js", "SQL", "PostgreSQL", "REST API", "Docker",
                          "Microservices", "Redis", "Git", "Unit Testing", "System Design"],
    "Full Stack Developer": ["JavaScript", "TypeScript", "React", "Node.js", "Express.js", "MongoDB",
                             "SQL", "REST API", "Git", "Docker", "HTML", "CSS"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Responsive Design", "Git",
                      "REST API", "MySQL", "SEO", "WordPress", "Bootstrap"],
    "Data Analyst": ["SQL", "Excel", "Python", "Power BI", "Tableau", "Statistics", "Data Visualization",
                     "Data Cleaning", "Pandas", "Dashboards", "Reporting", "Communication"],
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "Pandas", "NumPy", "scikit-learn",
                       "SQL", "Deep Learning", "Data Visualization", "Feature Engineering", "TensorFlow",
                       "Jupyter"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
                                  "MLOps", "Docker", "Model Deployment", "NLP", "AWS", "SQL", "Git"],
    "DevOps Engineer": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Jenkins",
                        "Ansible", "Bash", "Monitoring", "Git", "Networking"],
    "Cloud Engineer": ["AWS", "Azure", "Google Cloud", "Terraform", "Docker", "Kubernetes", "Linux",
                       "Networking", "Serverless", "CI/CD", "IAM", "Python"],
    "Mobile App Developer": ["Android", "iOS", "Kotlin", "Swift", "Flutter", "React Native", "Dart",
                             "Firebase", "REST API", "Git", "Mobile Design", "Unit Testing"],
    "UI/UX Designer": ["Figma", "Adobe XD", "User Research", "Wireframing", "Prototyping", "UI Design",
                       "UX Design", "Usability Testing", "Design Systems", "Typography",
                       "Interaction Design", "Communication"],
    "QA / Test Engineer": ["Manual Testing", "Test Automation", "Selenium", "Cypress", "Postman",
                           "Regression Testing", "Jira", "SQL", "Python", "Java", "Bug Tracking", "Agile"],
    "Cybersecurity Analyst": ["Cybersecurity", "Network Security", "SIEM", "Penetration Testing",
                              "Vulnerability Assessment", "Firewalls", "Linux", "Wireshark",
                              "Incident Response", "OWASP", "Python", "Networking"],
    "Product Manager": ["Product Management", "Roadmapping", "Agile", "Scrum", "Jira", "User Research",
                        "Stakeholder Management", "Data Analysis", "Market Research", "Communication",
                        "Leadership", "A/B Testing"],
    "Business Analyst": ["Requirements Gathering", "SQL", "Excel", "Power BI", "Stakeholder Management",
                         "Data Analysis", "Documentation", "Agile", "Jira", "Communication",
                         "Problem Solving", "Reporting"],
}

ACTION_VERBS = [
    "Achieved", "Architected", "Automated", "Built", "Collaborated", "Created", "Delivered", "Designed",
    "Developed", "Drove", "Engineered", "Enhanced", "Implemented", "Improved", "Increased", "Launched",
    "Led", "Managed", "Mentored", "Optimized", "Orchestrated", "Reduced", "Redesigned", "Resolved",
    "Spearheaded", "Streamlined", "Analyzed", "Deployed", "Integrated", "Migrated", "Presented",
    "Researched", "Tested", "Trained", "Coordinated", "Established", "Generated", "Executed",
]

# Weak bullet openings (lower-case regex) -> stronger replacement verb
WEAK_PHRASES = [
    (r"^responsible for (managing|handling)\s+", "Managed "),
    (r"^responsible for (developing|building|creating)\s+", "Developed "),
    (r"^responsible for\s+", "Owned "),
    (r"^worked on (developing|building)\s+", "Built "),
    (r"^worked on\s+", "Developed "),
    (r"^worked with\s+", "Collaborated with "),
    (r"^helped (to )?(build|develop|create)\s+", "Co-developed "),
    (r"^helped (to )?\s*", "Supported "),
    (r"^assisted (in|with)\s+", "Contributed to "),
    (r"^was involved in\s+", "Contributed to "),
    (r"^involved in\s+", "Contributed to "),
    (r"^participated in\s+", "Contributed to "),
    (r"^tasked with\s+", "Executed "),
    (r"^did\s+", "Performed "),
    (r"^made\s+", "Created "),
    (r"^handled\s+", "Managed "),
    (r"^in charge of\s+", "Led "),
    (r"^duties included\s+", "Performed "),
]
