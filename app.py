import os
from flask import Flask, request, jsonify

# Use langchain_huggingface to avoid deprecation warnings
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

import os

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_ENDPOINT_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

if not HUGGINGFACE_API_TOKEN:
    raise ValueError("Set your HUGGINGFACEHUB_API_TOKEN environment variable!")

# Initialize the LLM (remote model inference endpoint)
llm = HuggingFaceEndpoint(
    endpoint_url=HF_ENDPOINT_URL,
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    model_kwargs={"max_length": 512},
)

# Load documents (PDF resume)
resume_path = "./static/RESUME_Taylor Alanna 2025_Tech.pdf"
loader = PyPDFLoader(resume_path)
documents = loader.load()
print(f"Loaded {len(documents)} documents")

# Setup embeddings model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Create vectorstore (Chroma) from documents
persist_directory = "./chroma_db"
vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
# No need to call persist() manually with recent Chroma versions

# Create retriever
retriever = vectorstore.as_retriever()

# Setup RetrievalQA chain
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Initialize Flask app
app = Flask(__name__)

import traceback

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        print(f"📨 Received message: {user_message}")  # New log
        result = qa.invoke({"query": user_message})
        print(f"🤖 QA result: {result}")  # New log

        if isinstance(result, dict) and "result" in result:
            response = result["result"]
        else:
            response = str(result)

        return jsonify({'response': response})
    except Exception as e:
        print("❌ Error occurred:")
        traceback.print_exc()
        return jsonify({"response": "Error processing your request."})


@app.route("/", methods=["GET"])
def home():
    return "Resume Chatbot is running!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)