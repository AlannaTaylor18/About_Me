import openai
import os
openai.api_key = os.getenv("HRKU-AAAJB02PkglwW9bmx4OzJtHBstGFt_TVup8s9DpVnCsg_____waHx_synQFI")

from flask import Flask, render_template, request, jsonify
import requests
import PyPDF2
from io import BytesIO

app = Flask(__name__)

RESUME_URL = "https://github.com/AlannaTaylor18/About_Me/raw/main/files/RESUME_Taylor%20Alanna%202025_Tech.pdf"

def extract_resume_text(url):
    response = requests.get(url)
    pdf_file = BytesIO(response.content)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

resume_text = extract_resume_text(RESUME_URL)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    if "skills" in user_input.lower():
        answer = "Here are some key skills from my resume: " + ", ".join(
            [word for word in resume_text.split() if word.istitle()][:10]
        )
    else:
        answer = "Let me review your question and get back to you."

    return jsonify({"reply": answer})

if __name__ == "__main__":
    print("Starting Flask app...")  # Added print statement
    app.run(debug=True)