import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Upload Knowledge")

st.title("📚 Upload Knowledge to Virtus")

uploaded_file = st.file_uploader(
    "Upload a document",
    type=["txt", "pdf"]
)

if uploaded_file is not None:

    st.write(f"Selected: {uploaded_file.name}")

    if st.button("Process Document"):

        with st.spinner("Processing document..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    uploaded_file.type
                )
            }

            res = requests.post(
                f"{API_URL}/virtus/upload",
                files=files
            )

            if res.status_code == 200:
                data = res.json()

                st.success("Document processed successfully")
                st.write(f"Chunks created: {data['chunks']}")

            else:
                st.error(res.text)