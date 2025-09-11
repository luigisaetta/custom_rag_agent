"""
Test LLM with MCP server.

We're using tools calling with the old langchain way.
"""

import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from oci_models import get_llm
from mcp_servers_config import MCP_SERVERS_CONFIG
from utils import get_console_logger

logger = get_console_logger()


async def run_agent(user_prompt: str):
    """
    Create the agent calling the MCP server.
    Runs the agent
    """
    # Define your MCP servers
    client = MultiServerMCPClient(MCP_SERVERS_CONFIG)

    # Load tools
    tools = await client.get_tools()

    # Build the agent
    # with old langchain I can only use Cohere
    llm = get_llm(model_id="cohere.command-a-03-2025")

    agent = create_react_agent(llm, tools)

    # Use it.
    # We have several collection in the DB. We specify here which one we want to use (BOOKS).
    system_prompt = """You are an AI assistant equipped with an MCP server and several tools.
    Use the BOOKS collection.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    logger.info("")
    logger.info("Calling agent...")
    logger.info("")

    response = await agent.ainvoke({"messages": messages})

    # we take only the last message (ai response)
    return response["messages"][-1].content


if __name__ == "__main__":
    answer = asyncio.run(
        run_agent("Tell me about Luigi Saetta. Provide me his email address.")
    )

    print("Agent answer:")
    print(answer)
