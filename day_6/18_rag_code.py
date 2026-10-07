from langchain_community.document_loaders import DirectoryLoader,PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os 
load_dotenv()

# step 1 : load documents and ingest data 
loader = DirectoryLoader(
    path='pdfs',        
    glob='**/*.pdf', # load all the pdf files from day_5 and codes folder
    loader_cls=PyMuPDFLoader
)
docs = loader.load()
for doc in docs:
    print(len(doc.page_content)) # returns token count of each page of all pdf files ( 4 files = 17 pages) #29k tokens total

# Step 2 : create chunks for all the documents uploaded 


splitter = RecursiveCharacterTextSplitter(chunk_size = 600,chunk_overlap=100)
chunks = splitter.split_documents(docs)
# print(chunks[3].page_content)
print(f"Loaded pages: {len(docs)}")
print(f"Created chunks: {len(chunks)}")  

# step 3 : Create vector embeddings using huggingface 
embeddings = HuggingFaceEmbeddings(model_name="nomic-ai/nomic-embed-text-v1.5")
vector_size = len(embeddings.embed_query("dimension test"))
print(vector_size)

# info about the chunks 
print(len(chunks[0].page_content))
print(chunks[0].page_content)
print(chunks[0].metadata)

# STEP 4a : connect to a lightweight vectorstore (chroma,FAISS)
# connect with faiss  Faiss can store hold 1 to 5 million small vectors 
# FAISS is an in-memory library, meaning it loads the entire index directly into your system's RAM
# 768 dimensions * 4 bytes = 3072 bytes (~3 KB) per vector (almost 4-5million small vectors)
from langchain_community.vectorstores import FAISS
vector_store_faiss = FAISS.from_documents(chunks,embeddings)
vector_store_faiss

len(vector_store_faiss.index.reconstruct_n(0,vector_store_faiss.index.ntotal))
vector_store_faiss.index.reconstruct_n(0,vector_store_faiss.index.ntotal) # vectors which are stored according to our chunks
# display and confirm that vector embeddings are indeed created


# STEP 4b : test connection to postgre,enable pgvector, create a db/schema setup to initialize,create a vector store
# connect to postgresql 
from sqlalchemy import create_engine,text 
import os 
from dotenv import load_dotenv
engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
print("postgresql connection successful")

# enable pgvector extension 
with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
print("pgvector extension is enabled!")

# extension vector not available, it must first be installed on the system
#  where postgresql is running 
# should copy the files of pgvector into postgre folder then run this cell

# async postgre engine connection required to store pgvectors 
from langchain_postgres import PGEngine 
DATABASE_URL2 = "postgresql+asyncpg://postgres:12345@localhost:5432/demo_db"
pg_engine = PGEngine.from_connection_string(url=DATABASE_URL2)
print("PGEngine created successfully\n",pg_engine)

# we are creating a new column chunk id in the metadata and converting its datatype to int and same for page 

for i,chunk in enumerate(chunks):
    chunk.metadata['chunk_id'] = i

# initialize and create a database/schema to create a pgvector table 
from langchain_postgres import Column 
pg_engine.init_vectorstore_table(
    table_name="nds_documents",
    vector_size=768,
    metadata_columns=[
        Column("source","TEXT"),
        Column("page","INTEGER"),
        Column("chunk_id","INTEGER")
    ],
    overwrite_existing=True
)

# create a vectorstore and create vector embeddings 
# vector store object creation
from langchain_postgres import PGVectorStore
try:
    vector_store = PGVectorStore.create_sync(
        engine=pg_engine,
        table_name="nds_documents",
        embedding_service=embeddings,
        metadata_columns=["source","page","chunk_id"]
    )
    print("vector store created successfully!")
except Exception as e:
    print(f"Vector store not created : {e}")

# update/insert the chunks into the vector store 
vector_store.add_documents(chunks)
print(f"Successfully inserted {len(chunks)} chunks into pgvector")
