import os
import asyncio

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main():
    # 1. Configure the LLM
    llm = ChatOpenRouter(
        model="deepseek/deepseek-v4.1-flash",
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0,
    )

    # 2. Connect to GitHub's remote MCP server
    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {
                    "Authorization": (
                        f"Bearer {os.environ['GITHUB_TOKEN']}"
                    )
                },
            }
        }
    )

    # 3. Discover GitHub tools
    tools = await client.get_tools()

    print("Available GitHub tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    # 4. Create the agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a GitHub assistant. "
            "Use GitHub tools to answer questions about repositories. "
            "Do not make changes to repositories unless explicitly asked."
        ),
    )

    # 5. Ask a question
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "List the repositories I can access "
                        "and explain what each one contains."
                    ),
                }
            ]
        }
    )

    result["messages"][-1].pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
