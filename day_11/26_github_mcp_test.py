import os 
import asyncio
from dotenv import load_dotenv
load_dotenv()
from langchain_openrouter import ChatOpenRouter
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    # 1. Configure the LLM
    llm = ChatOpenRouter(
        model="deepseek/deepseek-v4.1-flash",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,max_tokens=5000
    )
    #2. Connect to Github remoter MCP server
    client = MultiServerMCPClient(
        {
            "github": {
                "transport":"streamable_http",
                "url":"https://api.githubcopilot.com/mcp/",
                "headers":{
                    "authorization": (f"Bearer {os.getenv('GITHUB_TOKEN')}")
                }
            }
        }
    )
    # 3. Discover Github tools 
    tools = await client.get_tools()

    print("Available Github tools :")
    for tool in tools:
        print(f"{tool.name} : {tool.description}")

    # 4. Create a basic agent 
    agent = create_agent(
        model = llm,
        tools = tools,
        system_prompt=(
            "You are a Github assistant."
            "Use Github tools to answer questions about repositories"
            "Do not make changes to repositories unless explicitly asked"
        )
    )
    # 5. Ask a question 
    result = await agent.ainvoke(
        {
            "messages":[
                {
                    "role":"user",
                    "content": (
                        # "List the most recently created repositories "
                        # " and explain what it contains in brief"
                        "Fetch me the code for day 11 26_github_mcp_test.py from the ascendion repo agentic"
                    )
                }
            ]
        }
    )
    result["messages"][-1].pretty_print()

if __name__ == "__main__":
    asyncio.run(main())
