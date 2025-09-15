"""
Minimal MCP server

This should be the starting point for any MCP server built with Fastmcp
"""

from fastmcp import FastMCP

# to verify the JWT token
# if you don't need to add security, you can remove this
from fastmcp.server.auth import BearerAuthProvider

from config import (
    # first four needed only to manage JWT
    ENABLE_JWT_TOKEN,
    IAM_BASE_URL,
    ISSUER,
    AUDIENCE,
    TRANSPORT,
    # needed only if transport is stremable-http
    HOST,
    PORT,
)

AUTH = None

#
# if you don't need to add security, you can remove this part and set
# AUTH = None, or simply set ENABLE_JWT_TOKEN = False
#
if ENABLE_JWT_TOKEN:
    # check that a valid JWT token is provided
    AUTH = BearerAuthProvider(
        # this is the url to get the public key from IAM
        # the PK is usedd to check the JWT
        jwks_uri=f"{IAM_BASE_URL}/admin/v1/SigningCert/jwk",
        issuer=ISSUER,
        audience=AUDIENCE,
    )

mcp = FastMCP("MCP server with few lines of code", auth=AUTH)


#
# MCP tools definition
# add and write the code for the tools here
#
@mcp.tool
def say_the_truth(user: str) -> str:
    """
    This tool, given the name of the user return one of the secret truths.
    """
    # here you'll put the code that reads and return the info requested
    # mark each tool with the annotation
    return f"{user}: Less is more!"


#
# Run the MCP server
#
if __name__ == "__main__":
    # if you want to use stdio, you don't need host, port
    # config here is for streamable-http.
    # don't use sse! it is deprecated!
    mcp.run(
        transport=TRANSPORT,
        # Bind to all interfaces
        host=HOST,
        port=PORT,
    )
