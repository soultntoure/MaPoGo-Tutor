# test_pdf_processor.py

import os
from core.pdf_processor import process_pdf_semantically

def run_test():
    """
    Tests the semantic PDF processing function.
    """
    print("--- Starting PDF Processor Test ---")

    # Define the path to your sample PDF
    pdf_path = "NIPS-2017-attention-is-all-you-need-Paper.pdf"

    # 1. Check if the sample file exists
    if not os.path.exists(pdf_path):
        print(f"Error: Test file not found at '{pdf_path}'")
        print("Please make sure 'sample_document.pdf' is in the project root.")
        return

    print(f"Found test file: {pdf_path}")

    # 2. Call the function you want to test
    # This will use your real API key for embeddings, so ensure it's correct.
    try:
        chunks = process_pdf_semantically(pdf_path)
    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")
        print("\nTroubleshooting:")
        print("- Is your GOOGLE_API_KEY in the .env file correct?")
        print("- Are you connected to the internet?")
        return

    # 3. Analyze the output
    if chunks:
        print(f"\n--- Test Passed: Successfully created {len(chunks)} chunks. ---")

        # Print information about the first few chunks to inspect them
        print("\n--- Inspecting the first 3 chunks: ---")
        for i, chunk in enumerate(chunks[:30]):
            print(f"\n----- Chunk {i+1} -----")
            print(f"Type: {type(chunk)}")
            # The chunk object has 'page_content' and 'metadata' attributes
            print(f"Content Preview: '{chunk.page_content[:350]}...'")
            print(f"Character Count: {len(chunk.page_content)}")
            print("-" * 20)
    else:
        print("\n--- Test Failed: The function did not return any chunks. ---")

if __name__ == '__main__':
    # This block allows you to run the script directly from the command line
    run_test()