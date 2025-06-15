from flask import Flask, request, jsonify
from transformers import pipeline
import pdfplumber
import os

app = Flask(__name__)
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf")
        question = request.form.get("question")
        if not file or not question:
            return jsonify({"error": "Please upload a PDF and ask a question."}), 400

        pdf_path = "temp.pdf"
        file.save(pdf_path)

        try:
            context = extract_text_from_pdf(pdf_path)
            if not context.strip():
                return jsonify({"error": "Could not extract text from PDF."}), 400

            result = qa_pipeline(question=question, context=context)
            return jsonify({"answer": result["answer"]})
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    return '''
    <h2>Upload PDF and Ask a Question</h2>
    <form method="post" enctype="multipart/form-data">
      PDF file: <input type="file" name="pdf" accept="application/pdf"><br><br>
      Question: <input type="text" name="question" style="width:300px"><br><br>
      <input type="submit" value="Ask">
    </form>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)