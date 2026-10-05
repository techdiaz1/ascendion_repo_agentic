# Tool calling examples 
from langchain_core.tools import tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent)) 

# tool 1 : simple addition 
@tool
def add(a:float,b:float) -> float:
    """
    The function performs addition
    """
    return a+b

# print(add(5,10)) #function call 
print(add.invoke({'a':5,'b':10}))



# tool 2 : web search tool
# search tool using ddgs 

from langchain_community.tools import DuckDuckGoSearchRun,DuckDuckGoSearchResults
#initialize the web search 
# web_search = DuckDuckGoSearchRun()
#invoke the tool 
# response = web_search.invoke("Latest developments in agentic ai 2026")
# print(response)
print()
print()

# for multiple search results 
web_search_tool = DuckDuckGoSearchResults(max_results=3,output_format='list') 
# response = web_search_tool.invoke("Latest developments in agentic ai 2026")
# print(response)




#importing and loading the llm 
# from deepseek_llm import create_llm
# llm = create_llm()
# Binding tool with LLM 
# llm_with_tools = llm.bind_tools([web_search])

# response = llm_with_tools.invoke("Search the web and tell me today's weather in bangalore")

# print(response)




from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage
from langchain.tools import tool 
from langchain.agents import create_agent
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from deepseek_llm import create_llm

# tool 3 : Date time tool 

@tool 
def get_current_datetime() -> str:
    """ Get the current date and time in India (IST)"""
    current_time = datetime.now(ZoneInfo("Asia/Kolkata"))

    return current_time.strftime("%A %d %b %Y %H:%M:%S %Z")

#### CREATE THE AGENT #####

llm = create_llm()
agent = create_agent(
    model = llm,
    tools = [get_current_datetime,web_search_tool],
    system_prompt="""
    You are a helpful assistant. 
    You have access to these tools 
    
    1. date and time tool.
    Use the date/time tool whenever the user asks:
    -today's date
    -current date
    -current time 
    -today's day 
    - the current date and time

    Do not guess the current date or time.

    2. web search tool 
    use it when the user asks for any recent information,news,
    weather or anything that needs a websearch

    always use the appropriate tool when necessary. 
    Do not invent current information 
"""
)


response = agent.invoke({
   "messages" : [
       {
           "role":"user",
           "content":"""
            Tell me the current date and time in Bangalore,
            and also search the web for the latest developments
            in agentic AI.
            """
       }
   ]
})
print("\nFINAL ANSWER")
print(response["messages"][-1].content)
