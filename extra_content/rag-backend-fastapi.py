import os
import tempfile
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_groq import ChatGroq

from langchain_community.vectorstores import FAISS


# ------------------------
# ENVIRONMENT VARIABLES
# ------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GOOGLE_API_KEY or not GROQ_API_KEY:
    raise RuntimeError("API keys are missing from .env")


# ------------------------
# FASTAPI APP
# ------------------------

app = FastAPI(
    title="RAG Assistant API",
    description="Document-based Question Answering API",
    version="1.0"
)


# ------------------------
# GLOBAL VARIABLES
# ------------------------

vectorstore = None


# ------------------------
# EMBEDDINGS
# ------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)


# ------------------------
# LLM
# ------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=GROQ_API_KEY
)


# ------------------------
# REQUEST MODEL
# ------------------------

class QuestionRequest(BaseModel):
    question: str


# ------------------------
# HOME ROUTE
# ------------------------

@app.get("/")
def home():

    return {
        "message": "RAG Assistant API is running"
    }


# ------------------------
# DOCUMENT UPLOAD
# ------------------------

@app.post("/upload")
async def upload_documents(
    files: list[UploadFile] = File(...)
):

    global vectorstore

    documents = []

    allowed_extensions = ["pdf", "txt", "docx"]

    try:

        for file in files:

            extension = file.filename.split(".")[-1].lower()

            if extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file: {file.filename}"
                )

            suffix = "." + extension

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as tmp:

                shutil.copyfileobj(file.file, tmp)

                tmp_path = tmp.name

            try:

                if extension == "pdf":

                    loader = PyPDFLoader(tmp_path)

                elif extension == "txt":

                    loader = TextLoader(
                        tmp_path,
                        encoding="utf-8"
                    )

                elif extension == "docx":

                    loader = Docx2txtLoader(tmp_path)

                documents.extend(loader.load())

            finally:

                os.remove(tmp_path)

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No readable documents found"
            )

        # ------------------------
        # TEXT SPLITTING
        # ------------------------

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks generated"
            )

        # ------------------------
        # CREATE FAISS VECTORSTORE
        # ------------------------

        vectorstore = FAISS.from_documents(
            chunks,
            embeddings
        )

        return {
            "message": "Documents indexed successfully",
            "files_uploaded": len(files),
            "documents_loaded": len(documents),
            "chunks_created": len(chunks)
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ------------------------
# QUESTION ANSWERING
# ------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    global vectorstore

    if vectorstore is None:

        raise HTTPException(
            status_code=400,
            detail="Please upload and process documents first"
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:

        # ------------------------
        # RETRIEVER
        # ------------------------

        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

        docs = retriever.invoke(question)

        if not docs:
            return {
                "question": question,
                "answer": "I could not find this information in the uploaded documents.",
                "retrieved_chunks": []
            }

        # ------------------------
        # CONTEXT
        # ------------------------

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        # ------------------------
        # PROMPT
        # ------------------------

        prompt = f"""
You are a document assistant.

Answer ONLY using the provided context.

If the answer is not available,
say "I could not find this information in the uploaded documents."

Do not use outside knowledge.

Context:
{context}

Question:
{question}

Answer:
"""

        # ------------------------
        # LLM RESPONSE
        # ------------------------

        response = llm.invoke(prompt)

        # ------------------------
        # RETURN RESPONSE
        # ------------------------

        retrieved_chunks = []

        for i, doc in enumerate(docs, 1):

            retrieved_chunks.append({

                "chunk": i,

                "content": doc.page_content[:1000],

                "metadata": doc.metadata

            })

        return {

            "question": question,

            "answer": response.content,

            "retrieved_chunks": retrieved_chunks

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ------------------------
# SERVER STATUS
# ------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "documents_indexed": vectorstore is not None
    }
