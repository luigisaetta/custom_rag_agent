"""
Test Semantic Search...
"""

import asyncio
import json
from fastmcp import Client
from oci_jwt_client import OCIJWTClient
from utils import get_console_logger
from config import IAM_BASE_URL, ENABLE_JWT_TOKEN, PORT

logger = get_console_logger()

# this is the endpoint of the MCP server
ENDPOINT = f"http://localhost:{PORT}/mcp/"


# The MCP Client uses StreamableHttpTransport for HTTP URLs
async def main():
    """
    Main function to demonstrate the Semantic Search tool.
    """
    # this is the scope for which the token is issued
    scope = "urn:opc:idm:__myscopes__"
    # these are used in verification
    # these is depending from the tenant
    # the ocid of the secret in the vault
    secret_ocid = "ocid1.vaultsecret.oc1.eu-frankfurt-1.amaaaaaa2xxap7yalre4qru4asevgtxlmn7hwh27awnzmdcrnmsfqu7cia7a"

    # create the JWT token
    # can pass a user here
    if ENABLE_JWT_TOKEN:
        # this is a client to OCI IAM to get the JWT token
        print("")
        print("--- Using JWT based auth ---")
        print("")

        print("Getting JWT token...")
        print("")

        client_4_token = OCIJWTClient(IAM_BASE_URL, scope, secret_ocid)

        token, _, _ = client_4_token.get_token()

        # this is the client to invoke MCP server
        client = Client(ENDPOINT, auth=token)
    else:
        token = ""
        client = Client(ENDPOINT)

    async with client:
        # get the list of available tools
        tools = await client.list_tools()

        print("")
        print("---MCP Available tools:")
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

        results = await client.call_tool(
            "get_collections",
        )

        print("List Collections Results:")
        for result in results:
            print("Collection name: ", result.text)
        print()


asyncio.run(main())
