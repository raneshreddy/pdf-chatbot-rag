# PDF Chatbot

An AI-powered chatbot that answers questions about any PDF document, built with Python and Streamlit.

## Features

- Upload any PDF and ask questions about its contents
- Powered by Llama 3.1 via Groq API
- Clean chat interface built with Streamlit
- Conversation memory across turns
- Proper RAG pipeline using ChromaDB — handles PDFs of any size instead of sending raw text in the prompt
- Table-aware extraction for structured PDFs (e.g. marksheets), so rows aren't broken apart mid-parse
- Hybrid retrieval — exact-match lookup for structured IDs, vector search for everything else
- Debug mode to inspect retrieved context and which retrieval path was used

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install streamlit chromadb pdfplumber groq python-dotenv --break-system-packages
   ```
3. Create a `.env` file:
   ```
   GROQ_API_KEY=your_key_here
   ```
4. Run:
   ```bash
   streamlit run rag_app.py
   ```

## Limitations

Previously sent raw PDF text in the prompt, which only worked well on shorter documents. This is now fixed with a proper RAG pipeline (ChromaDB), so document size is no longer a hard limit. Retrieval accuracy on structured data (tables, IDs) still depends on clean table extraction from the source PDF.

## What I learned

- Extracting text from PDFs with pdfplumber
- Streamlit file uploader and session state
- Injecting document context into LLM system prompts
- Why generic word-count chunking breaks tabular data, and how to chunk row-by-row instead
- Why vector embeddings alone are unreliable for exact-match lookups (like IDs), and how to route between exact match and vector search
- Debugging RAG systematically — checking retrieved context first to separate retrieval failures from generation failures

## Roadmap

- [x] Terminal-based PDF chatbot
- [x] Streamlit UI
- [x] RAG with ChromaDB + hybrid retrieval
- [ ] Agents (next)
