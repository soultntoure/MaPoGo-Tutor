# test_retrieval_pipeline.py

import os
from core.pdf_processor import process_pdf_semantically
from core.vector_store_manager import (
    create_vector_store,
    get_retriever,
    clear_vector_store
)

def run_test():
    """
    Tests the full retrieval pipeline: PDF processing -> Vector Store -> Retriever.
    """
    print("--- Starting Full Retrieval Pipeline Test ---")

   
    pdf_path = "NIPS-2017-attention-is-all-you-need-Paper.pdf"
    
    
    TEST_QUERY = "what did recent work achieve?" 

    if not os.path.exists(pdf_path):
        print(f"Error: Test file not found at '{pdf_path}'")
        return

    # --- STAGE 1: Process the PDF to get chunks ---
    print("\n--- STAGE 1: Processing PDF ---")
    chunks = process_pdf_semantically(pdf_path)
    if not chunks:
        print("Test Failed: PDF processing returned no chunks.")
        return
    print("PDF processing successful.")

    # --- STAGE 2: Create the Vector Store ---
    print("\n--- STAGE 2: Creating Vector Store ---")
    # First, ensure the store is clear from any previous runs
    clear_vector_store() 
    create_vector_store(chunks)
    
    # --- STAGE 3: Get the Retriever and Test It ---
    print("\n--- STAGE 3: Getting Retriever and Performing Search ---")
    retriever = get_retriever()
    if not retriever:
        print("Test Failed: get_retriever() returned None.")
        return
    
    print(f"Successfully got a retriever. Now searching for: '{TEST_QUERY}'")
    
    try:
        # This is the core of the test: use the retriever to find relevant docs
        relevant_docs = retriever.invoke(TEST_QUERY)
        
        if relevant_docs:
            print(f"\n--- Test Passed: Successfully retrieved {len(relevant_docs)} relevant documents. ---")
            print("\n--- Inspecting Retrieved Documents: ---")
            for i, doc in enumerate(relevant_docs):
                print(f"\n----- Document {i+1} (Relevance Score: High -> Low) -----")
                print(f"Content: {doc.page_content}")
                print("-" * 30)
        else:
            print("Test Warning: The search returned no documents. The pipeline works, but the query might not have matches.")

    except Exception as e:
        print(f"An error occurred during retrieval: {e}")

    # --- STAGE 4: Test Clearing the Store ---
    print("\n--- STAGE 4: Testing Store Clearing ---")
    clear_vector_store()
    retriever_after_clear = get_retriever()
    if retriever_after_clear is None:
        print("--- Test Passed: Store successfully cleared. ---")
    else:
        print("--- Test Failed: Store was not cleared properly. ---")


if __name__ == '__main__':
    run_test()