import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Default skill list
DEFAULT_SKILLS = [
    "python", "java", "c++", "c#", "html", "css", "javascript",
    "react", "vue", "angular", "node", "express", "sql", "mongodb",
    "machine learning", "flask", "django", "aws", "docker", "kubernetes",
    "git", "rest api", "graphql", "typescript", "go", "rust", "fastapi",
    "postgresql", "mysql", "firebase", "redis", "elasticsearch",
    "agile", "scrum", "jira", "linux", "windows", "macos"
]

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text.lower()

def find_skills_in_text(text, skills_list=None):
    """Find skills in text from a given skill list"""
    if skills_list is None:
        skills_list = DEFAULT_SKILLS
    
    found_skills = []
    
    for skill in skills_list:
        # Use word boundary matching for better accuracy
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates

def calculate_tfidf_similarity(text1, text2):
    """Calculate TF-IDF based similarity between two texts using cosine similarity"""
    try:
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Combine texts to fit the vectorizer
        texts = [text1, text2]
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(similarity * 100, 2)
    except:
        return 0

def analyze_resume(text, required_skills=None, job_description=None):
    """
    Analyze resume and return comprehensive analysis
    
    Returns:
        tuple: (found_skills, match_score, matched_skills, unmatched_skills, job_match_score)
    """
    found_skills = find_skills_in_text(text, DEFAULT_SKILLS)
    
    # Calculate job description match if provided
    job_match_score = 0
    if job_description:
        job_match_score = calculate_tfidf_similarity(text, job_description)
    
    if required_skills is None or len(required_skills) == 0:
        # If no required skills, use default scoring
        score = (len(found_skills) / len(DEFAULT_SKILLS)) * 100
        return found_skills, round(score, 2), [], [], job_match_score
    else:
        # Calculate match based on required skills
        required_skills_lower = [s.lower() for s in required_skills]
        matched_skills = [skill for skill in found_skills if skill.lower() in required_skills_lower]
        
        match_score = (len(matched_skills) / len(required_skills)) * 100
        unmatched_skills = [s for s in required_skills if s.lower() not in [m.lower() for m in matched_skills]]
        
        return found_skills, round(match_score, 2), matched_skills, unmatched_skills, job_match_score

def get_skill_categories(skills):
    """Categorize skills into different categories"""
    categories = {
        "Programming Languages": ["python", "java", "c++", "c#", "javascript", "typescript", "go", "rust"],
        "Frontend": ["html", "css", "react", "vue", "angular"],
        "Backend": ["node", "express", "flask", "django", "fastapi"],
        "Databases": ["sql", "mongodb", "postgresql", "mysql", "firebase", "redis", "elasticsearch"],
        "Cloud & DevOps": ["aws", "docker", "kubernetes", "azure", "gcp"],
        "Other": []
    }
    
    categorized = {cat: [] for cat in categories}
    
    for skill in skills:
        found = False
        for cat, skill_list in categories.items():
            if cat != "Other" and skill.lower() in [s.lower() for s in skill_list]:
                categorized[cat].append(skill)
                found = True
                break
        if not found:
            categorized["Other"].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}