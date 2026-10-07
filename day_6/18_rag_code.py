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

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 600,chunk_overlap=100
)

chunks = splitter.split_documents(docs)

# print(chunks[3].page_content)

print(f"Loaded pages: {len(docs)}")
print(f"Created chunks: {len(chunks)}")  


# step 3 : Create vector embeddings using huggingface 

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# test the embeddings model - this model should show 384 embedding dimensions 
# all-MiniLM-L6-v2 is a lightweight, general-purpose embedding model 
# that converts sentences and paragraphs into 384-dimensional dense vectors for semantic similarity and search tasks
# Trained on over 1 billion training pairs
# Max Token Limit: handles up to 256 word pieces or tokens    Extremely Lightweight: At only ~90 MB in size
