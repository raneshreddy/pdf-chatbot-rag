import streamlit as st
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("PDF Chatbot")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if "messages" not in st.session_state:
    st.session_state.messages = []

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()

    system_prompt = f"""You are a helpful assistant. 
Answer questions based on this document only:

{pdf_text}

If the answer is not in the document, say so."""

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask about your PDF..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ]
        )

        ai_reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        with st.chat_message("assistant"):
            st.write(ai_reply)
else:
    st.info("Upload a PDF to get started")