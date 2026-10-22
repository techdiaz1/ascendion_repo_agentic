import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from langchain_openrouter import ChatOpenRouter
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from azure.identity import DeviceCodeCredential
from langchain_azure_ai.callbacks.tracers import AzureAIOpenTelemetryTracer

async def main(user_query: str):                                                             
    # 1. Configure the LLM: DeepSeek via OpenRouter
    llm = ChatOpenRouter(                          
        model="deepseek/deepseek-v4.1-flash",      
        api_key=os.getenv("OPENROUTER_API_KEY"),   
        temperature=0,                             
        max_tokens=5000,                           
    )    
    # 2. Authenticate with Microsoft Foundry for tracing
    credential = DeviceCodeCredential()

    # 3. Configure Azure opentelemetry tracing and create the tracer 
    tracer = AzureAIOpenTelemetryTracer(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        credential=credential,
        name="github-mcp-tracer",
        agent_id="github-mcp-agent-1",
        trace_all_langgraph_nodes=True
    )
    # 4. Connect to GitHub's remote MCP server               
    client = MultiServerMCPClient(                           
        {                                                    
            "github": {                                      
                "transport": "streamable_http",              
                "url": "https://api.githubcopilot.com/mcp/", 
                "headers": {                                 
                    "Authorization": (                       
                        f"Bearer {os.getenv('GITHUB_TOKEN')}"
                    )                                        
                },                                           
            },

        }                                                    
    )  

    #5. Discover and list the MCP tools 
    
    tools = await client.get_tools()                        
    print("Available Github tools :")                                                                             
    for tool in tools:                                      
        print(f"{tool.name} : {tool.description}")          

    # 6. Create a basic agent                               
    agent = create_agent(                                   
        model = llm,                                        
        tools = tools,                                      
        system_prompt=(                                     
            "You are a Github assistant."                   
            "Use Github tools to answer questions about repositories and source code"
            "Do not make changes to repositories unless user explicitly requests that action"
        )                                                   
    )                    

    # 7. Ask a question                                     
    result = await agent.ainvoke(                           
        {                                                   
            "messages":[                                    
                {                                           
                    "role":"user","content": user_query     
                }                                           
            ]                                               
        }, 
        config = {
            "callbacks" : [tracer],
            "run_name" : "github-run1",
            "tags":["github-mcp","openrouter","azure-Otel"],
            "metadata" : {
                "agent_id" : "github-mcp-agent-1",
                "model":"deepseek/deepseek-v4.1-flash"
            }
        }                                                  
    )

    # 8. Print final answer 
    print("Github Agent response : \n")                                                       
    result["messages"][-1].pretty_print()          

    if __name__ == "__main__":      
        user_query = input("Enter your Github question : ")     
        if user_query:                                          
            asyncio.run(main(user_query))                       
        else:                                                   
            print("No question asked")                          
