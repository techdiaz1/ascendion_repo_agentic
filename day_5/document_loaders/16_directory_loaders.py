from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader
# loader = DirectoryLoader(
    # path='codes',        
    # glob='/*.pdf', # load pdf from codes folder only 
    # loader_cls=PyPDFLoader
# )


loader = DirectoryLoader(
    path='',        
    glob='**/*.pdf', # load all the pdf files from day_5 and codes folder
    loader_cls=PyPDFLoader
)

docs = loader.lazy_load()
# 
print(len(docs))
print(docs)
# 
for doc in docs:
    print(doc.page_content)


