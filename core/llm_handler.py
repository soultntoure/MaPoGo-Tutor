# core/llm_handler.py

import logging
from typing import List, Dict 
from langchain_core.documents import Document
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import the centralized models and the retriever function
from core.model_manager import llm 
from core.vector_store_manager import get_retriever, get_total_chunks


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


    def get_summary(self) -> str:
        """
        Generates a concise summary of the document using an adaptive
        number of chunks based on the document's size.
        """
        logging.info("Generating document summary with adaptive retrieval...")
        
        total_chunks = get_total_chunks()
        if total_chunks == 0:
            return "Vector store is empty. Please upload a PDF first."

        # --- Adaptive K Logic ---
        # 1. Calculate a proportional number of chunks (e.g., 20% of the doc)
        proportional_k = int(total_chunks * 0.25)

        # 2. Define safety nets: a floor and a ceiling for k
        MIN_SUMMARY_CHUNKS = 7
        MAX_SUMMARY_CHUNKS = 25 

        # 3. Clamp the calculated k within our min/max bounds
        dynamic_k = max(MIN_SUMMARY_CHUNKS, min(proportional_k, MAX_SUMMARY_CHUNKS))
        
        logging.info(f"Total chunks in document: {total_chunks}. Adaptively retrieving {dynamic_k} chunks for summary.")

        # Use the dynamically calculated k with the MMR search type
        retriever = get_retriever(k=dynamic_k, search_type="mmr")
        if not retriever:
            # This case is mostly handled by the total_chunks check above, but good practice
            return "Vector store not initialized. Please upload a PDF first."
        
        context_docs = retriever.invoke("A comprehensive overview of the entire document's content.")
        context = format_docs(context_docs)

        # ... The rest of the prompt and chain logic remains exactly the same ...
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






    def get_quiz_questions(self, difficulty: str = "medium", num_questions: int = 5) -> List[Dict]:
        """
        Generates a multiple-choice quiz and returns it as a structured
        list of dictionaries (JSON), which is ideal for API responses.
        """
        logging.info(f"Generating structured JSON quiz: {difficulty}, {num_questions} questions.")

        # --- 1. Define the desired JSON structure WRAPPED in a parent key ---
        # We define the schemas for the inner objects as before.
        question_schema = ResponseSchema(name="question", description="The text of the quiz question.")
        options_schema = ResponseSchema(name="options", description="A list of 4 string options for the question.")
        answer_schema = ResponseSchema(name="answer", description="The correct answer, which must be one of the strings from the 'options' list.")
        
        # [+] NEW: Define a schema for the top-level object.
        # Its description tells the LLM that its value should be a list of other objects.
        quiz_schema = ResponseSchema(
            name="quiz",
            description=f"A list of {num_questions} JSON objects, where each object has the keys 'question', 'options', and 'answer'."
        )

        # --- 2. Create a parser that expects the TOP-LEVEL schema ---
        # The parser will now look for the "quiz" key.
        output_parser = StructuredOutputParser.from_response_schemas([quiz_schema])
        format_instructions = output_parser.get_format_instructions()

        # --- 3. Adaptive Retrieval (your logic is perfect) ---
        proportional_k = num_questions * 2
        dynamic_k = max(4, min(proportional_k, 20))
        
        logging.info(f"Adaptively retrieving {dynamic_k} chunks for the quiz.")
        retriever = get_retriever(k=dynamic_k, search_type="similarity")
        if not retriever:
            return []

        context_docs = retriever.invoke("Key concepts, definitions, and important details suitable for a quiz.")
        context = format_docs(context_docs)

        # --- 4. Update the prompt to ask for the WRAPPED structure ---
        system_prompt = """You are an expert quizmaster AI. Your task is to create a quiz based *only* on the provided context.
        
        Follow these instructions precisely:
        1. Generate exactly {num_questions} questions of {difficulty} difficulty.
        2. Base every question and answer strictly on the provided context.
        3. **CRITICAL**: Format your entire output as a single JSON object with a single top-level key named "quiz". The value of "quiz" must be a JSON array (list) of question objects. Do not include any other text, explanations, or markdown formatting.
        
        {format_instructions}
        """

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "CONTEXT:\n{context}\n\nQUIZ JSON:")
        ])
        
        chain = prompt_template | self.llm | output_parser
        
        try:
            # --- 5. Invoke the chain and EXTRACT the list from the parsed dictionary ---
            parsed_output = chain.invoke({
                "num_questions": num_questions,
                "difficulty": difficulty,
                "context": context,
                "format_instructions": format_instructions
            })
            
            # The parser now returns a dictionary: {'quiz': [...]}. We extract the list.
            return parsed_output.get('quiz', [])

        except Exception as e:
            logging.error(f"Failed to parse LLM response into JSON for quiz. Error: {e}", exc_info=True)
            return []