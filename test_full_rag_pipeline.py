# test_full_rag_pipeline.py

import os
from core.pdf_processor import process_pdf_semantically
from core.vector_store_manager import create_vector_store, get_retriever, clear_vector_store
from core.llm_handler import get_llm_response

def run_full_rag_test():
    """
    Tests the complete RAG pipeline:
    1. Processes a PDF into chunks.
    2. Creates a vector store from the chunks.
    3. Retrieves relevant documents for a given question.
    4. Generates a final answer using the LLM with the retrieved context.
    5. Verifies behavior for a question that is outside the document's context.
    """
    print("--- 🚀 Starting Full RAG Pipeline Test 🚀 ---")

    # --- 1. SETUP ---
    # Define the path to your test PDF
    pdf_path = "mars_lithograph.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ FATAL ERROR: Test PDF not found at '{pdf_path}'")
        print("Please make sure the PDF file is in the same directory as this script.")
        return

    # Define the test questions
    question_in_context = "What does scientific evidence suggest about the presence of water on Mars?"
    question_out_of_context = "What is the best recipe for baking chocolate chip cookies?"

    # Process the PDF and create the vector store once for all tests
    print("\n--- STAGE 1: PDF Processing & Vector Store Creation ---")
    chunks = process_pdf_semantically(pdf_path)
    if not chunks:
        print("❌ TEST FAILED: PDF processing yielded no chunks.")
        return
    
    clear_vector_store()  # Ensure store is fresh
    create_vector_store(chunks)
    retriever = get_retriever()
    if not retriever:
        print("❌ TEST FAILED: Vector store or retriever could not be initialized.")
        return
    print("✅ PDF processed and vector store created successfully.")
    print("-" * 50)

    # --- 2. TEST CASE 1: Question within document context ---
    print("\n--- STAGE 2: Testing with a question IN CONTEXT ---")
    print(f"❓ Query: \"{question_in_context}\"")

    # Retrieve relevant documents
    print("\n   -> Retrieving relevant documents...")
    # Use the modernized .invoke() method
    relevant_docs = retriever.invoke(question_in_context)
    print(f"   -> Retrieved {len(relevant_docs)} documents.")

    if not relevant_docs:
        print("   ⚠️ WARNING: No relevant documents were retrieved. The LLM will have no context.")
    
    # Generate the response
    print("   -> Generating response from LLM...")
    final_answer = get_llm_response(question_in_context, relevant_docs)

    print("\n" + "="*10 + " FINAL ANSWER " + "="*10)
    print(final_answer)
    print("="*34)
    print("-" * 50)


    # --- 3. TEST CASE 2: Question outside of document context ---
    print("\n--- STAGE 3: Testing with a question OUTSIDE OF CONTEXT ---")
    print(f"❓ Query: \"{question_out_of_context}\"")

    # Retrieve relevant documents
    print("\n   -> Retrieving relevant documents...")
    # The retriever will still try to find the "closest" documents, even if they aren't very relevant.
    relevant_docs_for_off_topic = retriever.invoke(question_out_of_context)
    print(f"   -> Retrieved {len(relevant_docs_for_off_topic)} documents (these may not be truly relevant).")

    # Generate the response
    print("   -> Generating response from LLM...")
    final_answer_off_topic = get_llm_response(question_out_of_context, relevant_docs_for_off_topic)
    
    print("\n" + "="*10 + " FINAL ANSWER " + "="*10)
    print(final_answer_off_topic)
    print("="*34)
    print("-" * 50)

    # --- 4. CLEANUP ---
    print("\n--- STAGE 4: Cleaning up ---")
    clear_vector_store()
    print("\n--- 🏁 Full RAG Pipeline Test Finished 🏁 ---")


if __name__ == '__main__':
    # Ensure you have a .env file with your GOOGLE_API_KEY or have it set as an environment variable
    # For example, create a file named 'config.py' with:
    # from dotenv import load_dotenv
    # import os
    # load_dotenv()
    # class Config:
    #     GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    run_full_rag_test()
