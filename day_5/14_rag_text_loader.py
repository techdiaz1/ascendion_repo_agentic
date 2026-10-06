from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openrouter import ChatOpenRouter
import os 
from dotenv import load_dotenv

load_dotenv()

loader = TextLoader('demo.txt',encoding='utf-8')

docs = loader.load() # (load into langchain base document format)

# print(type(docs[0]))  #prints type of the document 

# print(docs[0].page_content)      # prints the content 
# print(len(docs[0].page_content)) # prints the no. of characters in the content

print(docs[0].metadata)

prompt = PromptTemplate(template="write a summary for the following text data \n {demo}",input_variables=['demo'])

llm = ChatOpenRouter(model = "deepseek/deepseek-v4.1-flash",api_key=os.getenv("OPENROUTER_API_KEY"),
                    temperature=0.1,max_tokens=5000)

parser = StrOutputParser() 

chain = prompt | llm | parser # using LCEL 

# print(chain.invoke({'demo':docs[0].page_content})) 
# print the summary using the prompt and the content ,
#  follow steps mentioned in the chain 


# LLM latency 

import time 

start_time = time.perf_counter()

result = chain.invoke({'demo':docs[0].page_content})

end_time = time.perf_counter()

latency = end_time - start_time 
print(result)
print(f"Latency : {latency:.3f} seconds")
print(result.usage_metadata)  # works only if we remove parser from the chain 

#Cache read tokens are previously processed input data (like system prompts, conversation history, or code files) that an AI model reuses from a temporary cache instead of processing fresh.

#How Cache Read Tokens Work
#• Reused Context: When you send multiple messages in a session , the system resends the shared prefix context.
#• Discounted Rate: Instead of paying the full standard input price, reading these cached tokens typically costs around 10% of the normal input token rate.



# #LCEL (Langchain Expression Language)
# Why Use LCEL?
# Modular: Build applications by combining reusable components.
# Readable: Simple pipe (|) syntax makes workflows easy to understand.
# Reusable: Components can be reused across multiple applications.
# Flexible: Easily swap prompts, models, or output parsers.
# Production-ready: Supports streaming, async execution, batching, and debugging.


# doing llm calls using LCEL (easier alternative)
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnableLambda
# 
# parser = StrOutputParser()  # StrOutputParser() converts the AI message into plain text.
# 
# chain = (llm | parser | RunnableLambda(lambda response:f"Summarize this response:\n{response}") | llm | parser )
# 
# result = chain.invoke("explain agentic ai for developers")
# print(result)
