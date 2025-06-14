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
    raise ValueError("Set your HUGGINGFACEHUB_API_TOKEN environment variable!")

# Initialize HuggingFace LLM endpoint
llm = HuggingFaceEndpoint(
    endpoint_url=HF_ENDPOINT_URL,
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    model_kwargs={"max_length": 256, "temperature": 0.3},
)

# Set the path to your PDF resume relative to this script
resume_path = "./static/RESUME_Taylor Alanna 2025_Tech.pdf"

# Debug: print absolute path and check existence
print("Resume absolute path:", os.path.abspath(resume_path))
print("Resume exists:", os.path.exists(resume_path))

# Load documents from PDF
try:
    loader = PyPDFLoader(resume_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from resume")
except Exception as e:
    print("Error loading PDF:", e)
    documents = []

# Setup embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "./chroma_db"

vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)

retriever = vectorstore.as_retriever()

# Setup RetrievalQA chain
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

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
        print("❌ Error occurred:")
        traceback.print_exc()
        return jsonify({"response": "Error processing your request."})

@app.route("/", methods=["GET"])
def home():
    return "Resume Chatbot is running!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)