# core/pdf_processor.py
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from core.model_manager import embeddings_model
from langchain_core.documents import Document # Ensure Document type is imported for clarity
import re # Still useful for text cleaning
from typing import List, Optional # For type hints
from config import Config


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text_from_pdf(text: str) -> str:
    """
    Cleans extracted text by removing common PDF artifacts.
    - Removes excessive whitespace (multiple spaces, newlines)
    - Fixes hyphenated words broken across lines.
    """
    # Remove hyphenation at line breaks
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Replace multiple newlines and spaces with single space, then strip
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_pdf_semantically(
    file_path: str
) -> List[Document]:
    """
    Extracts text from a PDF and splits it into semantically coherent chunks
    using LangChain's PyPDFLoader and SemanticChunker.

    Args:
        file_path (str): The path to the PDF file.
        breakpoint_threshold_amount (float): 

    Returns:
        list: A list of Document objects, each representing a semantic chunk
              with added metadata (source).
    """
    logging.info(f"Starting Semantic PDF Processing for: {file_path}")

    # 1. Initialize the embedding model needed for semantic analysis
    

    # 2. Configure the SemanticChunker
    text_splitter = SemanticChunker(
        embeddings_model,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=Config.SEMANTIC_CHUNKER_BREAKPOINT_THRESHOLD
    )
    
    logging.info(f"SemanticChunker initialized with percentile threshold: {Config.SEMANTIC_CHUNKER_BREAKPOINT_THRESHOLD}.")

   
    loaded_pages: List[Document] = []
    try:
        loader = PyPDFLoader(file_path)
        loaded_pages = loader.load() # This returns a list of Document objects
        
        if not loaded_pages:
            print("No pages loaded from the PDF or file is empty.")
            return []

        print(f"Successfully loaded {len(loaded_pages)} pages using PyPDFLoader.")

        # Clean text from each loaded page document
        cleaned_page_contents: List[str] = []
        for page_doc in loaded_pages:
            cleaned_content = clean_text_from_pdf(page_doc.page_content)
            if cleaned_content:
                cleaned_page_contents.append(cleaned_content)
        
        if not cleaned_page_contents:
            print("No text left after cleaning from the PDF pages.")
            return []

        # Concatenate all cleaned page texts into a single string for semantic chunking
        # SemanticChunker typically works best on a single continuous string to find
        # semantic boundaries across page breaks.
        full_cleaned_text = " ".join(cleaned_page_contents)
        print(f"Concatenated text length for chunking: {len(full_cleaned_text)} characters.")

    except FileNotFoundError:
        print(f"Error: PDF file not found at {file_path}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during PDF loading or cleaning: {e}")
        return []

    # 4. Split the concatenated text into semantic chunks
    # Note: When SemanticChunker processes a single long string, the page numbers
    # from the original PDF documents are not directly carried over to the new
    # semantic chunks by default. Each semantic chunk will be a new Document object.
    chunks = text_splitter.create_documents([full_cleaned_text])
    
    # Add the original file path as 'source' metadata to each semantic chunk
    # This ensures each chunk knows which document it came from.
    for chunk in chunks:
        chunk.metadata["source"] = file_path

    print(f"--- Created {len(chunks)} semantic chunks. ---")
    
    # You can inspect a chunk to see the result


    return chunks
