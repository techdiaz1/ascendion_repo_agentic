#MCP client 
# MCP server --> Tools --> # API (inside tools)
import os
import asyncio
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
# configure Python to use a trusted CA certificate bundle when making HTTPS connections from your MCP client.
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# SSL_CERT_FILE	Tells TLS/SSL libraries that honor this variable where to find the CA certificate bundle.
# REQUESTS_CA_BUNDLE	Tells the Python requests library which CA bundle to use to verify HTTPS server certificates.
# certifi.where() returns the filesystem path to the CA certificate bundle provided by the certifi Python package.
# These help Python verify the identity of remote servers and establish secure TLS connections.

load_dotenv() 

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
client = MultiServerMCPClient(
    {
        "tavily" : {
            "transport" : "streamable_http",
            "url" : f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        }
    }
)

async def get_all_tools():
    tools = await client.get_tools()
    print("Available MCP Tools : \n")
    for tool in tools:
        print(tool.name)

# this returns the tavily_search tool object 


tavily_search_tool = None
async def get_tavily_search_tool():
    global tavily_search_tool
    if tavily_search_tool is not None:
        return 
    tools = await client.get_tools() 
    print("Available MCP Tools : \n")
    for tool in tools:               
        print(tool.name)
    tavily_search_tool = next(tool for tool in tools if tool.name == "tavily_search")
# the built-in next() function is used to manually retrieve the next item from a generator object or any iterator

# function to call the tavily_search_tool with a query 
async def tavily_mcp_search(query:str):
    await get_tavily_search_tool()
    result = await tavily_search_tool.ainvoke(   # async invoke on the tool object tavily_search_tool)
        {
            "query":query
        }
    )
    print(result)

if __name__ == "__main__":                        
#    asyncio.run(get_all_tools()) #list all tools
   query = "latest news in ai"
   asyncio.run(tavily_mcp_search(query))
