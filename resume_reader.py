import requests
import fitz  # PyMuPDF

def extract_resume_text(pdf_url):
    response = requests.get(pdf_url)
    with open("files/RESUME_Taylor Alanna 2025_Tech.pdf", "wb") as f:
        f.write(response.content)

    doc = fitz.open("files/RESUME_Taylor Alanna 2025_Tech.pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if __name__ == "__main__":
    pdf_url = "https://raw.githubusercontent.com/AlannaTaylor18/About_Me/main/AlannaTaylor_Resume_2024.pdf"
    resume_text = extract_resume_text(pdf_url)
    print(resume_text)
