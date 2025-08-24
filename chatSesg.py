from pymongo import MongoClient
from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google import genai
import os
import uuid
import re
import asyncio


app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# MongoDB Connection
# client = MongoClient("mongodb+srv://pranavrajkaravadi:pranavrajkaravadi@cluster0.ud6qbsd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient("mongodb+srv://admin:DavlAjh6GWIga01B@cluster0.pailzmu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['doj_database']
collection = db['minister_data']


os.environ["GOOGLE_API_KEY"] = "AIzaSyCcVBirCHxNl0V6lt4QF-Gj8qwnh7aKeoA"
client = genai.Client(api_key="AIzaSyCcVBirCHxNl0V6lt4QF-Gj8qwnh7aKeoA")

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Check if query is related to tables
import re

def is_table_related(query):
    table_keywords = [
        'name', 'designation', 'email', 'address', 'phone', 'fax', 'room no',
        'service', 'transaction', 'weightage', 'responsible person', 
        'mobile', 'phone numbers', 'process', 'document required', 'category', 'mode', 'amount',
        'si. no.', 'success indicators', 'data source', 'landline', 'nodal officer'
    ]
    
    # Convert query to lowercase for case-insensitive comparison
    query_lower = query.lower()
    
    # Check if any keyword is partially matched in the query
    return any(re.search(r'\b' + re.escape(keyword) + r'\b', query_lower) for keyword in table_keywords)


# MongoDB Search Function
def mongo_search(query_input):
    query = [
        {
            "$search": {
                "index": "default",
                "text": {
                    "query": query_input,
                    "path": {"wildcard": "*"}
                }
            }
        },
        {"$limit": 10}
    ]
    result = collection.aggregate(query)
    return list(result)

# RAG Function to send MongoDB results to LLM
def ollama_llm(question, context):
    llm = Ollama(model="llama3.2")
    prompt_template = ChatPromptTemplate.from_template("Answer the question based only on the following context: {context} --- Answer the question based on the above context: {question}")
    prompt = prompt_template.format(context=context, question=question)
    # response_text = llm.invoke(prompt)
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    
    return response.text

def user_input(user_question, context=""):
    if context:  # If there's context (i.e., MongoDB results), use it
        print("type mongo")
        response = ollama_llm(user_question, context)
    else:
        # If no context (i.e., it's a RAG-based question), use FAISS
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        
        # Prepare the context from FAISS
        context = "\n".join([doc.page_content for doc in docs])
        response = ollama_llm(user_question, context)

    return response

@app.route('/ask_question', methods=['POST'])
def ask_question():
    asyncio.set_event_loop(asyncio.new_event_loop())
    data = request.json
    question = data.get('question')
    session_id = data.get('session_id')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Check if query is related to tables
    if is_table_related(question):
        # Query MongoDB if it's related to tables
        mongo_results = mongo_search(question)
        
        # Prepare the MongoDB result as context for the LLM
        context = "\n".join([str(doc) for doc in mongo_results])
        
        # Send MongoDB result as context to LLM
        response = ollama_llm(question, context)
        
        return jsonify({"response": response, "session_id": session_id}), 200
    else:
        # Process with RAG if not related to tables
        response = user_input(question, "")
        return jsonify({"response": response, "session_id": session_id}), 200

@app.route('/new_chat', methods=['POST'])
def new_chat():
    session_id = str(uuid.uuid4())
    return jsonify({"session_id": session_id}), 200

if __name__ == '__main__':
    app.run(debug=False)
