import os
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

qa = None  # Global variable to store the chain

def initialize_qa():
    global qa
    if qa is None:
        loader = PyPDFLoader("static/Alanna_Taylor_Resume.pdf")
        documents = loader.load()
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Flask app setup
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, origins=["https://alannataylor18.github.io"])

# Global variables to be initialized later
qa = None

@app.before_first_request
def setup():
    global qa

    print("🔧 Initializing Hugging Face + LangChain setup...")

    # Load env vars
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL", "https://api-inference.huggingface.co/models/google/flan-t5-base")

    if not HUGGINGFACE_API_TOKEN:
        raise ValueError("❌ HUGGINGFACE_API_TOKEN is not set!")

    # Load PDF
    resume_path = "static/Alanna_Taylor_Resume.pdf"
    loader = PyPDFLoader(resume_path)
    documents = loader.load()
    print(f"📄 Loaded {len(documents)} documents")

    # Setup LLM and retriever
    llm = HuggingFaceEndpoint(
        endpoint_url=HF_ENDPOINT_URL,
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        model_kwargs={"max_length": 512},
    )

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    print("✅ QA system ready")

@app.route('/chat', methods=['POST'])
def chat():
    global qa

    if qa is None:
        return jsonify({"response": "Server not ready. Please try again in a few seconds."})

    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        result = qa.invoke({"query": user_message})
        response = result.get("result", "No response found.")
        return jsonify({'response': response})
    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()
        return jsonify({"response": "Server error."})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)