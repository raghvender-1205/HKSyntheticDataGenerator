import streamlit as st
import os
import tempfile
from dotenv import load_dotenv, find_dotenv
from hk_synthetic_generator.data_generator import HKSyntheticDataGenerator
from hk_synthetic_generator.models import GenerationParams

load_dotenv(find_dotenv())

if 'generator' not in st.session_state:
    st.session_state['generator'] = HKSyntheticDataGenerator()

def create_qa_interface():
    st.set_page_config(page_title="HK Synthetic Data Generator", layout="wide")

    # Let the user choose the data source: upload file(s) or provide a folder path
    data_source = st.radio("Select Data Source", ["Upload PDF File(s)", "Use Existing Folder"])
    left_col, right_col = st.columns([1, 2])

    if data_source == "Upload PDF File(s)":
        with left_col:
            uploaded_files = st.file_uploader("Upload your PDF file(s)", type=["pdf"], accept_multiple_files=True)
        folder_path = None 
    else:  # "Use Existing Folder"
        with left_col:
            folder_path = st.text_input("Enter the folder path containing PDF files")
        uploaded_files = None

    with right_col:
        questions_per_chunk = st.text_input("Number of questions per chunk", value="3")
        use_vectordb = st.checkbox("Index chunks in vectordb?", value=True)

    if st.button("Generate synthetic data"):
        if data_source == "Upload PDF File(s)":
            if not uploaded_files:
                st.error("Please upload at least one PDF file!")
                return

            # Create a temporary directory to save the uploaded file(s).
            # The document loader expects a folder path containing PDFs.
            with tempfile.TemporaryDirectory() as tmpdirname:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(tmpdirname, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.info(f"Files saved to temporary folder: {tmpdirname}")
                params = GenerationParams(
                    folder_path=tmpdirname,
                    questions_per_chunk=int(questions_per_chunk),
                    use_vectordb=use_vectordb
                )
                st.session_state['generator'].generate_data(params)
                st.success("Data generation completed!")
        else:
            if not folder_path:
                st.error("Please provide a valid folder path!")
                return

            # Check if the provided folder path exists
            if not os.path.isdir(folder_path):
                st.error("The provided folder path does not exist.")
                return

            params = GenerationParams(
                folder_path=folder_path,
                questions_per_chunk=int(questions_per_chunk),
                use_vectordb=use_vectordb
            )
            st.session_state['generator'].generate_data(params)
            st.success("Data generation completed!")

if __name__ == "__main__":
    create_qa_interface()
