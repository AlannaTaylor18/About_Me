from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import traceback

# Flask setup
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, origins=["https://alannataylor18.github.io"])

# LangChain & Hugging Face imports
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

# Hugging Face config
huggingface_token = os.getenv("HUGGINGFACE_API_TOKEN")
HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL") or "https://api-inference.huggingface.co/models/google/flan-t5-base"

if not huggingface_token:
    raise ValueError("Set your HUGGINGFACE_API_TOKEN environment variable!")

# Initialize the LLM once
llm = HuggingFaceEndpoint(
    endpoint_url=HF_ENDPOINT_URL,
    huggingfacehub_api_token=huggingface_token,
    model_kwargs={"max_length": 512},
)

# Load resume PDF once
resume_path = "static/Alanna_Taylor_Resume.pdf"
print("Checking resume file existence...")
print("Absolute path:", os.path.abspath(resume_path))
print("File exists:", os.path.isfile(resume_path))

loader = PyPDFLoader(resume_path)
documents = loader.load()
print(f"Loaded {len(documents)} documents")

# Set up embeddings, vectorstore, and RetrievalQA chain
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        print(f"📨 Message received: {user_message}")

        # Uncomment for debugging echo:
        # return jsonify({'response': f'You said: {user_message}'})

        result = qa.invoke({"query": user_message})
        print(f"🤖 Result: {result}")

        response = result.get("result", "No response found.")
        return jsonify({'response': response})

    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()
        return jsonify({"response": "Server error"})

# Home route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
