"""
Test Semantic Search...
"""

import asyncio
import json
from datetime import datetime, timedelta
from fastmcp import Client
import jwt
import config
from config_private import JWT_SECRET, JWT_ALGORITHM

ENDPOINT = f"http://localhost:{config.PORT}/mcp/"

# The Client uses StreamableHttpTransport for HTTP URLs
client = Client(ENDPOINT)


def create_token(user="test-user"):
    """
    create a JWT token
    """
    payload = {
        "sub": user,  # subject (any string identifying the user)
        "exp": datetime.utcnow() + timedelta(hours=1),  # token expires in one hour
    }
    # show how to create a valid JWT token
    _token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return _token


async def main():
    """
    Main function to demonstrate the semantic search tool.
    """
    async with client:
        # getthe list of available tools
        tools = await client.list_tools()

        print("")
        print("---Available tools:")
        print("")
        for tool in tools:
            print(f"Tool: {tool.name} - {tool.description}")
            # print the input schema for the tool
            print("Input Schema:")
            pretty_schema = json.dumps(tool.inputSchema, indent=4, sort_keys=True)
            print(pretty_schema)
            print("")

        print("")
        print("Calling get_collection tool...")
        print("")

        # create the JWT token
        token = create_token()

        results = await client.call_tool(
            "get_collections",
            {"token": token},
        )

        print("List Collections Results:")
        for result in results:
            print("Collection name: ", result.text)
        print()


asyncio.run(main())
