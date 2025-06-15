# core/llm_handler.py

import logging
from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import the centralized models and the retriever function
from core.model_manager import llm 
from core.vector_store_manager import get_retriever

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_docs(docs: List[Document]) -> str:
    """Helper function to format retrieved documents into a single string."""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


class LLMHandler:
    """
    Handles all interactions with the Language Model.

    This class encapsulates the logic for different RAG-based tasks such as
    generating summaries, answering questions about concepts, and creating quizzes.
    It uses a centralized LLM instance and retriever.
    """
    def __init__(self):
        # The LLM is already initialized in model_manager, so we just use it.
        self.llm = llm
        self.output_parser = StrOutputParser()
        logging.info("LLMHandler initialized.")

    def get_summary(self, num_chunks: int = 10) -> str:
        """
        Generates a concise summary of the entire document.

        It retrieves a broad set of chunks from the document to form a basis
        for the summary.
        """
        logging.info("Generating document summary...")
        retriever = get_retriever(k=num_chunks)
        if not retriever:
            return "Vector store not initialized. Please upload a PDF first."
        
        # We retrieve docs with a generic query that represents the whole document.
        context_docs = retriever.invoke("A comprehensive overview of the entire document's content.")
        context = format_docs(context_docs)
        
        system_prompt = "You are an expert academic assistant. Based on the following context extracted from a document, please provide a concise, high-level summary. Capture the main ideas and key topics covered."
        human_prompt = "CONTEXT:\n{context}\n\nCONCISE SUMMARY:"
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])

        chain = prompt_template | self.llm | self.output_parser
        summary = chain.invoke({"context": context})
        return summary




    def get_concept_explanation(self, user_query: str) -> str:
        """
        Explains a specific concept based on the user's query.

        This is the core RAG function for user questions.
        """
        logging.info(f"Generating explanation for query: '{user_query}'")
        retriever = get_retriever(k=5) # Retrieve 5 relevant chunks
        if not retriever:
            return "Vector store not initialized. Please upload a PDF first."

        system_prompt = """You are an expert AI tutor. Your task is to answer the user's question based *only* on the provided document context.
Provide a detailed, clear, and helpful answer. If the information to answer the question is not present in the context, you MUST state: "Based on the provided document, I cannot answer this question." Do not add any information that is not from the context."""
        human_prompt = "CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nHELPFUL ANSWER:"

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])

        # This chain combines retrieval and generation
        rag_chain = (
            {
                "context": retriever | format_docs, 
                "question": lambda x: x # Pass the user query through
            }
            | prompt_template
            | self.llm
            | self.output_parser
        )
        
        response = rag_chain.invoke(user_query)
        return response






    def get_quiz_questions(self, difficulty: str = "medium", num_questions: int = 5) -> str:
        """
        Generates a multiple-choice quiz from the document content.
        """
        logging.info(f"Generating {difficulty} quiz with {num_questions} questions...")
        retriever = get_retriever(k=10) # Get a good variety of chunks for quiz
        if not retriever:
            return "Vector store not initialized. Please upload a PDF first."
        
        context_docs = retriever.invoke("Key concepts and important details from the document.")
        context = format_docs(context_docs)

        system_prompt = """You are an expert quizmaster. Based on the context below, create a multiple-choice quiz.
                        Instructions:
                        1. Generate exactly {num_questions} questions.
                        2. The difficulty of the questions should be {difficulty}.
                        3. For each question, provide 4 options (A, B, C, D).
                        4. Clearly mark the correct answer for each question.
                        5. Ensure the questions are derived *only* from the provided context."""
        human_prompt = "CONTEXT:\n{context}\n\nQUIZ:"
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        chain = prompt_template | self.llm | self.output_parser
        quiz = chain.invoke({
            "num_questions": num_questions,
            "difficulty": difficulty,
            "context": context
        })
        return quiz