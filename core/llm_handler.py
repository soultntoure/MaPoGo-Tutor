# core/llm_handler.py

from typing import List
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config import Config

def get_llm_response(question: str, context_docs: List[Document]) -> str:
    """
    Generates a response from the LLM based on a question and context documents.

    This function orchestrates the "Generation" part of the RAG pipeline.
    It takes the retrieved documents, formats them into a detailed prompt,
    and gets the final answer from the Gemini model.

    Args:
        question (str): The user's question.
        context_docs (List[Document]): A list of context documents from the vector store.

    Returns:
        str: The generated answer from the language model.
    """
    
    # 1. Define the Prompt Template
    # This is the instruction manual for the LLM. It's crucial for controlling
    # the output and ensuring the model answers based on the provided context.
    prompt_template_str = """
    You are an expert AI tutor. Your task is to answer the user's question based *only* on the provided document context.
    
    Provide a detailed, clear, and helpful answer. If the information to answer the question is not present in the context, you MUST state: 
    "Based on the provided document, I cannot answer this question." 
    Do not add any information that is not from the context.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    ANSWER:
    """
    
    prompt = PromptTemplate(
        template=prompt_template_str, 
        input_variables=["context", "question"]
    )

    # 2. Initialize the Language Model
    # We use a low temperature to encourage factual, less creative answers.
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.2
    )

    # 3. Define the RAG Chain using LCEL
    # LangChain Expression Language (LCEL) is the modern way to compose chains.
    # The `|` (pipe) operator connects the different components of the chain.
    # We also add an output parser to ensure we get a clean string as the final result.


    def format_docs(docs: List[Document]) -> str:
        """A helper function to combine document contents into a single string."""
        return "\n\n".join(doc.page_content for doc in docs)

    # The chain is constructed as follows:
    # 1. We define a dictionary with the inputs to the prompt (`context` and `question`).
    #    - `context` is populated by taking the `input_documents`, formatting them with our helper function.
    #    - `question` is passed through directly from the user's original question.
    # 2. This dictionary is then "piped" into the `prompt`.
    # 3. The formatted `prompt` is "piped" into the `llm`.
    # 4. The output from the `llm` is "piped" into a `StrOutputParser` to get the final string.
    rag_chain = (
        {"context": (lambda x: format_docs(x["input_documents"])), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        # To run the LCEL chain, we use the .invoke() method.
        # We only need to pass the original question, as the context is handled within the chain.
        # NOTE: The retriever will pass the docs, so the input to the chain will be a dictionary
        # In a full chain, it would look like this:
        # full_chain = retriever | rag_chain
        # For this function, we assume docs are already retrieved.
        
        # We manually format the input dictionary that the chain expects
        chain_input = {"input_documents": context_docs, "question": question}
        response = rag_chain.invoke(chain_input)
        
        return response

    except Exception as e:
        print(f"An error occurred while running the LLM chain: {e}")
        return "An error occurred while processing your question."