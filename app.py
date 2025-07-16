import streamlit as st
import fitz  # PyMuPDF
import docx2txt
import openai
import os

# Nhập API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("📄 AI File Processor")
st.write("Upload PDF hoặc DOCX và nhập yêu cầu xử lý")

uploaded_file = st.file_uploader("Chọn file PDF hoặc DOCX", type=["pdf", "docx"])
user_prompt = st.text_area("Nhập yêu cầu (ví dụ: tóm tắt, liệt kê ý chính...)")

if st.button("Xử lý") and uploaded_file and user_prompt:
    ext = uploaded_file.name.split('.')[-1]
    text = ""

    if ext == "pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    elif ext == "docx":
        with open("temp.docx", "wb") as f:
            f.write(uploaded_file.read())
        text = docx2txt.process("temp.docx")
    else:
        st.error("Chỉ hỗ trợ PDF và DOCX.")
        st.stop()

    full_prompt = f"Văn bản:\n{text}\n\nYêu cầu xử lý:\n{user_prompt}"
    with st.spinner("Đang xử lý với GPT-4..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}]
        )
        result = response["choices"][0]["message"]["content"]

    st.subheader("✅ Kết quả:")
    st.write(result)
