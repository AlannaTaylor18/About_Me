from flask import Flask, request, jsonify
import os

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

app = Flask(__name__)

# ========== Load and Process PDF Once ==========
resume_path = os.path.join(os.path.dirname(__file__), "Resume_A_Taylor.pdf")
loader = PyPDFLoader(resume_path)
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(chunks, embeddings)

retriever = db.as_retriever()
qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(model_name="gpt-3.5-turbo"), retriever=retriever)

# ========== API Route ==========
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        response = qa.run(user_message)
        return jsonify({'response': response})
    except Exception as e:
        print("Error during processing:", str(e))
        return jsonify({'response': 'Error processing your request.'})


# ========== Start Server ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)