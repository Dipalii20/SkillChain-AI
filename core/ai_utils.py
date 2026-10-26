import re

# A transparent baseline skill extractor. Extend this list for your own use case.
SKILLS = [
    "python", "java", "javascript", "html", "css", "bootstrap", "django",
    "flask", "sql", "mysql", "postgresql", "git", "github", "machine learning",
    "scikit-learn", "pandas", "numpy", "data analysis", "solidity", "blockchain",
    "web3.py", "react", "spring boot", "rest api", "communication", "excel",
    "c++", "c", "problem solving", "linux", "docker"
]

ALIASES = {
    "web3.py": ["web3.py", "web3"],
    "machine learning": ["machine learning", "ml"],
    "rest api": ["rest api", "restful api"],
    "spring boot": ["spring boot"],
}

def extract_skills(text):
    lower = re.sub(r"\s+", " ", text.lower())
    found = []
    for skill in SKILLS:
        patterns = ALIASES.get(skill, [skill])
        for phrase in patterns:
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", lower):
                found.append(skill)
                break
    return sorted(set(found))

def match_score(student_skills, required_skills):
    required = {s.strip().lower() for s in required_skills.split(",") if s.strip()}
    student = {s.strip().lower() for s in student_skills if s.strip()}
    if not required:
        return 0, [], []
    matched = sorted(required & student)
    missing = sorted(required - student)
    return round(100 * len(matched) / len(required)), matched, missing
