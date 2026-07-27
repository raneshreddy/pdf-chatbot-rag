import streamlit as st
import chromadb
import pdfplumber
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- Setup ----------
st.set_page_config(page_title="Marksheet RAG", page_icon="📄")

@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

client = get_groq_client()

# Chroma client + collection kept in session_state so a re-upload
# rebuilds the collection instead of stacking old + new data together
if "chroma_client" not in st.session_state:
    st.session_state.chroma_client = chromadb.Client()
if "collection" not in st.session_state:
    st.session_state.collection = None
if "messages" not in st.session_state:
    st.session_state.messages = []

COLUMNS = [
    "Sno", "StudentID", "Section",
    "Comp1", "Comp2", "Comp3", "Comp4",
    "Attendance", "Total70", "Percentage",
    "ComprePartA", "ComprePartB", "CompreTotal", "FinalTotal"
]

# ---------- Core RAG functions ----------
def load_pdf_tables(file_obj):
    rows_as_text = []
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or not row[1] or "PS" not in str(row[1]):
                        continue
                    row_str = " | ".join(
                        f"{col}: {val}" for col, val in zip(COLUMNS, row) if val
                    )
                    rows_as_text.append(row_str)
    return rows_as_text

def build_collection(chunks):
    # Fresh collection each upload — avoids old PDF's data leaking into new queries
    try:
        st.session_state.chroma_client.delete_collection(name="pdf_docs")
    except Exception:
        pass
    collection = st.session_state.chroma_client.create_collection(name="pdf_docs")
    collection.add(
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection

def query_db(question, collection, n=3):
    id_match = re.search(r'20\d{2}A[A-Z0-9]PS\d{4}U', question.upper())
    if id_match:
        student_id = id_match.group()
        all_docs = collection.get()["documents"]
        exact_matches = [doc for doc in all_docs if student_id in doc]
        if exact_matches:
            return exact_matches, True  # True = exact match used

    results = collection.query(query_texts=[question], n_results=n)
    return results["documents"][0], False

def ask(question, collection):
    relevant_chunks, was_exact = query_db(question, collection)
    context = "\n".join(relevant_chunks)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": (
                "Answer ONLY using the context below. If the answer is not "
                "explicitly present in the context, say 'I don't have that "
                "information' — do not guess, estimate, or infer a number.\n\n"
                f"Context:\n{context}"
            )},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content, context, was_exact

# ---------- UI ----------
st.title("📄 Marksheet RAG Chatbot")
st.caption("Upload a marksheet PDF, then ask questions about it.")

with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file is not None:
        if st.button("Process PDF", type="primary"):
            with st.spinner("Extracting tables and building index..."):
                chunks = load_pdf_tables(uploaded_file)
                if not chunks:
                    st.error("No student rows found. Check the PDF has a real table structure.")
                else:
                    st.session_state.collection = build_collection(chunks)
                    st.session_state.messages = []  # reset chat on new PDF
                    st.success(f"Loaded {len(chunks)} rows. Ready to query.")

    show_context = st.checkbox("Show retrieved context (debug)", value=False)

# ---------- Chat ----------
if st.session_state.collection is None:
    st.info("Upload and process a PDF from the sidebar to get started.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and show_context and "context" in msg:
                with st.expander("Retrieved context"):
                    st.text(msg["context"])
                    st.caption("Exact ID match used" if msg.get("was_exact") else "Vector search used")

    question = st.chat_input("Ask about the marksheet...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, context, was_exact = ask(question, st.session_state.collection)
                st.write(answer)
                if show_context:
                    with st.expander("Retrieved context"):
                        st.text(context)
                        st.caption("Exact ID match used" if was_exact else "Vector search used")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "context": context,
            "was_exact": was_exact
        })