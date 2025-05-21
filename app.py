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
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.strip()

def clean_json_output(output):
    # Remove markdown code fences like ```json or ```
    return re.sub(r"```json|```", "", output.strip())

def extract_name_skill_using_ai(text):
    print("Inside extract_name_skill_using_ai")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )



    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",
        messages=[
            {
                "role": "user",
                "content": f"From the resume text below, extract only: - 'name' (full name) - 'skills': a list of web development skills, including: - Languages (e.g., JavaScript, Python) - Frontend (e.g., React, Next.js) - Backend (e.g., Node.js, Flask) - Databases (e.g., PostgreSQL, MongoDB) - Tools (e.g., Git, Postman, AWS) - Other web tech (e.g., REST APIs, CI/CD) Ignore mobile, AI/ML, payment gateways, soft skills. **Respond ONLY in this strict JSON format:** name and skills as an array, Resume Text: {text}"
            }
        ]
    )

    raw_output = completion.choices[0].message.content
    print("RAW AI RESPONSE:", raw_output)

    cleaned_output = clean_json_output(raw_output)
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
        name_skill_json = extract_name_skill_using_ai(resume_text)

        try:
            parsed_response = json.loads(name_skill_json)
            return jsonify(parsed_response), 200
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse AI response', 'raw_response': name_skill_json}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
