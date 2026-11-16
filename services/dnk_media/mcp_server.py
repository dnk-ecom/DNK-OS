from mcp.server.fastmcp import FastMCP
from services.dnk_media.src.service import process_data

mcp = FastMCP("dnk_media")

@mcp.tool()
def execute(query: str) -> str:
    return process_data(query)

if __name__ == "__main__":
    mcp.run()
