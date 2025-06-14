import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup Flask
app = Flask(__name__)
# This should apply CORS to all routes handled by 'app'
CORS(app, origins=["https://alannataylor18.github.io"], allow_headers=["Content-Type", "Authorization"])

# LangChain and Hugging Face setup
# Import inside try block or handle import errors if needed, but usually imports are fine at the top
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings

# Hugging Face API config
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_ENDPOINT_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

# Check for API token early - this should raise an error if missing
# Render's build process might catch this, but good to have
if not HUGGINGFACE_API_TOKEN:
    # Consider returning an error response on the home route instead of raising
    # if you want the server to "run" but indicate config is missing
    print("❌ CRITICAL: HUGGINGFACEHUB_API_TOKEN environment variable is NOT set!")
    # You might want to keep the ValueError if you want the service to fail deployment if missing
    # raise ValueError("Set your HUGGINGFACEHUB_API_TOKEN environment variable!")
    # If you comment out the raise, handle the missing token in the initialization_error below
    initialization_error = "HUGGINGFACEHUB_API_TOKEN environment variable is NOT set!"
else:
    initialization_error = None # Assume no error initially if token is present

# Initialize LLM and Embeddings - Wrapped in try/except for robustness
llm = None
embeddings = None
vectorstore = None
retriever = None
qa = None
# initialization_error = None # Moved initialization_error declaration up

try:
    if initialization_error:
         # If token was missing and we didn't raise, set the error here
         pass # Error is already set above

    else: # Proceed with initialization only if token is present (and no error yet)
        print("Attempting to initialize Hugging Face components...")
        # Initialize LLM
        llm = HuggingFaceEndpoint(
            endpoint_url=HF_ENDPOINT_URL,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
            temperature=0.3,
            model_kwargs={"max_length": 256},
        )
        print("✅ LLM initialized.")

        # Setup embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("✅ Embeddings initialized.")

        # === Load Resume and Build Vectorstore ===
        # IMPORTANT: Verify this path on Render!
        resume_path = os.path.join("static", "RESUME_Taylor Alanna 2025_Tech.pdf")
        abs_path = os.path.abspath(resume_path)
        print("📄 Resume absolute path:", abs_path)

        documents = []
        if os.path.exists(resume_path):
            try:
                loader = PyPDFLoader(resume_path)
                documents = loader.load()
                print(f"✅ Loaded {len(documents)} documents from resume")
            except Exception as e:
                print("❌ Error loading PDF:", e)
                # Continue even if PDF loading fails, but log it
                documents = []
        else:
            print(f"⚠️ Resume not found at: {resume_path}")
            # Continue even if PDF not found
            documents = []

        # Setup Chroma DB
        persist_directory = "./chroma_db"
        if documents and embeddings: # Need embeddings initialized to create vectorstore
             # Only build vectorstore if documents were loaded AND embeddings are available
            vectorstore = Chroma.from_documents(documents, embeddings, persist_directory=persist_directory)
            print("✅ Vectorstore built from documents.")
        else:
            # Create an empty or pre-existing vectorstore if no documents loaded
            # Assuming a pre-existing one might be present from build or previous runs
            if os.path.exists(persist_directory) and embeddings: # Need embeddings to load
                 try:
                    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
                    print("✅ Loaded existing empty/partial vectorstore.")
                 except Exception as e:
                     print(f"⚠️ Could not load existing vectorstore: {e}")
                     vectorstore = None # Ensure it's None if loading fails
            else:
                print("⚠️ No documents loaded, no existing vectorstore found, or embeddings failed.")
                vectorstore = None

        # Setup retriever and QA chain only if vectorstore and llm are available
        if vectorstore and llm:
             retriever = vectorstore.as_retriever()
             qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
             print("✅ RetrievalQA chain initialized.")
        else:
             print("❌ Could not initialize RetrievalQA chain due to missing vectorstore or LLM.")


except Exception as e:
    print(f"❌ CRITICAL Error during application initialization: {e}")
    traceback.print_exc()
    initialization_error = str(e) # Store the error

# === ROUTES ===

@app.route('/chat', methods=['POST'])
def chat():
    # Check if initialization failed
    if initialization_error:
        print(f"❌ Chat request received but application initialization failed: {initialization_error}")
        # Return 500 Internal Server Error if a critical error occurred during startup
        return jsonify({"response": f"Server initialization error: {initialization_error}. Please check server logs."}), 500

    # Check if the QA chain was successfully created
    # This is more specific than checking initialization_error
    if not qa:
         print("❌ Chat request received but QA chain is not available.")
         # Return 503 Service Unavailable if models/vectorstore couldn't be loaded
         return jsonify({"response": "Chat functionality is currently unavailable. Required components failed to load."}), 503

    # If initialization and QA chain are OK, proceed with chat processing
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        print(f"📨 Received message: {user_message}")
        result = qa.invoke({"query": user_message})
        response = result["result"] if isinstance(result, dict) and "result" in result else str(result)
        print(f"✅ Sent response: {response[:100]}...") # Print part of the response
        return jsonify({'response': response})
    except Exception:
        traceback.print_exc()
        # Log specific error for this request
        print("❌ Error processing chat request.")
        # Return 500 Internal Server Error for errors during request processing
        return jsonify({"response": "Error processing your request."}), 500

@app.route("/", methods=["GET"])
def home():
    # You could add a check here to see if initialization_error is set
    # and return a different message or status if the service is degraded
    if initialization_error:
        return f"Resume Chatbot is running, but with initialization errors: {initialization_error}", 500
    elif not qa:
         return "Resume Chatbot is running, but chat functionality is unavailable.", 503
    else:
         return "Resume Chatbot is running and ready."


# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    # When using Gunicorn (as per your Render config), this block is often
    # not the primary way the app is run in production, but it's fine to keep
    # for local testing or as a fallback. Render's Start Command handles the actual launch.
    port = int(os.environ.get("PORT", 5000))
    # Using debug=True in production is NOT recommended for security
    # app.run(host="0.0.0.0", port=port, debug=True)
    app.run(host="0.0.0.0", port=port)