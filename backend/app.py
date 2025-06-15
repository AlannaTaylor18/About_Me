from flask import Flask, request, jsonify
import pdfplumber
import os
from flask_cors import CORS
from transformers import pipeline

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Load the QA pipeline once, on startup (not per request)
qa_pipeline = pipeline("question-answering", model="deepset/tinyroberta-squad2")

def extract_text_from_pdf(pdf_path, max_pages=2):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= max_pages:
                break
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

@app.route("/", methods=["GET"])
def home():
    return '''
    <h2>Upload PDF and Ask a Question</h2>
    <form method="post" enctype="multipart/form-data" action="/chat">
      PDF file: <input type="file" name="pdf" accept="application/pdf"><br><br>
      Question: <input type="text" name="question" style="width:300px"><br><br>
      <input type="submit" value="Ask">
    </form>
    '''

@app.route("/chat-json", methods=["POST"])
def chat_json():
    try:
        data = request.get_json()
        question = data.get("message")
        if not question:
            return jsonify({"reply": "Please enter a question."}), 400

        # Use static resume-like context instead of PDF
        context = (
            "Alanna Taylor is a tech-savvy professional skilled in Python, "
            "web development, and machine learning. She has experience with "
            "Flask, IBM Watson APIs, and GitHub Pages."
        )

        context = " ".join(context.split()[:500])
        result = qa_pipeline(question=question, context=context)
        return jsonify({"reply": result.get("answer", "No answer found.")})

    except Exception as e:
        return jsonify({"reply": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)