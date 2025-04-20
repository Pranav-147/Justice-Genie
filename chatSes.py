from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os
import uuid

from langchain_community.embeddings import OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)
CORS(app)

os.environ["GOOGLE_API_KEY"] = "AIzaSyC9O_P4M9OFdofX5pl9Dzk0dSvBiD8dH9A"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def ollama_llm(question, context):
    llm = Ollama(model="llama3.2")
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context, question=question)
    print(prompt)
    response_text = llm.invoke(prompt)
    return response_text

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)
    
    print("question",user_question)

    response = ollama_llm(user_question, docs)

    return response



@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    session_id = data.get('session_id')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    response = user_input(question)
    return jsonify({"response": response, "session_id": session_id}), 200


@app.route('/new_chat', methods=['POST'])
def new_chat():
    session_id = str(uuid.uuid4())
    return jsonify({"session_id": session_id}), 200

if __name__ == '__main__':
    app.run(debug=False)
