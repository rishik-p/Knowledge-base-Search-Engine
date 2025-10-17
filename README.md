Knowledge-base Search Engine

A Streamlit + FastAPI app that allows users to ask questions based on uploaded PDFs or pasted text. It uses a RAG (Retrieval-Augmented Generation) pipeline with OpenAI embeddings to create vector representations of documents, enabling context-aware answers while remembering chat history. Users can upload PDFs, paste text, or both, ask questions, and reset the session to clear previous documents.

Features

Upload PDFs and/or paste raw text for question answering

Context-aware answers using RAG with OpenAI embeddings

Maintains chat history for each session

Reset documents and chat history when needed

Simple, interactive interface with Streamlit

Installation

Clone the repository

Create a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

Install dependencies:
pip install -r requirements.txt

Set your OpenAI API key in a .env file:
OPENAI_API_KEY=your_api_key_here

Running the App

Start the FastAPI backend:
uvicorn main:app --reload

Start the Streamlit frontend in a new terminal:
streamlit run frontend.py

Open the URL shown by Streamlit (usually http://localhost:8501
) in your browser.

Use the sidebar to:

Upload PDFs, paste text, or both

Process input

Ask questions in the main interface

Clear chat history or reset documents
