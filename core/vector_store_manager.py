# core/vector_store_manager.py

from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from langchain.schema.vectorstore import VectorStoreRetriever
from config import Config

# This global variable will act as our simple, in-memory "session" storage.
# It holds the vector store for the most recently uploaded PDF.
# Using 'Optional[Chroma]' for type hinting means it can either be a Chroma object or None.
vector_store: Optional[Chroma] = None


def clear_vector_store():
    """
    Clears the existing in-memory vector store.
    This is called when a new PDF is uploaded to ensure a fresh session.
    """
    global vector_store
    vector_store = None
    print("--- In-memory vector store cleared. ---")


def create_vector_store(text_chunks: List[Document]):
    """
    Creates a new in-memory vector store from the provided text chunks.

    This function takes the text chunks from the PDF processor, generates
    embeddings for them using Google's model, and stores them in a Chroma
    vector store that lives only in the application's memory.

    Args:
        text_chunks (List[Document]): A list of Document objects from the pdf_processor.
    """
    global vector_store

    if not text_chunks:
        print("No text chunks provided to create a vector store.")
        return

    try:
        # 1. Initialize the embedding model
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=Config.GOOGLE_API_KEY
        )

        # 2. Create the Chroma vector store from the documents and embeddings
        # This is the core step where text is converted to vectors and indexed.
        print(f"Creating vector store from {len(text_chunks)} chunks...")
        vector_store = Chroma.from_documents(
            documents=text_chunks,
            embedding=embeddings
        )
        print("--- In-memory vector store created successfully. ---")

    except Exception as e:
        print(f"An error occurred while creating the vector store: {e}")
        # Ensure the store is None if creation fails
        vector_store = None


def get_retriever() -> Optional[VectorStoreRetriever]:
    """
    Returns a retriever object from the currently active vector store.

    The retriever is the interface used to perform similarity searches on the
    vector store to find documents relevant to a user's query.

    Returns:
        Optional[VectorStoreRetriever]: A retriever object if the vector store
                                        exists, otherwise None.
    """
    if vector_store:
        # as_retriever() is a handy method to get a ready-to-use retriever
        return vector_store.as_retriever()
    
    print("Vector store not initialized. Please upload a PDF first.")
    return None