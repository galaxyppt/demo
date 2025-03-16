import os
import re
import PyPDF2
import random

def extract_text_from_file(file_path):
    """Extract text from a file (txt, pdf)."""
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith('.pdf'):
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    else:
        raise ValueError("Unsupported file format. Please provide a .txt or .pdf file.")

def extract_sections(text):
    """Extract relevant sections from the resume text."""
    sections = {
        "Skills": "",
        "Certifications": "",
        "Education Details": "",
        "Work Experience": "",
        "Tools and Technologies": ""
    }

    # Use correct word boundary syntax (\b)
    patterns = {
        "Skills": r"\b(skills|technical skills)\b",
        "Certifications": r"\b(certifications|licenses|certificates)\b",
        "Education Details": r"\b(education|academic background|qualifications)\b",
        "Work Experience": r"\b(experience|work experience|employment history)\b",
        "Tools and Technologies": r"\b(tools|technologies|software|frameworks)\b"
    }

    lines = text.splitlines()
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        for section, pattern in patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                current_section = section
                break
        else:
            if current_section:
                sections[current_section] += line + " "

    for key in sections.keys():
        sections[key] = sections[key].strip()

    return sections

def generate_varied_questions(topic, category):
    """Generate varied questions for a given topic and category."""
    question_templates = {
        "general": [
            "Can you explain your experience with {topic}?",
            "How do you approach {topic} in your work?",
            "What challenges have you faced when working with {topic}?"
        ],
        "application": [
            "Can you describe a project where you used {topic}?",
            "How have you applied {topic} to solve real-world problems?",
            "What strategies do you use when working with {topic}?"
        ],
        "proficiency": [
            "How proficient are you in {topic}?",
            "Can you compare {topic} with other similar technologies?",
            "What are your favorite tools or methods for working with {topic}?"
        ]
    }
    
    if category in question_templates:
        return random.choice(question_templates[category]).format(topic=topic)
    return "Tell me more about {topic}.".format(topic=topic)

def generate_questions(resume_data, job_role):
    """Generates interview questions based on resume data and job role."""
    questions = []
    
    job_role_questions = {
        "Data Analyst": [
            "Describe a time you worked with a large dataset. What was your approach?",
            "What are the most common challenges in data cleaning, and how do you handle them?"
        ],
        "Artificial Intelligence": [
            "Can you walk me through a machine learning project you worked on?",
            "How do you decide which AI model to use for a given problem?"
        ],
        "Software Developer": [
            "How do you handle debugging complex code?",
            "What are your best practices for writing clean and maintainable code?"
        ],
        "UI Designer": [
            "How do you ensure usability in your designs?",
            "What design trends do you follow, and why?"
        ],
        "Web Developer": [
            "Which front-end or back-end technologies do you prefer, and why?",
            "Can you describe a web project where performance optimization was key?"
        ]
    }

    if job_role in job_role_questions:
        questions.extend(job_role_questions[job_role])
    
    # Generate questions from each section of resume data
    for category, content in resume_data.items():
        if content:
            # Split by comma or newline (corrected from '/n' to '\n')
            items = re.split(r',|\n', content)
            for item in items:
                item = item.strip()
                if item:
                    category_type = random.choice(["general", "application", "proficiency"])
                    questions.append(generate_varied_questions(item, category_type))
    
    return questions

def process_resume(file_path, job_role):
    """Process a resume file to extract information and generate interview questions."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    resume_text = extract_text_from_file(file_path)
    extracted_data = extract_sections(resume_text)
    questions = generate_questions(extracted_data, job_role)
    
    return {
        "file_name": os.path.basename(file_path),
        "job_role": job_role,
        "extracted_data": extracted_data,
        "questions": questions
    }

# Example usage:
# result = process_resume("path/to/resume.pdf", "Software Developer")
# print(result)
