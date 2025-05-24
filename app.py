import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
app = Flask(__name__)
CORS(app)
load_dotenv()
SKILLS_SUPERSET = {
    "languages": [
        "JavaScript", "Python", "Java", "C++", "C#", "Ruby", "PHP", "TypeScript", "Go", "Swift", "Kotlin"
    ],
    "frontend": [
        "React", "Vue", "Angular", "Next.js", "Svelte", "HTML", "CSS", "Bootstrap", "Tailwind CSS", "jQuery"
    ],
    "backend": [
        "Node.js", "Express", "Flask", "Django", "Spring", "Laravel", "Ruby on Rails", "ASP.NET", "FastAPI"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Redis", "Cassandra", "MariaDB"
    ],
    "cloud_tools": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible", "CI/CD"
    ],
    "other_web_tech": [
        "REST API", "GraphQL", "WebSocket", "HTTP", "AJAX", "JSON", "XML"
    ],
    "tools": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Postman", "JIRA", "Trello", "VS Code", "Webpack", "NPM", "Yarn"
    ],
    "soft_skills": [
        "Communication", "Teamwork", "Problem Solving", "Leadership", "Time Management", "Adaptability", "Creativity"
    ]
}
def custom_extract_skills(text):
    """
    Extract skills from resume text by matching against a predefined superset of skills.
    Args:
        text (str): The extracted text from the resume.
    Returns:
        dict: A dictionary with categorized skills.
    """
    text_lower = text.lower()
    
    extracted_skills = {
        "name": "",  
        "skills": {
            "languages": [],
            "frontend": [],
            "backend": [],
            "databases": [],
            "cloud_tools": [],
            "other_web_tech": [],
            "tools": [],
            "soft_skills": []
        }
    }
    
    for category, keywords in SKILLS_SUPERSET.items():
        for skill in keywords:
            if skill.lower() in text_lower:
                extracted_skills["skills"][category].append(skill)
    
    return extracted_skills
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.strip()

def clean_json_output(output):
    return re.sub(r"```json|```", "", output.strip())

def extract_name_skill_using_ai(text):
    print("Inside extract_name_skill_using_ai")
    
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API Key not found in environment variables!")
    print("API Key Loaded:", api_key[:10] + "..." if api_key else "None")
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        
    except Exception as e:
        print("Error creating OpenAI client:", str(e))
        raise

    if not client:
        raise ValueError("client not created")
    print("client:", client )

    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",
        # model="deepseek/deepseek-v3-base:free",
        messages=[
            {
                "role": "user",
                "content": f"From the resume text below, extract only: - 'name' (full name) - 'skills': a list of web development skills, including: - Languages (e.g., JavaScript, Python) - Frontend (e.g., React, Next.js) - Backend (e.g., Node.js, Flask) - Databases (e.g., PostgreSQL, MongoDB) - Tools (e.g., Git, Postman, AWS) - Other web tech (e.g., REST APIs, CI/CD) Ignore mobile, AI/ML, payment gateways, soft skills. **Respond ONLY in this strict JSON format nothing extra:** name and skills as an array only not extra key other things, Resume Text: {text}"
            }
        ]
    )
    raw_output = completion.choices[0].message.content

    cleaned_output = clean_json_output(raw_output)
    # cleaned_output = ""
    return cleaned_output

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        resume_text = extract_text_from_pdf(file)
        skills=custom_extract_skills(resume_text)
        try:
            return jsonify(skills), 200
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse AI response', 'raw_response': name_skill_json}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
