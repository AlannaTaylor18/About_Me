import os
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Import your LLM and vectorstore classes here
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA

# Create the Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, origins=["https://alannataylor18.github.io"])

# Global variables for your LLM and QA system
llm = None
qa = None

def setup_qa_chain():
    global llm, qa

    if llm is not None and qa is not None:
        return  # Already initialized

    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    HF_ENDPOINT_URL = os.getenv(
        "HF_ENDPOINT_URL", 
        "https://api-inference.huggingface.co/models/google/flan-t5-base"
    )

    if not HUGGINGFACE_API_TOKEN:
        raise ValueError("Set your HUGGINGFACE_API_TOKEN environment variable!")

    print("Checking resume file existence...")
    resume_path = "static/Alanna_Taylor_Resume.pdf"
    print("Absolute path:", os.path.abspath(resume_path))
    print("File exists:", os.path.isfile(resume_path))

    loader = PyPDFLoader(resume_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever()

    llm = HuggingFaceEndpoint(
        endpoint_url=HF_ENDPOINT_URL,
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        model_kwargs={"max_length": 512},
    )

    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    print("✅ QA system ready")

@app.route('/chat', methods=['POST'])
def chat():
    global qa
    if qa is None:
        setup_qa_chain()

    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': '⚠️ No message provided.'}), 400

    try:
        result = qa.invoke({"query": user_message})
        response = result.get("result", "🤖 No answer found.")
        return jsonify({'response': response}), 200
    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()
        return jsonify({"response": "❌ Server error. Please try again later."}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)