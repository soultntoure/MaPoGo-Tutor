# MaPoGo Tutor - An AI-Powered RAG Learning Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-black)
![React](https://img.shields.io/badge/React-18-blue)
![Lovable.ai](https://img.shields.io/badge/UI%20built%20with-Lovable.ai-blue)
![LangChain](https://img.shields.io/badge/LangChain-blueviolet)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-orange)

MaPoGo Tutor is a full-stack web application designed to explore and demonstrate the principles of Retrieval-Augmented Generation (RAG). It transforms static PDF documents into dynamic, interactive learning experiences, showcasing a complete, end-to-end RAG pipeline from document processing to intelligent, AI-driven interaction.

<!-- 
**ACTION REQUIRED:** Create a short GIF of you uploading a PDF and getting a summary or quiz, then replace the placeholder below. This is the best way to showcase your project!
Tools like ScreenToGif (Windows) or Giphy Capture (Mac) are great for this. 
-->
![App Demo](./docs/demo.gif)
*(Replace this with a link to your own demo GIF)*

## ✨ Project Purpose & Scope

The primary purpose of this project was to gain practical, hands-on experience in designing and building a RAG application. It serves as a demonstration of skills in:

*   **RAG Pipeline Design:** Implementing the full lifecycle of data ingestion, indexing, retrieval, and generation.
*   **LLM Integration:** Connecting to and prompting Google's Gemini large language models.
*   **Text Processing:** Using modern techniques like semantic chunking for intelligent document parsing.
*   **Vector Similarity Search:** Leveraging an in-memory vector store (ChromaDB) for efficient, session-based retrieval.
*   **Prompt Engineering:** Crafting robust, task-specific prompts that enforce desired output formats (like JSON).
*   **Rapid Full-Stack Development:** Building a Python/Flask backend and rapidly prototyping/exporting a React frontend using **Lovable.ai**.

A core design choice is the **ephemeral nature of data**. The application is a session-based demo: when a user uploads a PDF, its content is processed and held in memory only for that session. All data is cleared upon new uploads or a server restart, emphasizing the RAG workflow over long-term data persistence.

## 🛠️ Key Functionalities

*   **PDF Upload & Processing:** A Flask endpoint receives an uploaded PDF, which is then parsed, cleaned, and split into semantically coherent chunks. These chunks are converted into vector embeddings and stored in an in-memory ChromaDB vector store for the current session.
*   **Intelligent Summarizer:** This feature retrieves a diverse set of relevant chunks from the document using Maximal Marginal Relevance (MMR) search. It then prompts the Gemini API to generate a high-level summary, ensuring broad coverage of the document's topics.
*   **Concept Explainer:** A user can ask a natural language question. The query is embedded, and a vector similarity search retrieves the most relevant text chunks from the document. These chunks provide the context for the Gemini API to generate a detailed, source-grounded explanation.
*   **Adaptive Quiz Generator:** This function creates multiple-choice quizzes based on the document's content. It adaptively retrieves context based on the number of questions requested and uses a structured output parser to force the LLM to return clean, reliable JSON, simplifying frontend rendering.

## ⚙️ Tech Stack & Architecture

*   **Backend:**
    *   **Framework:** Python 3.10+ with Flask
    *   **AI Orchestration:** LangChain
    *   **LLM:** Google Gemini Pro (`gemini-1.5-pro-latest`)
    *   **Embeddings:** Google Text Embeddings (`text-embedding-004`)
    *   **Vector Store:** ChromaDB (In-Memory)
    *   **PDF Processing:** `PyPDFLoader` for extraction, `SemanticChunker` for text splitting.

*   **Frontend:**
    *   **Framework:** React (The UI was rapidly built and exported using the **Lovable.ai** low-code platform)
    *   **Styling:** Tailwind CSS
    *   **Build Tool:** Vite

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

*   Python 3.10+
*   Node.js and npm (LTS version recommended)
*   Git
*   A Google AI API Key. You can get one from the [Google AI Studio](https://aistudio.google.com/app/apikey).

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/MaPoGo_tutor.git
    cd MaPoGo_tutor
    ```

2.  **Setup the Backend:**
    ```bash
    # Navigate to the backend directory
    cd backend

    # Create and activate a Python virtual environment
    python -m venv venv
    .\venv\Scripts\Activate.ps1  # On Windows PowerShell
    # source venv/bin/activate    # On macOS/Linux

    # Install Python dependencies
    pip install -r requirements.txt

    # Create a .env file from the example
    # Create a file named .env in the `backend` folder and add your API key:
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    ```

3.  **Setup the Frontend:**
    ```bash
    # In a new terminal, navigate to the frontend directory
    cd frontend

    # Install JavaScript dependencies
    npm install
    ```

### Running the Application

You need to run two processes in two separate terminals.

*   **Terminal 1: Run the Backend Server**
    ```bash
    # Make sure you are in the `backend` directory with the venv active
    python app.py
    ```
    *The backend will be running at `http://localhost:5000`.*

*   **Terminal 2: Run the Frontend Server**
    ```bash
    # Make sure you are in the `frontend` directory
    npm run dev
    ```
    *The frontend will be available at `http://localhost:5173` (or another port specified in the terminal).*

Open your browser to the frontend URL to use the application!
