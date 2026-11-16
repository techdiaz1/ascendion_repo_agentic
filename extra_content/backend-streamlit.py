import streamlit as st
import requests

# ------------------------
# CONFIG
# ------------------------

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RAG Assistant",
    layout="centered"
)

# ------------------------
# CUSTOM CSS
# ------------------------

st.markdown("""
<style>

.stApp {
    background-color: #f7f8fc;
}

.main-title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #333366;
}

.subtitle {
    text-align: center;
    color: gray;
    font-size: 16px;
}

.stButton button {
    background-color: #5146e5;
    color: white;
    border-radius: 8px;
    border: none;
    width: 100%;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


# ------------------------
# HEADER
# ------------------------

st.markdown(
    '<div class="main-title">RAG Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Upload documents and ask questions</div>',
    unsafe_allow_html=True
)

st.divider()


# ------------------------
# SESSION STATE
# ------------------------

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ------------------------
# DOCUMENT UPLOAD
# ------------------------

st.subheader("Upload Documents")

files = st.file_uploader(
    "Choose PDF, TXT or DOCX files",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True
)

if st.button("Process Documents"):

    if not files:
        st.warning("Please upload documents first.")

    else:

        try:

            file_data = [
                (
                    "files",
                    (file.name, file.getvalue(), file.type)
                )
                for file in files
            ]

            with st.spinner("Processing documents..."):

                response = requests.post(
                    f"{API_URL}/upload",
                    files=file_data,
                    timeout=300
                )

            if response.status_code == 200:

                result = response.json()

                st.session_state.uploaded = True

                st.success("Documents indexed successfully!")

                st.write(
                    f"Files: {result['files_uploaded']}"
                )

                st.write(
                    f"Chunks: {result['chunks_created']}"
                )

            else:

                st.error(response.text)

        except requests.RequestException as e:

            st.error(f"API connection error: {e}")


st.divider()


# ------------------------
# QUESTION ANSWERING
# ------------------------

st.subheader("Ask Questions")

question = st.text_input(
    "Enter your question",
    placeholder="What is this document about?"
)

if st.button("Ask Question"):

    if not st.session_state.uploaded:

        st.warning("Please process documents first.")

    elif not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner("Finding your answer..."):

                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=120
                )

            if response.status_code == 200:

                result = response.json()

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": result["answer"],
                    "chunks": result["retrieved_chunks"]
                })

            else:

                st.error(response.text)

        except requests.RequestException as e:

            st.error(f"API connection error: {e}")


# ------------------------
# DISPLAY CHAT HISTORY
# ------------------------

for chat in reversed(st.session_state.chat_history):

    with st.chat_message("user"):
        st.write(chat["question"])

    with st.chat_message("assistant"):

        st.write(chat["answer"])

        with st.expander("View Retrieved Chunks"):

            for chunk in chat["chunks"]:

                st.markdown(
                    f"### Chunk {chunk['chunk']}"
                )

                st.write(chunk["content"])

                st.divider()


# ------------------------
# CLEAR CHAT
# ------------------------

if st.button("Clear Chat"):

    st.session_state.chat_history = []

    st.rerun()
