@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    print("User message received:", user_message)

    if not user_message:
        return jsonify({'response': 'No message received.'})

    try:
        # Load PDF content
        loader = PyPDFLoader("Resume_A_Taylor.pdf")
        documents = loader.load()
        print("Loaded documents:", documents[:1])  # Show a preview of docs

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        print("Split into", len(texts), "chunks")

        # Embed and store
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)
        print("Chroma vector store created")

        # Set up retriever and QA chain
        retriever = db.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(model_name="gpt-3.5-turbo"), retriever=retriever)
        print("QA chain ready")

        # Run QA
        response = qa.run(user_message)
        print("Bot response:", response)

        return jsonify({'response': response})
    except Exception as e:
        print("Error during processing:", str(e))
        return jsonify({'response': 'Error processing your request.'})