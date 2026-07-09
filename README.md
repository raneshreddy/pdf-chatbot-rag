# PDF Chatbot

An AI-powered chatbot that answers questions about any PDF document, built with Python and Streamlit.

## Features
- Upload any PDF and ask questions about its contents
- Powered by Llama 3.1 via Groq API
- Clean chat interface built with Streamlit
- Conversation memory across turns

## Setup
1. Clone the repo
2. Install dependencies:
3. Create a `.env` file:
4. Run:
## Limitations
Currently sends raw PDF text in the prompt — works best on shorter documents.
Next version will use ChromaDB for proper RAG to handle any size PDF.

## What I learned
- Extracting text from PDFs with pdfplumber
- Streamlit file uploader and session state
- Injecting document context into LLM system prompts
