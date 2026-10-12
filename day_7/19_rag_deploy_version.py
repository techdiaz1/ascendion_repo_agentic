import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVectorStore, Column
from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter

load_dotenv()

# --------------------------------------------------
# STEP 1: CONFIGURATION
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL2")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

TABLE_NAME = "nds_documents"
PDF_DIRECTORY = "pdfs"

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL2 is missing from .env")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is missing from .env")

# --------------------------------------------------
# STEP 2: INITIALIZE EMBEDDINGS AND LLM
# --------------------------------------------------

# This model generates 768-dimensional embeddings.
embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)

VECTOR_SIZE = len(embeddings.embed_query("dimension test"))

llm = ChatOpenRouter(
    model="deepseek/deepseek-v4.1-flash",
    api_key=OPENROUTER_API_KEY,
    temperature=0.1,
    max_tokens=1500,
)

prompt = ChatPromptTemplate.from_template(
    """
You are a helpful IT support assistant.

Answer the question using only the context below.
If the context does not contain the answer, say that
you could not find the answer in the provided documents.

Question:
{question}

Context:
{context}
"""
)

chain = prompt | llm

# --------------------------------------------------
# STEP 3: DATABASE LIFECYCLE
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create one async SQLAlchemy engine.
    sql_engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    try:
        # Enable pgvector using an async connection.
        async with sql_engine.begin() as conn:
            await conn.execute(
                text("CREATE EXTENSION IF NOT EXISTS vector")
            )

        print("pgvector extension enabled")

        # Give the same async engine to PGEngine.
        pg_engine = PGEngine.from_engine(
            engine=sql_engine
        )

        # Create the vector table if it does not exist.
        # Do not overwrite existing data.
        await pg_engine.ainit_vectorstore_table(
            table_name=TABLE_NAME,
            vector_size=VECTOR_SIZE,
            metadata_columns=[
                Column("source", "TEXT"),
                Column("page", "INTEGER"),
                Column("chunk_id", "INTEGER"),
            ],
            overwrite_existing=True,
        )

        # Create the async-compatible vector store.
        vector_store = await PGVectorStore.create(
            engine=pg_engine,
            table_name=TABLE_NAME,
            embedding_service=embeddings,
            metadata_columns=["source", "page", "chunk_id"],
            k=3,
            fetch_k=7,
            lambda_mult=0.5,
        )

        # Store reusable resources on the FastAPI app.
        app.state.pg_engine = pg_engine
        app.state.vector_store = vector_store

        print("Database and vector store ready")

        yield

    finally:
        await sql_engine.dispose()
        print("Database connection pool closed")


app = FastAPI(
    title="IT Support RAG API",
    description="PDF retrieval with async PostgreSQL and pgvector",
    lifespan=lifespan,
)

# --------------------------------------------------
# STEP 4: REQUEST SCHEMAS
# --------------------------------------------------

class AskRequest(BaseModel):
    question: str


class IngestResponse(BaseModel):
    pages_loaded: int
    chunks_created: int
    chunks_inserted: int


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]


# --------------------------------------------------
# STEP 5: LOAD AND SPLIT PDF DOCUMENTS
# --------------------------------------------------

def load_and_split_pdfs():
    pdf_path = Path(PDF_DIRECTORY)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF directory not found: {pdf_path.resolve()}"
        )

    loader = DirectoryLoader(
        path=str(pdf_path),
        glob="**/*.pdf",
        loader_cls=PyMuPDFLoader,
        show_progress=True,
    )

    docs = loader.load()

    if not docs:
        raise ValueError("No PDF pages were loaded")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(docs)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return len(docs), chunks


# --------------------------------------------------
# STEP 6: INGEST ENDPOINT
# --------------------------------------------------

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents():
    try:
        # PDF reading and splitting are synchronous.
        # Run them in a worker thread to avoid blocking
        # FastAPI's event loop.
        from starlette.concurrency import run_in_threadpool

        pages_loaded, chunks = await run_in_threadpool(
            load_and_split_pdfs
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks found in PDFs",
            )

        # Async insertion into PostgreSQL / pgvector.
        await app.state.vector_store.aadd_documents(chunks)

        print(f"Loaded pages: {pages_loaded}")
        print(f"Created chunks: {len(chunks)}")

        return IngestResponse(
            pages_loaded=pages_loaded,
            chunks_created=len(chunks),
            chunks_inserted=len(chunks),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        ) from e


# --------------------------------------------------
# STEP 7: ASYNC MMR RETRIEVAL
# --------------------------------------------------

async def retrieve_documents(question: str):
    vector_store = app.state.vector_store

    # Async database search using MMR.
    documents = await vector_store.amax_marginal_relevance_search(
        question,
        k=3,
        fetch_k=7,
        lambda_mult=0.5,
    )

    return documents


# --------------------------------------------------
# STEP 8: ASYNC OPENROUTER RERANKING
# --------------------------------------------------

async def rerank_documents(question: str, documents: list):
    if not documents:
        return []

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/rerank",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "voyageai/rerank-3-lite",
                "query": question,
                "documents": [
                    doc.page_content for doc in documents
                ],
                "top_n": min(3, len(documents)),
            },
        )

        response.raise_for_status()
        data = response.json()

    # The returned indexes refer to the retrieved documents,
    # NOT the original PDF pages.
    ranked = data.get("results", [])

    return [
        documents[item["index"]]
        for item in ranked
        if 0 <= item.get("index", -1) < len(documents)
    ]


# --------------------------------------------------
# STEP 9: ASYNC QUESTION-ANSWER ENDPOINT
# --------------------------------------------------

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    try:
        # 1. Retrieve relevant chunks from pgvector.
        retrieved_docs = await retrieve_documents(question)

        if not retrieved_docs:
            return AskResponse(
                question=question,
                answer="No relevant documents were found.",
                sources=[],
            )

        # 2. Rerank retrieved chunks.
        try:
            final_docs = await rerank_documents(
                question,
                retrieved_docs,
            )
        except (httpx.HTTPError, ValueError, KeyError):
            # Continue with retrieval results if the reranking
            # service fails or returns an unexpected response.
            final_docs = retrieved_docs

        if not final_docs:
            final_docs = retrieved_docs

        # 3. Build the final context.
        context = "\n\n".join(
            doc.page_content for doc in final_docs
        )

        # 4. Invoke the LLM asynchronously.
        response = await chain.ainvoke(
            {
                "question": question,
                "context": context,
            }
        )

        # 5. Return the answer and source metadata.
        sources = [
            {
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page"),
                "chunk_id": doc.metadata.get("chunk_id"),
            }
            for doc in final_docs
        ]

        return AskResponse(
            question=question,
            answer=str(response.content),
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}",
        ) from e


# --------------------------------------------------
# STEP 10: HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok"}
