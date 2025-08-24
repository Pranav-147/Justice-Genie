from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AIzaSyCcVBirCHxNl0V6lt4QF-Gj8qwnh7aKeoA"
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_pdf_text(pdf_docs):
    """
    Extracts text from a list of PDF documents.

    Args:
        pdf_docs (list of str): Paths to the PDF files.

    Returns:
        str: Extracted text from all pages of the PDF files.
    """
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    """
    Splits the extracted text into smaller chunks.

    Args:
        text (str): The extracted text to split.

    Returns:
        list of str: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    """
    Creates a vector store from the text chunks.

    Args:
        text_chunks (list of str): A list of text chunks.

    Returns:
        FAISS: The vector store containing the embeddings of the text chunks.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store


# Example usage
if __name__ == "__main__":
    pdf_files = ["data.pdf"]  # Replace with your PDF file paths
    extracted_text = get_pdf_text(pdf_files)
    text_chunks = get_text_chunks(extracted_text)
    vector_store = get_vector_store(text_chunks)
    print("Vector store created and saved locally.")
