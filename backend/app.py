import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup Flask
app = Flask(__name__)
CORS(app, origins=["https://alannataylor18.github.io"], allow_headers=["Content-Type", "Authorization"])

# LangChain and Hugging Face setup
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings

# Hugging Face API config
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_ENDPOINT_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

if not HUGGINGFACE_API_TOKEN:
    raise ValueError("Set your HUGGINGFACEHUB_API_TOKEN environment variable!")

# Initialize LLM
llm = HuggingFaceEndpoint(
    endpoint_url=HF_ENDPOINT_URL,
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    temperature=0.3,
    model_kwargs={"max_length": 256},
)

# === Load Resume and Build Vectorstore ===
resume_path = os.path.join("static", "RESUME_Taylor Alanna 2025_Tech.pdf")
abs_path = os.path.abspath(resume_path)
print("📄 Resume absolute path:", abs_path)

documents = []
try:
    if os.path.exists(resume_path):
        loader = PyPDFLoader(resume_path)
        documents = loader.load()
        print(f"✅ Loaded {len(documents)} documents from resume")
    else:
        print(f"⚠️ Resume not found at: {resume_path}")
except Exception as e:
    print("❌ Error loading PDF:", e)
    documents = []

# Setup embeddings and Chroma DB
persist_directory = "./chroma_db"
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

if documents:
    vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
else:
    # Prevent crash if PDF failed — create empty retriever
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# === ROUTES ===
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        print(f"📨 Received message: {user_message}")
        result = qa.invoke({"query": user_message})
        response = result["result"] if isinstance(result, dict) and "result" in result else str(result)
        return jsonify({'response': response})
    except Exception:
        traceback.print_exc()
        return jsonify({"response": "Error processing your request."})

@app.route("/", methods=["GET"])
def home():
    return "Resume Chatbot is running!"

# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)