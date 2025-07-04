rom flask import Flask, request, jsonify
import os
from flask_cors import CORS
from transformers import pipeline

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load the QA pipeline once on startup
qa_pipeline = pipeline("question-answering", model="deepset/tinyroberta-squad2")

# Your full resume as a multiline string:
resume_text = """
Stuart, Florida  
Alanna Taylor  
(772) 626-4475  
AlannaTaylor@live.com  
https://alannataylor18.github.io/About_Me/  
https://www.linkedin.com/in/pivoting2tech/

Enthusiastic and results-driven professional transitioning into technology from a background in education. Completed IBM’s Applied AI Developer certification with hands-on experience in Python, machine learning, REST APIs, and IBM Cloud. Currently pursuing an engineering certificate to deepen technical expertise. Demonstrated success in data analysis, workflow optimization, LMS management, Excel-based reporting, and technical troubleshooting in a fully remote environment. Eager to contribute to innovative teams solving real-world challenges with scalable, user-focused solutions.

Experience  
DARWIN GLOBAL LLC (REMOTE)  
Lead Academic Coach — JUNE 2021 - PRESENT  
● Manage and mentor a remote team of Academic Coaches using real-time performance dashboards and KPIs.  
● Perform data extraction and analysis from LMS to generate weekly performance and engagement reports using Excel (PivotTables, formulas).  
● Troubleshoot and resolve LMS and workflow system issues; often serve as liaison with IT for backend fixes.  
● Built custom workflows to streamline academic intervention processes, reducing student resolution time by 30%.  
● Collaborate cross-functionally with stakeholders (Product, IT, Student Services) to enhance platform functionality and data integrity.

Academic Coach — 2016-2021  
● Supported 400+ adult learners by analyzing performance data and implementing interventions that improved course completion.  
● Acted as Tier 1 tech support for platform and account issues; resolved 90% of issues without escalation.  
● Maintained accurate student records in alignment with accreditation/FERPA standards, ensuring data integrity and accountability.  
● Maintained FERPA-compliant student records and processed over $1.5M in financial aid awards.  
● Delivered career development webinars and academic coaching sessions, enhancing student outcomes.

LOGISTICS HEALTH  
Administrative Intake Personnel (PER DIEM) — 2008-2016  
● Managed logistics for military healthcare events serving 300+ participants; streamlined documentation and reduced wait times by 20%.

Education  
Bachelor of Science, Indian River State College - Fort Pierce, Florida  
Exceptional Student Education with Reading and ESOL Endorsement

Skills & Certifications  
● IBM Applied AI Developer (IBM, 2025)  
Completed 7-course specialization with hands-on projects in Python, machine learning, REST APIs, and IBM Cloud.  
edX Verified Certificates: AI for Everyone, Introduction to Generative AI, Prompt Engineering, Developing Generative AI Applications with Python, Python for AI & Development Project

● Programming & Tools: Python, Jupyter Notebooks, IBM Watson, REST APIs, Git/GitHub, VS Code, JSON  
● Cloud & AI Platforms: IBM Cloud, Watson NLP, Watson Assistant, Watson Studios  
● Software: Microsoft Office, Google Suite, Five9 Dialer, Reporting & Analytics tools  
● Data & Troubleshooting: Data analytics, LMS systems, FERPA compliance, ticketing systems  
● Other Tools: Excel, Google Workspace, Microsoft Teams, Zoom, Canvas LMS, Blackboard, Salesforce  
● Soft Skills: Excellent communication & documentation, tech troubleshooting, training & coaching, remote collaboration
"""

@app.route("/", methods=["GET"])
def home():
    return "Chatbot is running. POST to /chat with a question."

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        question = data.get("message")
        if not question:
            return jsonify({"reply": "Please enter a question."}), 400

        # Use the resume text as the context for QA
        result = qa_pipeline(question=question, context=resume_text)
        answer = result.get("answer", "Sorry, I don't have an answer for that.")

        return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"reply": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)