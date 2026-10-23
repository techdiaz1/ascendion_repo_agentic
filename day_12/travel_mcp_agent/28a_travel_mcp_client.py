import os                                                                                                     
import asyncio                                                                                                
import certifi                                                                                                
from dotenv import load_dotenv                                                                                
from langchain_mcp_adapters.client import MultiServerMCPClient 
from langchain_openrouter import ChatOpenRouter                                               
os.environ["SSL_CERT_FILE"] = certifi.where()                                                                 
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()    
from pathlib import Path   
import sys                                                       
load_dotenv()                                                                                                 

# Automatically find the current project folder to replace hard coded windows path to fetch the custom mcp server file                                                                                                               
PROJECT_DIR = Path(__file__).resolve().parent
WEATHER_SERVER_PATH = PROJECT_DIR / "custom_weather_mcp_server.py"

# Define keys                                                                                                               
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")    
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")             
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")         
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
                                                                                                              
#call the llm 
llm = ChatOpenRouter(model = "deepseek/deepseek-v4.1-flash",api_key=os.getenv("OPENROUTER_API_KEY"),
temperature=0.1,max_tokens=5000)

# MCP client configurations (1. Tavily remote server, 2. Aviationstack local server, 3. Openweathermap custom server)                                                                  
client = MultiServerMCPClient(                                                                                
    {                                                                                                         
        "tavily" : {                                                                                          
            "transport" : "streamable_http",                                                                  
            "url" : f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"                              
        },  

        "aviationstack" : {
        "transport" : "stdio",
        "command" : "uvx",
        "args" : ["aviationstack-mcp"],
        "env" : {"AVIATIONSTACK_API_KEY" : AVIATIONSTACK_API_KEY}
        },

        "weather" : {
        "transport" : "stdio",
        "command" : sys.executable, #use the same env as your other files for execution
        "args" : [str(WEATHER_SERVER_PATH)],
        "env" : {"OPENWEATHER_API_KEY" : OPENWEATHER_API_KEY} # fetch the custom_weather file from the current project directory 
        }
    }
)       

# 
async def get_all_tools():
    """ 
    Load each MCP server separately. 
    so that broken server doesn't stop the other servers from loading
    """

    all_tools = []

    for server_name in ["tavily","aviationstack","weather"]:
        try:
            tools = await client.get_tools(server_name=server_name)
            all_tools.extend(tools)

            print(f"Available tools from {server_name} MCP : \n")
            for tool in tools:
                print(f"Tool name : {tool.name} ")   
        except Exception as error:
            print(f"Could not connect to {server_name} MCP") 

    return all_tools 

####### TAVILY MCP TOOlS ##########

#list only tavily tools
tavily_search_tool = None                                                            
async def get_tavily_search_tool():                                                  
    global tavily_search_tool                                                        
    if tavily_search_tool is not None:                                               
        return                                                                       
    tools = await client.get_tools(server_name="tavily")                                                 
    print("Available Tavily MCP Tools : \n")                                                
    for tool in tools:                                                               
        print(tool.name)                                                             
    tavily_search_tool = next(tool for tool in tools if tool.name == "tavily_search")


async def tavily_mcp_search(query:str):
    await get_tavily_search_tool()

    result = await tavily_search_tool.ainvoke(
        {
            "query" : query
        }
    )
    print(result)

###### AVIATION STACK MCP TOOLS ########


#list only aviationstack tools 
aviation_tools = {}
async def init_aviation_tools():                                                   
    global aviation_tools           
    if aviation_tools:
        return                                                                                                                                    
    tools = await client.get_tools(server_name="aviationstack")
    aviation_tools = {tool.name : tool for tool in tools}                              
    print("Available aviation MCP Tools : \n")                                                 
    for tool_name in aviation_tools:                                                                
        print(tool_name)                                                              
                                                                                      
async def aviation_mcp_call(tool_name : str,tool_args : dict | None = None):
    await init_aviation_tools()

    tool = aviation_tools.get(tool_name)
    result = await tool.ainvoke(tool_args or {})
    print(result)



###### WEATHER MCP TOOLS ########


if __name__ == "__main__":
    # query = "what is agentic ai in brief?"
    # asyncio.run(tavily_mcp_search(query))   
    # asyncio.run(get_tavily_search_tool())    
    # asyncio.run(init_aviation_tools())   
    asyncio.run(aviation_mcp_call("get_flight_status",{"flight_number":"SG649"}))

