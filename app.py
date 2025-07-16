import streamlit as st
import openai
import tempfile
import os

from PyPDF2 import PdfReader
import docx2txt

st.set_page_config(page_title="AI File Prompt Processor")
st.title("📄 AI Document Processor with GPT")
st.markdown("Upload a **.pdf** or **.docx** file, enter a prompt, and process it with GPT.")

uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=["pdf", "docx"])
user_prompt = st.text_area("Enter your prompt")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter your OpenAI API key", type="password")

if st.button("Process"):
    if not uploaded_file or not user_prompt or not api_key:
        st.warning("Please provide a file, prompt, and API key.")
        st.stop()

    ext = uploaded_file.name.split('.')[-1].lower()
    text = ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    if ext == "pdf":
        reader = PdfReader(tmp_file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif ext == "docx":
        text = docx2txt.process(tmp_file_path)
    else:
        st.error("Unsupported file type.")
        st.stop()

    client = openai.OpenAI(api_key=api_key)
    full_prompt = f"Document Content:\n{text}\n\nUser Request:\n{user_prompt}"

    with st.spinner("Processing with GPT-4..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": full_prompt}]
            )
            result = response.choices[0].message.content
            st.success("✅ Response:")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")
