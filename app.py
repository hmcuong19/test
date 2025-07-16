import streamlit as st
import tempfile
import os
import requests
import json

from PyPDF2 import PdfReader
import docx2txt

st.set_page_config(page_title="AI File Prompt Processor (Gemini)")
st.title("📄 AI Document Processor with Gemini Pro")
st.markdown("Upload a **.pdf** or **.docx** file, enter a prompt, and process it using Google Gemini API.")

uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=["pdf", "docx"])
user_prompt = st.text_area("Enter your prompt")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    gemini_api_key = st.text_input("Enter your Gemini API key", type="password")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"

if st.button("Process"):
    if not uploaded_file or not user_prompt or not gemini_api_key:
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

    full_prompt = f"Document Content:\n{text}\n\nUser Request:\n{user_prompt}"

    with st.spinner("Processing with Gemini Pro..."):
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }
            response = requests.post(
                f"{GEMINI_API_URL}?key={gemini_api_key}",
                headers=headers,
                data=json.dumps(payload)
            )
            result = response.json()

            if "candidates" in result and result["candidates"]:
                output = result["candidates"][0]["content"]["parts"][0]["text"]
                st.success("✅ Response:")
                st.write(output)
            else:
                st.error("❌ Gemini API did not return a valid response. Check your prompt or API key.")
                st.subheader("Raw API response:")
                st.json(result)

        except Exception as e:
            st.error(f"❌ Error: {e}")
