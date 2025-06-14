import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# Flask app initialization
app = Flask(__name__)

# Setup CORS to allow your GitHub Pages front-end only
CORS(app, origins=["https://alannataylor18.github.io"], allow_headers=["Content-Type", "Authorization"])

# Import langchain after Flask and CORS setup
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

# Load Hugging Face API token from environment variable
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_ENDPOINT_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

if not HUGGINGFACE_API_TOKEN:
    raise ValueError("❌ Set your HUGGINGFACEHUB_API_TOKEN environment variable!")

# Initialize HuggingFace LLM endpoint
llm = HuggingFaceEndpoint(
    endpoint_url=HF_ENDPOINT_URL,
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    temperature=0.3,
    model_kwargs={"max_length": 256},
)

# Set the path to your PDF resume
resume_path = os.path.join("static", "RESUME_Taylor Alanna 2025_Tech.pdf")
abs_path = os.path.abspath(resume_path)
print("📄 Resume absolute path:", abs_path)
print("📄 Resume exists:", os.path.exists(resume_path))

# Setup embeddings and vectorstore
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "./chroma_db"
vectorstore = None

# Load resume if available
documents = []
if os.path.exists(resume_path):
    try:
        loader = PyPDFLoader(resume_path)
        documents = loader.load()
        print(f"✅ Loaded {len(documents)} documents from resume")

        if documents:
            print("📌 Creating Chroma vectorstore from resume...")
            vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
        else:
            print("⚠️ Resume loaded but no content extracted.")

    except Exception as e:
        print("❌ Error loading or parsing resume PDF:", e)
else:
    print("⚠️ Resume file not found at:", abs_path)

# Stop app if no vectorstore could be built
if not vectorstore:
    raise RuntimeError("❌ Failed to create vectorstore. Make sure your resume is accessible and non-empty.")

# Create retriever
retriever = vectorstore.as_retriever()

# Setup RetrievalQA chain
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        print(f"📨 Received message: {user_message}")
        result = qa.invoke({"query": user_message})
        print(f"🤖 QA result: {result}")

        if isinstance(result, dict) and "result" in result:
            response = result["result"]
        else:
            response = str(result)

        return jsonify({'response': response})
    except Exception:
        print("❌ Error occurred during query processing:")
        traceback.print_exc()
        return jsonify({"response": "Error processing your request."})

# Home route
@app.route("/", methods=["GET"])
def home():
    return "Resume Chatbot is running!"

# Start the server
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)