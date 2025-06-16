# core/model_manager.py

"""
Centralized model management for the MaPoGo Tutor application.

This module initializes and provides singleton instances of the AI models
used throughout the application, such as the embedding model and the
main language model. This avoids re-initializing models in different
parts of the code, improving efficiency and maintainability.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from config import Config

# --- Singleton Model Instances ---

# Initialize the embedding model.
# This is used for creating vector representations of text chunks.
# We specify the task_type for retrieval to optimize the embeddings.
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=Config.GOOGLE_API_KEY,
    task_type="retrieval_document" # Use "retrieval_query" for retrieving docs
)


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=Config.GOOGLE_API_KEY,
    temperature=1.0, # A balanced value for creativity and factuality
)

print("--- AI Models Initialized (Embeddings & LLM) ---")