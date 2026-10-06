
# WebBaseLoader 
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openrouter import ChatOpenRouter
import os 
from dotenv import load_dotenv


load_dotenv()


url = 'https://www.flipkart.com/apple-iphone-18-pro-burgundy-256-gb/p/itm2b2c10b01cc46?pid=MOBHQT5JBPDHYHJM&lid=LSTMOBHQT5JBPDHYHJM3ZGIUY&marketplace=FLIPKART&q=iphone+18+pro&store=tyy%2F4io&srno=s_1_1&otracker=AS_QueryStore_OrganicAutoSuggest_2_7_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_2_7_na_na_na&fm=organic&iid=c229de81-0af2-42e0-b461-37456712daa2.MOBHQT5JBPDHYHJM.SEARCH&ppt=dynamic&ppn=Login%3ACategory_List&ssid=qh1jrc55c00000001791272848268&qH=f969d826bf8e013f&ov_redirect=true'
loader = WebBaseLoader(url)

docs = loader.load()
# print(docs)


prompt=PromptTemplate(template='Answer the following question \n {question} ' \
'                           from the following text - \n {text}',
                        input_variables=['question','text']) 

llm = ChatOpenRouter(model = "deepseek/deepseek-v4.1-flash",api_key=os.getenv("OPENROUTER_API_KEY"),
                    temperature=0.1,max_tokens=5000)

parser = StrOutputParser() 

chain = prompt | llm | parser # using LCEL 

print(chain.invoke({'question':'What is the product we are speaking about here?', 'text':docs[0].page_content}))