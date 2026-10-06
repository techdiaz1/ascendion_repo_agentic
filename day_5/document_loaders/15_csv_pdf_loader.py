# from langchain_community.document_loaders import CSVLoader
# 
# loader = CSVLoader('Salary.csv')
# 
# docs = loader.load() # Each document represents one row of the CSV file
# 
# print(docs[1])
# print(len(docs))
# 
# for doc in docs:
    # print(doc)      #print all rows from the csv


# Pdf loader

from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('C_Programs_11_to_15.pdf')

docs = loader.load()

# print(docs[0].page_content)
# print(docs[0].metadata)

for doc in docs:
    print(doc.page_content) # print entire pdf 

