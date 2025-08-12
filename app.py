from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI

from pdf_utils import extract_text_from_pdf, create_pdf_from_text

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5000",
                "https://resume-shortner.onrender.com/",  # Add your Render URL
            ]
        }
    },
)
load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4.1"

client = OpenAI(base_url=endpoint, api_key=token)

def compress_resume_with_ai(content):
    """Use AI to compress resume content for single page"""
    
    prompt = f"""
    Convert this multi-page resume into a concise single-page format. Keep only the most important information.
    Make it professional and ATS-friendly. Output as plain text with clear sections.

    ORIGINAL RESUME:
    {content}

    FORMAT THE OUTPUT AS:
    NAME
    Contact Info (email, phone, location)

    OBJECTIVE (if relevant, 1-2 lines max)

    EDUCATION
    - Degree, University, Year, GPA (if notable)

    TECHNICAL SKILLS
    - Languages: 
    - Frameworks:
    - Tools:

    EXPERIENCE (most recent/relevant only)
    - Job Title | Company | Duration
      • Key achievement with metrics
      • Another achievement

    PROJECTS (top 2-3 only)
    - Project Name | Technologies
      • Key feature/impact

    ACHIEVEMENTS
    - Award/certification with context

    Keep it under 600 words total. Be ruthless about cutting fluff. Make sure to just have the format and nothing else, please re-check if its exactly like the format and nothing else in the response.
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert resume writer who creates impactful single-page resumes."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            top_p=1.0,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI compression error: {e}")
        return content[:1000] + "..."  # Fallback


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_resume():
    # try:
    if 'resume' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['resume']
    
    if file.filename == '':
        return "No file selected", 400
        
    # Extract text from PDF
    content = extract_text_from_pdf(file)
    
    if not content.strip():
        return "Could not extract text from PDF", 400
    
    # Compress with AI
    compressed_text = compress_resume_with_ai(content)
    
    # Create new PDF
    pdf_buffer = create_pdf_from_text(compressed_text)
    
    # Return PDF
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='converted_resume.pdf',
        mimetype='application/pdf'
    )
        
    # except Exception as e:
    #     return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)