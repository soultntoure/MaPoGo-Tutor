# core/vector_store_manager.py

import logging
from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.schema.vectorstore import VectorStoreRetriever

# Import the centralized embedding model
from core.model_manager import embeddings_model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global state variables ---
# This will hold our single, session-based vector store instance.
vector_store: Optional[Chroma] = None
# We'll use a constant name for our session's collection.
SESSION_COLLECTION_NAME = "mapogo_tutor_session"

def clear_vector_store():
    """
    Forcefully clears the existing in-memory vector store and its collection.
    This ensures no data persists between uploads.
    """
    global vector_store
    if vector_store:
        try:
            # The correct way to clear Chroma is to delete the collection.
            logging.info(f"Attempting to delete collection: '{SESSION_COLLECTION_NAME}'")
            vector_store._client.delete_collection(name=SESSION_COLLECTION_NAME)
            logging.info("--- In-memory vector store collection deleted successfully. ---")
        except Exception as e:
            # This might happen if the collection was already gone, which is fine.
            logging.error(f"Error while deleting collection (might be benign): {e}")
    
    # Set the Python variable to None to be sure.
    vector_store = None

def create_vector_store(text_chunks: list[Document]):
    """
    Creates a new in-memory vector store from the provided text chunks.
    It FIRST ensures any old collection is deleted.
    """
    global vector_store

    # --- This is the most important change ---
    # Always clear the old store BEFORE creating a new one.
    clear_vector_store()

    if not text_chunks:
        logging.warning("No text chunks provided to create a vector store.")
        return

    try:
        logging.info(f"Creating new vector store collection '{SESSION_COLLECTION_NAME}' from {len(text_chunks)} chunks...")
        vector_store = Chroma.from_documents(
            documents=text_chunks,
            embedding=embeddings_model,
            collection_name=SESSION_COLLECTION_NAME # Explicitly name our collection
        )
        logging.info("--- In-memory vector store created successfully. ---")

    except Exception as e:
        logging.error(f"An error occurred while creating the vector store: {e}", exc_info=True)
        vector_store = None

def get_total_chunks() -> int:
    """
    Returns the total number of vectors/documents in the current vector store.
    """
    if vector_store:
        try:
            return vector_store._collection.count()
        except Exception as e:
            logging.error(f"Could not retrieve chunk count from vector store: {e}")
            return 0
    return 0

def get_retriever(k: int = 5, search_type: str = "similarity") -> Optional[VectorStoreRetriever]:
    """
    Returns a retriever object from the currently active vector store.
    """
    if vector_store:
        total_chunks_available = get_total_chunks()
        if total_chunks_available == 0:
             return None
        
        safe_k = min(k, total_chunks_available)
        if k > total_chunks_available:
            logging.warning(f"Requested k={k} chunks, but only {total_chunks_available} are available. Using k={safe_k}.")

        return vector_store.as_retriever(
            search_type=search_type, 
            search_kwargs={"k": safe_k}
        )
    
    logging.warning("Vector store not initialized. Please upload a PDF first.")
    return None