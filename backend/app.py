# app.py

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# --- Load environment variables first ---
load_dotenv()

# --- Import your project's core logic ---
# Make sure these modules are ready and polished, as we've done.
from core.pdf_processor import process_pdf_semantically
from core.vector_store_manager import create_vector_store, clear_vector_store
from core.llm_handler import LLMHandler

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize the Flask App ---
app = Flask(__name__)

# --- Enable CORS for all domains on all routes ---
# This is crucial for allowing your Lovable.ai frontend to communicate with this backend.
CORS(app)

# --- Configure Upload Folder ---
# Make sure the 'temp_uploads' directory exists.
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Initialize a Singleton instance of the LLM Handler ---
# This is efficient because the models inside the handler are loaded only once
# when the application starts.
try:
    llm_handler = LLMHandler()
    logging.info("LLM Handler initialized successfully for the Flask app.")
except Exception as e:
    logging.error(f"FATAL: Could not initialize LLMHandler. The app may not function. Error: {e}", exc_info=True)
    llm_handler = None # Ensure it's None if initialization fails

# ==============================================================================
# === API ENDPOINTS ============================================================
# ==============================================================================

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Endpoint to upload a PDF file.
    It clears any previous session, processes the new PDF, and creates a new vector store.
    """
    if not llm_handler:
         return jsonify({"error": "LLM Handler is not available. Server configuration issue."}), 500

    # 1. Check if a file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']

    # 2. Check if the file has a name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # 3. Securely save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f"File '{filename}' uploaded successfully to '{filepath}'.")

        try:
            


            # b. Process the new PDF into chunks
            text_chunks = process_pdf_semantically(filepath)
            
            if not text_chunks:
                return jsonify({"error": "Failed to extract text from the PDF."}), 500

            # c. Create a new in-memory vector store from the chunks
            create_vector_store(text_chunks)
            
            return jsonify({"message": f"Successfully processed '{filename}'."}), 200

        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}", exc_info=True)
            return jsonify({"error": "An internal error occurred while processing the PDF."}), 500
    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400


@app.route('/summary', methods=['GET'])
def get_summary_endpoint():
    """
    Endpoint to get a summary of the uploaded document.
    """
    if not llm_handler:
         return jsonify({"error": "LLM Handler is not available."}), 500

    logging.info("Received request for document summary.")
    summary = llm_handler.get_summary()
    return jsonify({"summary": summary})


@app.route('/explain', methods=['POST'])
def explain_concept_endpoint():
    """
    Endpoint to get an explanation for a user's query.
    Expects a JSON body with a "query" key.
    """
    if not llm_handler:
         return jsonify({"error": "LLM Handler is not available."}), 500

    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    user_query = data['query']
    logging.info(f"Received request to explain concept: '{user_query}'")
    explanation = llm_handler.get_concept_explanation(user_query)
    return jsonify({"explanation": explanation})


@app.route('/quiz', methods=['POST'])
def get_quiz_endpoint():
    """
    Endpoint to generate a quiz. It expects an optional JSON body with
    "difficulty" and "num_questions" and returns a structured JSON response.
    """
    if not llm_handler:
         return jsonify({"error": "LLM Handler is not available. Server configuration issue."}), 500

    data = request.get_json()
    if not data:
        # It's good practice to handle cases where the request body is empty
        data = {}

    # 1. Extract parameters with sensible defaults and type safety.
    difficulty = data.get('difficulty', 'medium')
    try:
        # Ensure num_questions is treated as an integer
        num_questions = int(data.get('num_questions', 5))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid 'num_questions' format. It must be an integer."}), 400

    logging.info(f"Received request for a '{difficulty}' quiz with {num_questions} questions.")
    
    # 2. Call the LLM handler, which now does the heavy lifting of parsing.
    # We expect `quiz_data` to be a List of Dictionaries.
    quiz_data = llm_handler.get_quiz_questions(difficulty=difficulty, num_questions=num_questions)

    # 3. Check if the quiz generation was successful.
    # The handler returns an empty list `[]` on failure.
    if not quiz_data:
        logging.warning("Quiz generation returned no data. This could be due to a parsing error in the handler or insufficient context.")
        # Return a structured error message that the frontend can use.
        return jsonify({
            "error": "Failed to generate quiz.",
            "message": "Could not create a quiz from the provided document. The content may not be suitable or a server error occurred."
        }), 500

    # 4. Use `jsonify` to send the structured data to the frontend.
    # We wrap our list in a dictionary with a 'quiz' key. This is a best practice.
    # The frontend will receive: {"quiz": [{...}, {...}, ...]}
    return jsonify({"quiz": quiz_data})


# ==============================================================================
# === MAIN EXECUTION BLOCK =====================================================
# ==============================================================================

if __name__ == '__main__':
    # Runs the Flask app. debug=True will auto-reload the server on code changes.
    # Use host='0.0.0.0' to make the server accessible on your local network.
    app.run(host='0.0.0.0', port=5000, debug=True)