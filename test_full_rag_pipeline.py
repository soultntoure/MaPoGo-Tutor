# test_full_rag_pipeline.py

import os
import logging
from dotenv import load_dotenv

# --- Important: Load environment variables before importing other modules ---
# This ensures that Config() can access GOOGLE_API_KEY when modules are imported.
load_dotenv() 

# Import your project's core components
from core.pdf_processor import process_pdf_semantically
from core.vector_store_manager import create_vector_store, clear_vector_store
from core.llm_handler import LLMHandler

# --- 1. CONFIGURE LOGGING AND TEST PARAMETERS ---

# Set up detailed logging to see the inner workings of the pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# Define the path to your test document
PDF_PATH = "mars_lithograph.pdf" 

# Define the test questions
QUESTION_IN_CONTEXT = "What are some significant dates and events in the history of Mars exploration, as described in the document?"
QUESTION_OUT_OF_CONTEXT = "What is the significance of the 'Canali' in the context of Mars exploration?"

def run_test_pipeline():
    """
    Executes a full, end-to-end test of the RAG pipeline.
    """
    logging.info("==================================================")
    logging.info("======= STARTING E2E RAG PIPELINE TEST =======")
    logging.info("==================================================")
    
    # --- PRE-TEST CHECKS ---
    if not os.path.exists(PDF_PATH):
        logging.error(f"FATAL: Test PDF not found at '{PDF_PATH}'. Please download it and place it in the project root.")
        return

    # Ensure we start with a clean slate
    clear_vector_store()

    # --- STAGE 1: PDF PROCESSING (LOADING & CHUNKING) ---
    logging.info(f"\n--- [STAGE 1/4] Processing PDF: {PDF_PATH} ---")
    try:
        text_chunks = process_pdf_semantically(PDF_PATH)
        if not text_chunks:
            logging.error("PDF processing resulted in zero chunks. Aborting test.")
            return
        logging.info(f"Successfully processed PDF into {len(text_chunks)} semantic chunks.")
    except Exception as e:
        logging.error(f"An error occurred during PDF processing: {e}", exc_info=True)
        return

    # --- STAGE 2: VECTOR STORE CREATION (EMBEDDING & STORING) ---
    logging.info("\n--- [STAGE 2/4] Creating in-memory vector store ---")
    try:
        create_vector_store(text_chunks)
        logging.info("Vector store created successfully.")
    except Exception as e:
        logging.error(f"An error occurred during vector store creation: {e}", exc_info=True)
        return

    # --- STAGE 3: INITIALIZE LLM HANDLER ---
    logging.info("\n--- [STAGE 3/4] Initializing LLM Handler ---")
    try:
        llm_handler = LLMHandler()
        logging.info("LLMHandler initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize LLMHandler: {e}", exc_info=True)
        return

    # --- STAGE 4: RUNNING QUERIES ---
    logging.info("\n--- [STAGE 4/4] Running test queries ---")

    # Test 1: In-Context Question
    print("\n" + "="*50)
    logging.info(f"TEST 1: Asking an IN-CONTEXT question...")
    print(f"QUESTION: {QUESTION_IN_CONTEXT}")
    response_in_context = llm_handler.get_concept_explanation(QUESTION_IN_CONTEXT)
    print("\nLLM RESPONSE:")
    print(response_in_context)
    print("="*50)

    # Test 2: Out-of-Context Question
    print("\n" + "="*50)
    logging.info(f"TEST 2: Asking an OUT-OF-CONTEXT question...")
    print(f"QUESTION: {QUESTION_OUT_OF_CONTEXT}")
    response_out_of_context = llm_handler.get_concept_explanation(QUESTION_OUT_OF_CONTEXT)
    print("\nLLM RESPONSE:")
    print(response_out_of_context)
    print("="*50)
    
    # Test 3: Document Summary
    print("\n" + "="*50)
    logging.info("TEST 3: Generating a document summary...")
    summary = llm_handler.get_summary()
    print("\nDOCUMENT SUMMARY:")
    print(summary)
    print("="*50)

    # Test 4: Quiz Generation
    print("\n" + "="*50)
    logging.info("TEST 4: Generating a 'hard' quiz...")
    quiz = llm_handler.get_quiz_questions(difficulty="hard", num_questions=3)
    print("\nGENERATED QUIZ:")
    print(quiz)
    print("="*50)


    # --- FINAL CLEANUP ---
    logging.info("\n--- Test complete. Clearing vector store. ---")
    clear_vector_store()
    logging.info("==================================================")
    logging.info("=============== TEST RUN FINISHED ===============")
    logging.info("==================================================")


if __name__ == '__main__':
    # This block ensures the test runs only when the script is executed directly
    run_test_pipeline()